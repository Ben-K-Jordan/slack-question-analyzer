"""
Question extraction and parsing module.
Extracts questions from Slack message text.
"""

import re
from typing import List, Dict


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

        Args:
            content: Raw Slack content string

        Returns:
            List of dictionaries containing questions and metadata
        """
        # Split by separator line (a run of 10+ dashes on its own line)
        messages = re.split(r'\n-{10,}\n?|^-{10,}\n', content)

        parsed_questions = []

        for message in messages:
            message = message.strip()
            if not message:
                continue

            # Extract date (first line typically)
            lines = message.split('\n')
            date = None
            text_lines = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Try to parse as date
                if not date and self._is_date_line(line):
                    date = line
                else:
                    text_lines.append(line)

            # Join remaining text
            text = ' '.join(text_lines)

            # Extract questions from this message
            questions = self.extract_questions(text)

            for question in questions:
                parsed_questions.append({
                    'text': question,
                    'normalized_text': self.normalize_question(question),
                    'date': date or 'Unknown',
                    'original_message': text[:200]  # Keep first 200 chars for context
                })

        return parsed_questions

    def _is_date_line(self, line: str) -> bool:
        """Check if a line looks like a date."""
        date_patterns = [
            r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',  # YYYY-MM-DD
            r'\b\w+\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
            r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b',  # MM/DD/YYYY
        ]

        for pattern in date_patterns:
            if re.search(pattern, line):
                return True

        return False
