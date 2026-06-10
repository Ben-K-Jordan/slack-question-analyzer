"""
LLM prompting layer for the analysis pipeline.

All generation goes through one chat-based core with:
- JSON-schema-enforced output (Ollama `format` schema / OpenAI json_schema)
- temperature 0 and a fixed seed for reproducibility
- keep_alive so Ollama keeps the model loaded across sequential calls
- semantic validation with one corrective retry

Capabilities (all optional — the pipeline works without any of them):
- label_group:        topic name + one-sentence summary per question group
- verify_same_topic:  yes/no check for borderline group merges
- summarize_analysis: executive summary of the whole analysis
- detect_questions:   find help requests the regex extractor missed
- is_answered:        decide whether thread replies resolved a question
"""

import os
import json
import re
import logging
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

from .disk_cache import JsonDiskCache

logger = logging.getLogger(__name__)

MAX_QUESTIONS_IN_PROMPT = 8
MAX_TOPIC_WORDS = 6

# Topics made up entirely of these words are useless and get retried
GENERIC_TOPIC_WORDS = {
    'general', 'misc', 'miscellaneous', 'various', 'questions', 'question',
    'help', 'issues', 'issue', 'stuff', 'other', 'others', 'support',
    'technical', 'assorted', 'random', 'topics', 'topic', 'inquiries', 'asks',
}

LABEL_SCHEMA = {
    'type': 'object',
    'properties': {
        'topic': {'type': 'string'},
        'summary': {'type': 'string'},
    },
    'required': ['topic', 'summary'],
}

VERIFY_SCHEMA = {
    'type': 'object',
    'properties': {'same_topic': {'type': 'boolean'}},
    'required': ['same_topic'],
}

SUMMARY_SCHEMA = {
    'type': 'object',
    'properties': {'summary': {'type': 'string'}},
    'required': ['summary'],
}

DETECT_SCHEMA = {
    'type': 'object',
    'properties': {
        'questions': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'index': {'type': 'integer'},
                    'question': {'type': 'string'},
                },
                'required': ['index', 'question'],
            },
        },
    },
    'required': ['questions'],
}

ANSWERED_SCHEMA = {
    'type': 'object',
    'properties': {'answered': {'type': 'boolean'}},
    'required': ['answered'],
}

LABEL_SYSTEM = (
    "You label groups of similar support questions from a Slack channel.\n"
    "Rules:\n"
    "- The topic must name the SPECIFIC feature, system, or task being asked about.\n"
    "- Never use vague topics like 'General Questions', 'Help', 'Miscellaneous', "
    "'Various Issues', or 'Technical Questions'.\n"
    "- Never use the bare product name alone as the topic — name the specific "
    "capability inside it.\n"
    "- Never start the topic with 'How to' — it is a category name, not a question.\n"
    "- Keep exact product and feature terms from the questions (don't paraphrase "
    "technical names).\n"
    "- Topic: 2-4 words, Title Case. Summary: one sentence describing what people "
    "are asking.\n"
    "- Respond with JSON only."
)

LABEL_FEW_SHOT = """Example:
Questions:
- Copy Task failing with "Exception while scanning for virus" — please advise.
- When a virus is detected, how can we send an email notification to an admin?
Answer: {"topic": "Antivirus Scanning", "summary": "Users ask how to configure virus scanning and handle scan failures."}

Example:
Questions:
- Is there a REST API to deactivate a list of Scheduled Actions?
- Can we trigger a file transfer via a REST API call instead of a scheduled action?
Answer: {"topic": "Scheduled Action APIs", "summary": "Users want REST APIs to trigger or manage scheduled actions instead of using the scheduler."}

Example:
Questions:
- Why won't the MFT UI open after upgrading to v12?
- Debug log shows NullPointerException while fetching UI settings — anyone seen this?
Answer: {"topic": "MFT UI Errors", "summary": "Users hit internal errors and exceptions opening the MFT UI after upgrades."}

Now label this group."""

VERIFY_SYSTEM = (
    "You are a strict deduplicator of support-question topics. Two groups are "
    "the same topic ONLY if a single documentation page or how-to answer would "
    "resolve both groups' questions. Sharing the same product, the same general "
    "area, or the same vocabulary does NOT make them the same topic. When in "
    "doubt, answer false.\n\n"
    "Example: Group A asks how the metering agent gets installed; Group B asks "
    "how to set up monitoring alerts. Same product, different features: "
    "{\"same_topic\": false}\n"
    "Example: Group A asks where quarantined files go; Group B asks what happens "
    "to a file when its virus scan fails: {\"same_topic\": true}\n"
    "Example: Group A asks about triggering transfers via REST API; Group B asks "
    "about scheduling recurring transfers: {\"same_topic\": false}\n"
    "Example: Group A asks about resetting passwords; Group B asks about "
    "resetting API keys: {\"same_topic\": false}\n\n"
    "Respond with JSON only."
)

SUMMARY_SYSTEM = (
    "You write a brief executive summary of support-question analytics for a team lead. "
    "2-3 sentences: the dominant themes, with concrete topic names and counts, plus "
    "anything notable (spikes, new topics). No filler, no preamble, no advice.\n"
    "Example: {\"summary\": \"Antivirus scanning dominates this period with 12 "
    "questions, followed by metering setup (7). Cluster failover questions appeared "
    "for the first time.\"}\n"
    "Respond with JSON only."
)

DETECT_SYSTEM = (
    "You find questions and requests for help in Slack messages that don't use "
    "question words or question marks (for example: 'I can't get the webhook to work, "
    "been stuck all day' is a request for help).\n"
    "For each message that asks for help or information, rewrite it as a clear, short "
    "question. Skip statements, status updates, and answers. Messages may be in any "
    "language: keep the rewritten question in its original language.\n"
    "Respond with JSON only: {\"questions\": [{\"index\": <message number>, "
    "\"question\": \"<the rewritten question>\"}]}. Use an empty list if none qualify."
)

EXTRACT_SYSTEM = (
    "You extract every question and request for help from Slack messages.\n"
    "Rules:\n"
    "- Rewrite each one as a clear, self-contained question, dropping greetings "
    "('Hi team'), signatures, and filler.\n"
    "- Keep exact technical terms, product names, error messages, and version numbers "
    "verbatim — never paraphrase or invent details that aren't in the message.\n"
    "- A message may contain several questions: output one entry per question, "
    "repeating the message number.\n"
    "- Implicit help requests count.\n"
    "- Skip statements, status updates, headers, and answers.\n"
    "- Messages may be in any language: keep the rewritten question in its "
    "original language.\n"
    "Respond with JSON only: {\"questions\": [{\"index\": <message number>, "
    "\"question\": \"<the question>\"}]}. Use an empty list if none qualify."
)

EXTRACT_FEW_SHOT = """Example messages:
0. Hi all! Quick one — can we trigger transfers via REST instead of the scheduler? Also is there a way to bulk-disable actions?
1. Deployed the fix to prod this morning, all green.
2. been fighting the SFTP connection all day, keeps refusing, no idea why

Example answer: {"questions": [
{"index": 0, "question": "Can we trigger transfers via REST instead of the scheduler?"},
{"index": 0, "question": "Is there a way to bulk-disable actions?"},
{"index": 2, "question": "Why does my SFTP connection keep getting refused?"}]}

Now extract from these messages."""

ANSWERED_SYSTEM = (
    "You decide whether the replies in a Slack thread actually answered the question.\n"
    "A reply that only acknowledges, asks for more details, says 'I'll look into it', "
    "or links elsewhere without substance does NOT count as an answer.\n"
    "Example: question 'How do I reset my password?', reply 'Settings > Security > "
    "Reset, then check your email.' Answer: {\"answered\": true}\n"
    "Example: question 'Why did my transfer fail?', reply 'Hmm, let me check with the "
    "team.' Answer: {\"answered\": false}\n"
    "Respond with JSON only."
)


class GroupLabeler:
    """LLM prompting layer (labels, verification, summaries, detection)."""

    REQUEST_TIMEOUT_SECONDS = 60
    KEEP_ALIVE = '10m'
    SEED = 42

    def __init__(self, provider: str = 'ollama'):
        load_dotenv()
        self.provider = provider
        self._available: Optional[bool] = None
        self._client = None

        if provider == 'ollama':
            self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434').rstrip('/')
            self.model = os.getenv('OLLAMA_GENERATION_MODEL', 'llama3.2')
        elif provider == 'azure':
            self.model = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT')  # opt-in only
        else:  # openai
            self.model = os.getenv('CHAT_MODEL', 'gpt-4o-mini')

        # Outputs are deterministic (temperature 0, fixed seed), so caching by
        # prompt makes re-analyzing the same transcript free
        cache_enabled = os.getenv('LLM_CACHE', 'on').lower() not in ('off', '0', 'false')
        self._cache = JsonDiskCache(provider, self.model or 'none',
                                    os.getenv('LLM_CACHE_DIR', '.llm_cache'),
                                    enabled=cache_enabled,
                                    max_entries=int(os.getenv('LLM_CACHE_MAX', '5000')))

        # Optional domain hint injected into every prompt: knowing the product
        # makes small models dramatically more specific
        self.domain_context = os.getenv('DOMAIN_CONTEXT', '').strip()

    def _system(self, base: str) -> str:
        """System prompt with the optional domain context appended."""
        if self.domain_context:
            return f"{base}\nContext: the messages come from {self.domain_context}."
        return base

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    def available(self) -> bool:
        """Whether a generation model is actually usable (cached)."""
        if self._available is None:
            self._available = self._check_available()
        return self._available

    def _check_available(self) -> bool:
        if self.provider == 'ollama':
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
                response.raise_for_status()
                names = [m.get('name', '') for m in response.json().get('models', [])]
                return any(n == self.model or n.startswith(f"{self.model}:") for n in names)
            except (requests.RequestException, ValueError):
                return False
        if self.provider == 'azure':
            return bool(self.model and os.getenv('AZURE_OPENAI_API_KEY'))
        return bool(os.getenv('OPENAI_API_KEY'))  # openai

    # ------------------------------------------------------------------
    # Generation core
    # ------------------------------------------------------------------

    def _chat(self, messages: List[Dict], schema: Dict, max_tokens: int = 300) -> str:
        """One chat completion with schema-enforced JSON output."""
        if self.provider == 'ollama':
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    'model': self.model,
                    'messages': messages,
                    'stream': False,
                    'format': schema,  # Ollama enforces the JSON schema while decoding
                    'options': {'temperature': 0, 'seed': self.SEED,
                                'num_predict': max_tokens},
                    'keep_alive': self.KEEP_ALIVE,  # stay loaded across our call series
                },
                timeout=self.REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return response.json().get('message', {}).get('content', '')

        if self._client is None:
            from openai import AzureOpenAI, OpenAI
            if self.provider == 'azure':
                self._client = AzureOpenAI(
                    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                    api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
                    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                )
            else:
                self._client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
            max_tokens=max_tokens,
            response_format={'type': 'json_schema',
                             'json_schema': {'name': 'response', 'schema': schema}},
        )
        return response.choices[0].message.content or ''

    @staticmethod
    def _parse_json(raw: str) -> Optional[Dict]:
        """Parse model output; tolerate JSON wrapped in prose."""
        match = re.search(r'\{.*\}', raw, flags=re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    def _generate_json(self, system: str, user: str, schema: Dict,
                       validator=None, corrective: str = '',
                       max_tokens: int = 300) -> Optional[Dict]:
        """
        Chat once; if validation fails, retry once with corrective feedback
        appended to the conversation. Returns None when both attempts fail.
        Successful (validated) results are cached on disk by prompt.
        """
        cache_key = f"{self.model}\n{system}\n{user}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        messages = [{'role': 'system', 'content': system},
                    {'role': 'user', 'content': user}]
        try:
            raw = self._chat(messages, schema, max_tokens=max_tokens)
            data = self._parse_json(raw)
            problem = ('Response was not valid JSON.' if data is None
                       else (validator(data) if validator else None))
            if problem is None:
                self._cache.set(cache_key, data)
                self._cache.save()
                return data

            if corrective:
                messages.append({'role': 'assistant', 'content': raw})
                messages.append({'role': 'user', 'content': f"{corrective} ({problem})"})
                raw = self._chat(messages, schema, max_tokens=max_tokens)
                data = self._parse_json(raw)
                if data is not None and (validator is None or validator(data) is None):
                    self._cache.set(cache_key, data)
                    self._cache.save()
                    return data
            return None
        except Exception as e:
            logger.warning("LLM call failed: %s", e)
            return None

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_label(data: Dict) -> Optional[str]:
        """Return a problem description, or None when the label is good."""
        topic = str(data.get('topic', '')).strip()
        summary = str(data.get('summary', '')).strip()
        if not topic:
            return 'topic was empty'
        words = [w.strip('.,!?').lower() for w in topic.split()]
        if all(w in GENERIC_TOPIC_WORDS for w in words):
            return f"topic '{topic}' is too generic"
        if not summary:
            return 'summary was empty'
        return None

    def label_group(self, question_texts: List[str],
                    keywords: Optional[List[str]] = None) -> Optional[Dict[str, str]]:
        """
        Generate {'topic', 'summary'} for a group of similar questions.
        Returns None on any failure — callers should fall back gracefully.
        """
        sample = question_texts[:MAX_QUESTIONS_IN_PROMPT]
        parts = [LABEL_FEW_SHOT]
        if keywords:
            parts.append(f"Keywords: {', '.join(keywords[:5])}")
        parts.append('Questions:\n' + '\n'.join(f"- {q}" for q in sample))
        user = '\n'.join(parts)

        data = self._generate_json(
            self._system(LABEL_SYSTEM), user, LABEL_SCHEMA,
            validator=self._validate_label,
            corrective='Your previous answer was rejected. The topic must name the '
                       'specific feature, system, or task in 2-4 words. Respond with '
                       'JSON only.',
        )
        if data is None:
            return None

        topic = str(data['topic']).strip()
        topic_words = topic.split()
        if len(topic_words) > MAX_TOPIC_WORDS:
            topic = ' '.join(topic_words[:MAX_TOPIC_WORDS])
        return {'topic': topic, 'summary': str(data['summary']).strip()}

    def verify_same_topic(self, questions_a: List[str],
                          questions_b: List[str]) -> Optional[bool]:
        """Decide whether two borderline groups ask about the same topic."""
        user = (
            'Group A:\n' + '\n'.join(f"- {q}" for q in questions_a[:3]) +
            '\n\nGroup B:\n' + '\n'.join(f"- {q}" for q in questions_b[:3]) +
            '\n\nDo Group A and Group B ask about the same underlying topic?'
        )
        data = self._generate_json(self._system(VERIFY_SYSTEM), user, VERIFY_SCHEMA, max_tokens=60)
        if data is None or not isinstance(data.get('same_topic'), bool):
            return None
        return data['same_topic']

    def summarize_analysis(self, groups: List[Dict], total_questions: int) -> Optional[str]:
        """Write a 2-3 sentence executive summary of the top question groups."""
        lines = [f"Total questions analyzed: {total_questions}", 'Top question groups:']
        for i, group in enumerate(groups[:10], 1):
            topic = group.get('topic') or group['representative_question']
            lines.append(f"{i}. {topic} — asked {group['count']} times "
                         f"(e.g. \"{group['representative_question']}\")")
        data = self._generate_json(
            self._system(SUMMARY_SYSTEM), '\n'.join(lines), SUMMARY_SCHEMA,
            validator=lambda d: None if str(d.get('summary', '')).strip() else 'summary was empty',
            corrective='Respond with JSON only and a non-empty summary.',
        )
        if data is None:
            return None
        return str(data['summary']).strip()

    def detect_questions(self, message_texts: List[str]) -> List[Dict]:
        """
        Find implicit help requests in messages the regex extractor skipped.
        Returns [{'index': int, 'question': str}], empty on failure.
        """
        return self._questions_from_llm(message_texts, self._system(DETECT_SYSTEM)) or []

    def extract_questions(self, message_texts: List[str]) -> Optional[List[Dict]]:
        """
        LLM-first extraction (LLM_EXTRACTION=full): pull every question out of
        every message, cleaned and rewritten. Multiple questions per message
        are allowed. Returns [{'index': int, 'question': str}]; an empty list
        means "no questions here", None means the call failed.
        """
        return self._questions_from_llm(message_texts, self._system(EXTRACT_SYSTEM))

    def _questions_from_llm(self, message_texts: List[str],
                            system: str) -> Optional[List[Dict]]:
        numbered = '\n'.join(f"{i}. {text[:600]}" for i, text in enumerate(message_texts))
        user = (f"{EXTRACT_FEW_SHOT}\n{numbered}" if system.startswith(EXTRACT_SYSTEM[:40])
                else f"Messages:\n{numbered}")
        data = self._generate_json(system, user, DETECT_SCHEMA,
                                   max_tokens=800)
        if data is None or not isinstance(data.get('questions'), list):
            return None

        found = []
        for item in data['questions']:
            if not isinstance(item, dict):
                continue
            index = item.get('index')
            question = str(item.get('question', '')).strip()
            if isinstance(index, int) and 0 <= index < len(message_texts) and question:
                found.append({'index': index, 'question': question})
        return found

    def is_answered(self, question: str, replies: List[str]) -> Optional[bool]:
        """Decide whether thread replies actually answered the question."""
        user = (
            f"Question: {question}\n\nThread replies:\n" +
            '\n'.join(f"- {r[:300]}" for r in replies[:5]) +
            '\n\nWas the question answered by these replies?'
        )
        data = self._generate_json(self._system(ANSWERED_SYSTEM), user, ANSWERED_SCHEMA, max_tokens=60)
        if data is None or not isinstance(data.get('answered'), bool):
            return None
        return data['answered']
