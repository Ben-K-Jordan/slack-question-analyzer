"""
Optional LLM-generated topic labels and summaries for question groups.

Uses a local Ollama chat model (or OpenAI/Azure) to give each question group
a short human-readable topic name and a one-sentence summary. Entirely
optional: when no generation model is available, callers fall back to
keyword-based labels and the analysis still works.
"""

import os
import json
import re
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

PROMPT_TEMPLATE = """You label groups of similar support questions from a Slack channel.

Below are questions that were grouped together because they ask about the same thing.
Respond with JSON only, in exactly this shape:
{{"topic": "<topic name, 2-4 words>", "summary": "<one sentence describing what people are asking>"}}

Questions:
{questions}"""

MAX_QUESTIONS_IN_PROMPT = 8
MAX_TOPIC_WORDS = 6


class GroupLabeler:
    """Generates topic labels for question groups via a chat/generation model."""

    REQUEST_TIMEOUT_SECONDS = 30

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

    def label_group(self, question_texts: List[str]) -> Optional[Dict[str, str]]:
        """
        Generate {'topic', 'summary'} for a group of similar questions.
        Returns None on any failure — callers should fall back gracefully.
        """
        sample = question_texts[:MAX_QUESTIONS_IN_PROMPT]
        prompt = PROMPT_TEMPLATE.format(
            questions='\n'.join(f"- {q}" for q in sample)
        )

        try:
            if self.provider == 'ollama':
                raw = self._generate_ollama(prompt)
            else:
                raw = self._generate_openai(prompt)
            return self._parse_label(raw)
        except Exception as e:
            print(f"Warning: group labeling failed ({e}); using keyword fallback")
            return None

    def _generate_ollama(self, prompt: str) -> str:
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                'model': self.model,
                'prompt': prompt,
                'stream': False,
                'format': 'json',
                'options': {'temperature': 0},
            },
            timeout=self.REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json().get('response', '')

    def _generate_openai(self, prompt: str) -> str:
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
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0,
            response_format={'type': 'json_object'},
        )
        return response.choices[0].message.content or ''

    @staticmethod
    def _parse_label(raw: str) -> Optional[Dict[str, str]]:
        """Parse and sanity-check the model's JSON output."""
        # Models occasionally wrap JSON in prose; grab the first object
        match = re.search(r'\{.*\}', raw, flags=re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

        topic = str(data.get('topic', '')).strip()
        summary = str(data.get('summary', '')).strip()
        if not topic:
            return None

        # Keep topics short even if the model rambles
        topic_words = topic.split()
        if len(topic_words) > MAX_TOPIC_WORDS:
            topic = ' '.join(topic_words[:MAX_TOPIC_WORDS])

        return {'topic': topic, 'summary': summary}
