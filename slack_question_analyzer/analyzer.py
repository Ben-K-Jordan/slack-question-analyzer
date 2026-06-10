"""
Main analyzer module that orchestrates question extraction, grouping, and ranking.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Literal
from datetime import datetime, timezone
import numpy as np
from dotenv import load_dotenv
from .question_extractor import QuestionExtractor
from .similarity_analyzer import SimilarityAnalyzer
from .group_labeler import GroupLabeler
from .exporters import to_csv, to_markdown

logger = logging.getLogger(__name__)

# Caps keep the optional LLM passes fast on huge transcripts
MAX_LABELED_GROUPS = 20
MAX_DETECTED_MESSAGES = 40
DETECT_BATCH_SIZE = 8
MAX_ANSWER_CHECKS = 20
MIN_DETECT_MESSAGE_CHARS = 20


class QuestionAnalyzer:
    """Main analyzer class that coordinates the analysis pipeline."""

    def __init__(self, provider: Optional[Literal['azure', 'openai', 'ollama']] = None,
                 use_disk_cache: bool = True, threshold: Optional[float] = None,
                 label_groups: Optional[bool] = None):
        """
        Initialize the analyzer.

        Args:
            provider: AI provider to use ('azure', 'openai', or 'ollama').
                     If None, reads from AI_PROVIDER env variable (defaults to 'ollama')
            use_disk_cache: Persist embeddings to disk so repeat runs are fast
            threshold: Similarity threshold (0-1). Overrides the
                       SIMILARITY_THRESHOLD env variable when given.
            label_groups: Generate LLM topic labels/summaries per group.
                          None (default) reads GROUP_LABELS env: 'auto' labels
                          when a generation model is available, 'on'/'off' force it.
        """
        load_dotenv()

        if provider is None:
            provider = os.getenv('AI_PROVIDER', 'ollama')

        self.extractor = QuestionExtractor()
        self.similarity_analyzer = SimilarityAnalyzer(provider=provider,
                                                      use_disk_cache=use_disk_cache,
                                                      threshold=threshold)

        if label_groups is None:
            mode = os.getenv('GROUP_LABELS', 'auto').lower()
        else:
            mode = 'on' if label_groups else 'off'
        # GROUP_LABELS=off disables ALL LLM features (labels, verification,
        # detection, answers, executive summary)
        self.labeler = GroupLabeler(provider) if mode in ('auto', 'on') else None
        self._labels_forced = (mode == 'on')

        # Per-feature switches; each is 'auto' (use when model available),
        # 'on', or 'off'
        self._verify_mode = os.getenv('LLM_VERIFY_GROUPS', 'auto').lower()
        self._detect_mode = os.getenv('LLM_EXTRACTION', 'auto').lower()
        self._answers_mode = os.getenv('LLM_ANSWER_DETECTION', 'auto').lower()
        self._summary_mode = os.getenv('EXECUTIVE_SUMMARY', 'auto').lower()

    def _llm_enabled(self, mode: str) -> bool:
        """Whether an optional LLM feature should run."""
        if self.labeler is None or mode == 'off':
            return False
        if mode == 'on':
            return True
        return self._labels_forced or self.labeler.available()  # 'auto'

    def analyze_slack_content(self, content: str, progress_callback=None) -> Dict:
        """
        Analyze Slack content and return grouped questions.

        Args:
            content: Raw Slack content string
            progress_callback: Optional fn(stage, completed, total) reporting
                progress. Stages: 'extracting', 'embedding', 'grouping',
                'keywords', 'complete'. For 'embedding', completed/total count
                individual embeddings; other stages report (0, 1) then (1, 1).

        Returns:
            Dictionary containing analysis results
        """
        return self.analyze_contents([content], progress_callback=progress_callback)

    def analyze_contents(self, contents: List[str], progress_callback=None) -> Dict:
        """
        Analyze one or more Slack content strings as a single corpus.

        Used for multi-file uploads (e.g. a zipped Slack export with one JSON
        file per day): messages from every file are merged before analysis.
        """
        def report(stage, completed=0, total=1):
            if progress_callback:
                progress_callback(stage, completed, total)

        report('extracting')
        logger.info("Step 1: Extracting questions from %d file(s)...", len(contents))
        messages = []
        for content in contents:
            messages.extend(self.extractor.extract_messages(content))
        questions = self.extractor.questions_from_messages(messages)
        logger.info("Found %d questions", len(questions))
        report('extracting', 1, 1)

        # Optional LLM pass: catch implicit help requests the regex missed
        if self._llm_enabled(self._detect_mode):
            questions += self._detect_missed_questions(messages, questions, report)

        if not questions:
            report('complete', 1, 1)
            return {
                'total_questions': 0,
                'total_groups': 0,
                'groups': [],
                'ungrouped_questions': [],
                'metadata': self._metadata()
            }

        verifier = (self.labeler.verify_same_topic
                    if self._llm_enabled(self._verify_mode) else None)

        logger.info("Step 2: Grouping similar questions using AI...")
        groups = self.similarity_analyzer.group_similar_questions(
            questions,
            progress_callback=(lambda done, total: report('embedding', done, total)),
            verifier=verifier
        )
        logger.info("Created %d question groups", len(groups))
        report('grouping', 1, 1)

        # Add keywords and date ranges to each group
        logger.info("Step 3: Extracting keywords from groups...")
        for group in groups:
            group['keywords'] = self._extract_keywords(group['questions'])
            group['date_range'] = self._date_range(group['questions'])
        report('keywords', 1, 1)

        # Optional LLM pass: name each group and summarize what's being asked
        self._label_groups(groups, report)

        # Optional LLM pass: did thread replies answer the question?
        answered_total = self._detect_answers(questions, groups, report)

        # Separate single-question groups
        multi_question_groups = [g for g in groups if g['count'] > 1]
        single_questions = [g for g in groups if g['count'] == 1]

        result = {
            'total_questions': len(questions),
            'total_groups': len(multi_question_groups),
            'groups': multi_question_groups,
            'ungrouped_questions': [q['questions'][0] for q in single_questions],
            'answered_questions': answered_total,
            'metadata': self._metadata()
        }

        # Optional LLM pass: 2-3 sentence executive summary
        if self._llm_enabled(self._summary_mode) and multi_question_groups:
            report('summarizing', 0, 1)
            logger.info("Generating executive summary...")
            result['executive_summary'] = self.labeler.summarize_analysis(
                multi_question_groups, len(questions))
            report('summarizing', 1, 1)
        else:
            result['executive_summary'] = None

        report('complete', 1, 1)
        return result

    def _detect_missed_questions(self, messages: List[Dict], questions: List[Dict],
                                 report) -> List[Dict]:
        """LLM pass over messages where the regex extractor found nothing."""
        matched = {q['original_message'] for q in questions}
        unmatched = []
        for message in messages:
            text = self.extractor.clean_slack_markup(message['text'].replace('\n', ' '))
            if len(text) >= MIN_DETECT_MESSAGE_CHARS and text[:200] not in matched:
                unmatched.append({'text': text, 'date': message.get('date'),
                                  'replies': message.get('replies')})
        unmatched = unmatched[:MAX_DETECTED_MESSAGES]
        if not unmatched:
            return []

        logger.info("Checking %d unmatched messages for implicit questions...", len(unmatched))
        batches = [unmatched[i:i + DETECT_BATCH_SIZE]
                   for i in range(0, len(unmatched), DETECT_BATCH_SIZE)]
        found = []
        report('detecting', 0, len(batches))
        for batch_num, batch in enumerate(batches, 1):
            for hit in self.labeler.detect_questions([m['text'] for m in batch]):
                message = batch[hit['index']]
                question = {
                    'text': hit['question'],
                    'normalized_text': self.extractor.normalize_question(hit['question']),
                    'date': message.get('date') or 'Unknown',
                    'original_message': message['text'][:200],
                    'llm_detected': True,
                }
                if message.get('replies'):
                    question['replies'] = message['replies']
                found.append(question)
            report('detecting', batch_num, len(batches))

        if found:
            logger.info("LLM found %d additional question(s)", len(found))
        return found

    def _detect_answers(self, questions: List[Dict], groups: List[Dict], report) -> int:
        """LLM pass: mark questions whose thread replies actually answered them."""
        if not self._llm_enabled(self._answers_mode):
            return 0
        candidates = [q for q in questions if q.get('replies')][:MAX_ANSWER_CHECKS]
        if not candidates:
            return 0

        logger.info("Checking %d threads for answers...", len(candidates))
        report('answers', 0, len(candidates))
        answered_total = 0
        for i, question in enumerate(candidates, 1):
            verdict = self.labeler.is_answered(question['text'], question['replies'])
            if verdict is not None:
                question['answered'] = verdict
                if verdict:
                    answered_total += 1
            report('answers', i, len(candidates))

        # Question dicts are shared with groups, so per-group counts are free
        for group in groups:
            group['answered'] = sum(1 for q in group['questions'] if q.get('answered'))
        return answered_total

    def _metadata(self) -> Dict:
        return {
            'analyzed_at': datetime.now(timezone.utc).isoformat(),
            'similarity_threshold': self.similarity_analyzer.similarity_threshold,
            'model': self.similarity_analyzer.embedding_model,
            'provider': self.similarity_analyzer.provider
        }

    def _label_groups(self, groups: List[Dict], report):
        """
        Give each group a 'topic' (and, when an LLM is available, a 'summary').

        Multi-question groups get LLM-generated labels when a generation model
        is configured and reachable; everything else falls back to keywords.
        """
        candidates = [g for g in groups if g['count'] > 1][:MAX_LABELED_GROUPS]
        use_llm = self.labeler is not None and (self._labels_forced or self.labeler.available())

        if use_llm and candidates:
            logger.info("Step 4: Generating topic labels with %s...", self.labeler.model)
            report('labeling', 0, len(candidates))
            for i, group in enumerate(candidates, 1):
                sample = self._diverse_sample(group['questions'])
                label = self.labeler.label_group([q['text'] for q in sample],
                                                 keywords=group.get('keywords'))
                if label:
                    group['topic'] = label['topic']
                    group['summary'] = label['summary']
                report('labeling', i, len(candidates))

        # Keyword fallback for anything the LLM didn't (or couldn't) label
        for group in groups:
            if not group.get('topic'):
                group['topic'] = self._keyword_topic(group)
                group['summary'] = None

    def _diverse_sample(self, questions: List[Dict], k: int = 8) -> List[Dict]:
        """
        Pick up to k questions that span the group's breadth, so the labeling
        prompt sees different phrasings instead of the same one repeated.
        Uses cached embeddings via greedy farthest-point selection; falls back
        to the first k distinct phrasings when embeddings aren't cached.
        """
        # One entry per distinct phrasing, preserving order
        seen = set()
        distinct = []
        for q in questions:
            if q['normalized_text'] not in seen:
                seen.add(q['normalized_text'])
                distinct.append(q)
        if len(distinct) <= k:
            return distinct

        cache = self.similarity_analyzer.embeddings_cache
        vectors = [cache.get(q['normalized_text']) for q in distinct]
        if any(v is None for v in vectors):
            return distinct[:k]

        matrix = np.array(vectors)
        chosen = [0]  # the first (often most common) phrasing seeds the sample
        while len(chosen) < k:
            chosen_matrix = matrix[chosen]
            # For each candidate, distance to its nearest already-chosen point
            distances = np.min(
                np.linalg.norm(matrix[:, None, :] - chosen_matrix[None, :, :], axis=2),
                axis=1)
            distances[chosen] = -1
            chosen.append(int(np.argmax(distances)))
        return [distinct[i] for i in sorted(chosen)]

    @staticmethod
    def _keyword_topic(group: Dict) -> str:
        keywords = group.get('keywords') or []
        if keywords:
            return ' / '.join(k.capitalize() for k in keywords[:2])
        words = group['representative_question'].split()[:4]
        return ' '.join(words)

    @staticmethod
    def _date_range(questions: List[Dict]) -> Dict:
        """First and last date a question in this group was asked."""
        dates = sorted(q['date'] for q in questions if q.get('date') and q['date'] != 'Unknown')
        return {
            'first_asked': dates[0] if dates else None,
            'last_asked': dates[-1] if dates else None
        }

    def analyze_from_file(self, input_path: str, output_path: Optional[str] = None) -> Dict:
        """
        Analyze questions from a file.

        Args:
            input_path: Path to input file containing Slack content
            output_path: Optional path to save results. Format is inferred from
                         the extension: .json, .csv, or .md

        Returns:
            Analysis results dictionary
        """
        logger.info("Reading input from: %s", input_path)

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        results = self.analyze_slack_content(content)

        if output_path:
            logger.info("Saving results to: %s", output_path)
            self.save_results(results, output_path)

        return results

    def save_results(self, results: Dict, output_path: str):
        """Save results in the format implied by the file extension."""
        lower = output_path.lower()
        if lower.endswith('.csv'):
            self.export_csv(results, output_path)
        elif lower.endswith('.md') or lower.endswith('.markdown'):
            self.export_markdown(results, output_path)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

    def export_csv(self, results: Dict, output_path: str):
        """Export grouped questions as a flat CSV (one row per question)."""
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            f.write(to_csv(results))

    def export_markdown(self, results: Dict, output_path: str):
        """Export results as a readable Markdown report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(to_markdown(results))

    def _extract_keywords(self, questions: List[Dict]) -> List[str]:
        """
        Extract common keywords from a group of questions.

        Args:
            questions: List of question dictionaries

        Returns:
            List of keywords
        """
        # Common words to ignore
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'when', 'where', 'why', 'how', 'there', 'here'
        }

        # Count word frequencies
        word_freq = {}
        for q in questions:
            words = q['normalized_text'].lower().split()
            for word in words:
                # Remove non-alphanumeric characters
                word = ''.join(c for c in word if c.isalnum())
                if len(word) > 3 and word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1

        # Get top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, _ in sorted_words[:5]]

        return keywords

    def print_summary(self, results: Dict):
        """
        Print a human-readable summary of the analysis.

        Args:
            results: Analysis results dictionary
        """
        print("\n" + "="*80)
        print("QUESTION ANALYSIS SUMMARY")
        print("="*80)
        print(f"\nTotal Questions Analyzed: {results['total_questions']}")
        print(f"Question Groups Found: {results['total_groups']}")
        print(f"Ungrouped Questions: {len(results['ungrouped_questions'])}")
        if results.get('answered_questions'):
            print(f"Answered (via thread replies): {results['answered_questions']}")
        print(f"Similarity Threshold: {results['metadata']['similarity_threshold']}")
        print(f"Model Used: {results['metadata']['model']}")

        if results.get('executive_summary'):
            print("\n" + "-"*80)
            print("EXECUTIVE SUMMARY")
            print("-"*80)
            print(results['executive_summary'])

        if results['groups']:
            print("\n" + "-"*80)
            print("TOP QUESTION GROUPS (Ranked by Frequency)")
            print("-"*80)

            for i, group in enumerate(results['groups'][:10], 1):  # Show top 10
                topic = f" [{group['topic']}]" if group.get('topic') else ''
                print(f"\n#{i}{topic} - Occurrences: {group['count']}")
                print(f"Representative Question: {group['representative_question']}")
                if group.get('summary'):
                    print(f"Summary: {group['summary']}")
                print(f"Keywords: {', '.join(group['keywords'])}")
                print(f"Average Similarity: {group['avg_similarity']:.2%}")
                if group.get('answered'):
                    print(f"Answered: {group['answered']} of {group['count']}")

                if group['count'] <= 5:  # Show all questions if 5 or fewer
                    print("All questions in this group:")
                    for q in group['questions']:
                        print(f"  - {q['text'][:100]}")

        if results['ungrouped_questions']:
            print("\n" + "-"*80)
            print(f"UNIQUE QUESTIONS ({len(results['ungrouped_questions'])})")
            print("-"*80)
            for q in results['ungrouped_questions'][:5]:  # Show first 5
                print(f"  - {q['text'][:100]}")

            if len(results['ungrouped_questions']) > 5:
                print(f"  ... and {len(results['ungrouped_questions']) - 5} more")

        print("\n" + "="*80)
