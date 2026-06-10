"""
Question extraction and parsing module.
Extracts questions from Slack content in multiple formats:

- Plain text with dashed separators between messages
- Slack JSON exports (a list of message objects, or {"messages": [...]})
- CSV with a text/message/question column and optional date column

Slack markup (mentions, links, emoji codes, code blocks) is stripped before
question detection so it doesn't pollute grouping.
"""

import re
import csv
import io
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional


class QuestionExtractor:
    """Extracts and normalizes questions from Slack messages."""

    # A sentence is treated as a question when it starts with an
    # interrogative/auxiliary word, not merely when it contains one —
    # otherwise nearly every declarative sentence matches.
    QUESTION_STARTERS = (
        r'^(how|what|when|where|why|who|whom|whose|which|can|could|would|will|'
        r'should|shall|is|are|was|were|does|do|did|has|have|had|may|might|am)\b'
    )

    # Help-seeking phrases that signal a question anywhere in the sentence
    HELP_PATTERNS = (
        r'\b(anyone|anybody|someone|somebody)\s+(know|knows|have|has|tried|'
        r'familiar|help|else|here)\b'
        r'|\b(any\s+(idea|ideas|thoughts|suggestions|recommendations|pointers))\b'
        r'|\b(is\s+there\s+a\s+way)\b'
        r'|\b(wondering\s+(if|how|whether|what|why))\b'
        r'|\b(not\s+sure\s+(how|if|whether|why|what))\b'
    )

    MIN_QUESTION_WORDS = 3  # Ignore fragments like "Why?" split from context

    def __init__(self):
        self.starter_regex = re.compile(self.QUESTION_STARTERS, re.IGNORECASE)
        self.help_regex = re.compile(self.HELP_PATTERNS, re.IGNORECASE)

    def is_question(self, sentence: str) -> bool:
        """Determine whether a sentence is a question or help request."""
        sentence = sentence.strip()
        if not sentence:
            return False
        if sentence.endswith('?'):
            return True
        if len(sentence.split()) < self.MIN_QUESTION_WORDS:
            return False
        return bool(self.starter_regex.search(sentence) or self.help_regex.search(sentence))

    def extract_questions(self, text: str) -> List[str]:
        """
        Extract questions from text.

        Args:
            text: Raw text from Slack message

        Returns:
            List of extracted question strings
        """
        # Split into sentences, keeping the trailing '?' so it can be detected
        sentences = re.findall(r'[^.!?\n]+[.!?]?', text)

        questions = []
        for sentence in sentences:
            sentence = sentence.strip()
            if self.is_question(sentence):
                # Drop trailing '.'/'!' but keep '?'
                questions.append(sentence.rstrip('.!').strip())

        return questions

    def normalize_question(self, question: str) -> str:
        """
        Normalize a question for better comparison.

        Args:
            question: Raw question text

        Returns:
            Normalized question text
        """
        # Convert to lowercase
        normalized = question.lower()

        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)

        # Remove special characters but keep question marks
        normalized = re.sub(r'[^\w\s?-]', '', normalized)

        # Remove common filler words
        filler_words = ['hi', 'hello', 'hey', 'team', 'guys', 'folks', 'please', 'thanks', 'thank you']
        for word in filler_words:
            normalized = re.sub(r'\b' + word + r'\b', '', normalized, flags=re.IGNORECASE)

        # Clean up extra spaces again
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def parse_slack_content(self, content: str) -> List[Dict]:
        """
        Parse Slack content and extract questions with metadata.
        The format (JSON, CSV, or plain text) is detected automatically.

        Args:
            content: Raw Slack content string

        Returns:
            List of dictionaries containing questions and metadata
        """
        return self.questions_from_messages(self.extract_messages(content))

    def extract_messages(self, content: str) -> List[Dict]:
        """
        Split raw content into individual messages, detecting the format.

        Returns a list of {'text', 'date', 'replies'} dicts (replies only
        present for Slack JSON exports with threads).
        """
        stripped = content.lstrip()
        if stripped.startswith('{') or stripped.startswith('['):
            messages = self._messages_from_json(stripped)
            if messages is not None:
                return messages

        messages = self._messages_from_csv(content)
        if messages is not None:
            return messages

        return self._messages_from_text(content)

    # ---- Slack markup ----

    @staticmethod
    def clean_slack_markup(text: str) -> str:
        """Strip Slack-specific markup so it doesn't pollute question grouping."""
        # Fenced code blocks are usually logs/stack traces, not question text
        text = re.sub(r'```.*?```', ' ', text, flags=re.DOTALL)
        text = text.replace('`', '')
        # <@U123> / <@U123|name> user mentions
        text = re.sub(r'<@[A-Z0-9]+(?:\|[^>]*)?>', '', text)
        # <#C123|channel-name> channel links
        text = re.sub(r'<#[A-Z0-9]+\|([^>]*)>', r'#\1', text)
        # <!here>, <!channel>, <!everyone> broadcasts
        text = re.sub(r'<!(?:here|channel|everyone)>', '', text)
        # <http://url|label> -> label, bare <http://url> -> dropped
        text = re.sub(r'<https?://[^|>]+\|([^>]*)>', r'\1', text)
        text = re.sub(r'<https?://[^>]+>', '', text)
        # :emoji_codes:
        text = re.sub(r':[a-z0-9_+\-]+:', '', text)
        # HTML entities Slack escapes
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return re.sub(r'[ \t]+', ' ', text).strip()

    # ---- Format-specific parsers ----

    @staticmethod
    def _slack_ts_to_date(ts) -> Optional[str]:
        """Convert a Slack epoch timestamp ('1717589200.000200') to YYYY-MM-DD."""
        try:
            return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime('%Y-%m-%d')
        except (TypeError, ValueError, OSError, OverflowError):
            return None

    def _messages_from_json(self, content: str) -> Optional[List[Dict]]:
        """
        Parse a Slack JSON export. Returns None when it isn't one.

        Thread replies (messages whose thread_ts points at another message)
        are attached to their parent as 'replies' instead of being treated
        as standalone messages, enabling answer detection.
        """
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return None

        if isinstance(data, dict):
            data = data.get('messages')
        if not isinstance(data, list):
            return None

        items = [item for item in data
                 if isinstance(item, dict) and isinstance(item.get('text'), str) and item['text']]

        # Split into thread parents and replies
        replies_by_parent: Dict[str, List[str]] = {}
        parents = []
        for item in items:
            ts = item.get('ts')
            thread_ts = item.get('thread_ts')
            if thread_ts and ts and thread_ts != ts:
                replies_by_parent.setdefault(thread_ts, []).append(
                    self.clean_slack_markup(item['text'])[:300])
            else:
                parents.append(item)

        messages = []
        for item in parents:
            date = item.get('date') or self._slack_ts_to_date(item.get('ts'))
            message = {'text': item['text'], 'date': date}
            replies = replies_by_parent.get(item.get('ts'), [])
            if replies:
                message['replies'] = replies[:5]
            messages.append(message)
        return messages

    _CSV_TEXT_COLUMNS = ('text', 'message', 'question', 'content', 'body')
    _CSV_DATE_COLUMNS = ('date', 'ts', 'timestamp', 'time', 'datetime')

    def _messages_from_csv(self, content: str) -> Optional[List[Dict]]:
        """Parse CSV with a recognizable text column. Returns None otherwise."""
        first_line = content.lstrip().split('\n', 1)[0]
        if ',' not in first_line:
            return None

        try:
            reader = csv.DictReader(io.StringIO(content.lstrip()))
            headers = {h.strip().lower(): h for h in (reader.fieldnames or [])}
        except csv.Error:
            return None

        text_col = next((headers[c] for c in self._CSV_TEXT_COLUMNS if c in headers), None)
        if text_col is None:
            return None
        date_col = next((headers[c] for c in self._CSV_DATE_COLUMNS if c in headers), None)

        messages = []
        try:
            for row in reader:
                text = (row.get(text_col) or '').strip()
                if not text:
                    continue
                date = (row.get(date_col) or '').strip() if date_col else None
                # Numeric timestamps (Slack ts) get converted; date strings pass through
                if date and re.fullmatch(r'\d{9,}(\.\d+)?', date):
                    date = self._slack_ts_to_date(date)
                messages.append({'text': text, 'date': date or None})
        except csv.Error:
            return None
        return messages

    def questions_from_messages(self, messages: List[Dict]) -> List[Dict]:
        """Extract questions from structured {'text', 'date', 'replies'} messages."""
        parsed_questions = []
        for message in messages:
            text = self.clean_slack_markup(message['text'].replace('\n', ' '))
            for question in self.extract_questions(text):
                parsed = {
                    'text': question,
                    'normalized_text': self.normalize_question(question),
                    'date': message.get('date') or 'Unknown',
                    'original_message': text[:200]
                }
                if message.get('replies'):
                    parsed['replies'] = message['replies']
                parsed_questions.append(parsed)
        return parsed_questions

    def _messages_from_text(self, content: str) -> List[Dict]:
        """Parse plain text with dashed separator lines between messages."""
        # Split by separator line (a run of 10+ dashes on its own line)
        blocks = re.split(r'\n-{10,}\n?|^-{10,}\n', content)

        messages = []

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            # Extract date (first line typically)
            lines = block.split('\n')
            date = None
            text_lines = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Take the first date found; a line that is ONLY a date is
                # consumed, but a line with a date AND text keeps its text
                if not date:
                    found, pure_date_line = self._extract_date(line)
                    if found:
                        date = found
                        if pure_date_line:
                            continue
                text_lines.append(line)

            if text_lines:
                messages.append({'text': ' '.join(text_lines), 'date': date})

        return messages

    _DATE_PATTERNS = [
        r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',  # YYYY-MM-DD
        r'\b\w+\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b',  # MM/DD/YYYY
    ]

    def _extract_date(self, line: str):
        """
        Find a date in a line.

        Returns (date_string, is_pure_date_line): is_pure_date_line is True
        when the line contains nothing meaningful besides the date.
        """
        for pattern in self._DATE_PATTERNS:
            match = re.search(pattern, line)
            if match:
                rest = line[:match.start()] + line[match.end():]
                rest_words = re.findall(r'[A-Za-z0-9]+', rest)
                return match.group(0), len(rest_words) < 3
        return None, False
