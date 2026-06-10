"""
Main analyzer module that orchestrates question extraction, grouping, and ranking.
"""

import os
import csv
import json
from typing import List, Dict, Optional, Literal
from datetime import datetime, timezone
from dotenv import load_dotenv
from .question_extractor import QuestionExtractor
from .similarity_analyzer import SimilarityAnalyzer
from .group_labeler import GroupLabeler

# Cap LLM labeling to the biggest groups so it stays fast on huge transcripts
MAX_LABELED_GROUPS = 20


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
        self.labeler = GroupLabeler(provider) if mode in ('auto', 'on') else None
        self._labels_forced = (mode == 'on')

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
        def report(stage, completed=0, total=1):
            if progress_callback:
                progress_callback(stage, completed, total)

        report('extracting')
        print("Step 1: Extracting questions from Slack content...")
        questions = self.extractor.parse_slack_content(content)
        print(f"Found {len(questions)} questions")
        report('extracting', 1, 1)

        if not questions:
            report('complete', 1, 1)
            return {
                'total_questions': 0,
                'total_groups': 0,
                'groups': [],
                'ungrouped_questions': [],
                'metadata': self._metadata()
            }

        print("\nStep 2: Grouping similar questions using AI...")
        groups = self.similarity_analyzer.group_similar_questions(
            questions,
            progress_callback=(lambda done, total: report('embedding', done, total))
        )
        print(f"Created {len(groups)} question groups")
        report('grouping', 1, 1)

        # Add keywords and date ranges to each group
        print("\nStep 3: Extracting keywords from groups...")
        for group in groups:
            group['keywords'] = self._extract_keywords(group['questions'])
            group['date_range'] = self._date_range(group['questions'])
        report('keywords', 1, 1)

        # Optional LLM pass: name each group and summarize what's being asked
        self._label_groups(groups, report)

        # Separate single-question groups
        multi_question_groups = [g for g in groups if g['count'] > 1]
        single_questions = [g for g in groups if g['count'] == 1]

        result = {
            'total_questions': len(questions),
            'total_groups': len(multi_question_groups),
            'groups': multi_question_groups,
            'ungrouped_questions': [q['questions'][0] for q in single_questions],
            'metadata': self._metadata()
        }

        report('complete', 1, 1)
        return result

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
            print(f"\nStep 4: Generating topic labels with {self.labeler.model}...")
            report('labeling', 0, len(candidates))
            for i, group in enumerate(candidates, 1):
                label = self.labeler.label_group([q['text'] for q in group['questions']])
                if label:
                    group['topic'] = label['topic']
                    group['summary'] = label['summary']
                report('labeling', i, len(candidates))

        # Keyword fallback for anything the LLM didn't (or couldn't) label
        for group in groups:
            if not group.get('topic'):
                group['topic'] = self._keyword_topic(group)
                group['summary'] = None

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
        print(f"Reading input from: {input_path}")

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        results = self.analyze_slack_content(content)

        if output_path:
            print(f"\nSaving results to: {output_path}")
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
            writer = csv.writer(f)
            writer.writerow(['group_rank', 'group_count', 'representative_question',
                             'keywords', 'avg_similarity', 'question', 'date'])
            for rank, group in enumerate(results['groups'], 1):
                for q in group['questions']:
                    writer.writerow([
                        rank, group['count'], group['representative_question'],
                        '; '.join(group['keywords']), f"{group['avg_similarity']:.4f}",
                        q['text'], q.get('date', 'Unknown')
                    ])
            for q in results.get('ungrouped_questions', []):
                writer.writerow(['', 1, q['text'], '', '', q['text'],
                                 q.get('date', 'Unknown')])

    def export_markdown(self, results: Dict, output_path: str):
        """Export results as a readable Markdown report."""
        meta = results['metadata']
        lines = [
            '# Question Analysis Report',
            '',
            f"- **Analyzed at:** {meta['analyzed_at']}",
            f"- **Provider / model:** {meta['provider']} / {meta['model']}",
            f"- **Similarity threshold:** {meta['similarity_threshold']}",
            f"- **Total questions:** {results['total_questions']}",
            f"- **Question groups:** {results['total_groups']}",
            f"- **Unique (ungrouped) questions:** {len(results.get('ungrouped_questions', []))}",
            '',
            '## Top Question Groups',
            ''
        ]

        for rank, group in enumerate(results['groups'], 1):
            title = group.get('topic') or ''
            lines.append(f"### #{rank} — {title + ' — ' if title else ''}asked {group['count']} times")
            lines.append('')
            lines.append(f"**{group['representative_question']}**")
            lines.append('')
            if group.get('summary'):
                lines.append(group['summary'])
                lines.append('')
            if group.get('keywords'):
                lines.append(f"Keywords: {', '.join(group['keywords'])}")
            date_range = group.get('date_range') or {}
            if date_range.get('first_asked'):
                lines.append(f"First asked: {date_range['first_asked']} — "
                             f"Last asked: {date_range['last_asked']}")
            lines.append(f"Average similarity: {group['avg_similarity']:.2%}")
            lines.append('')
            lines.append('<details><summary>All questions in this group</summary>')
            lines.append('')
            for q in group['questions']:
                lines.append(f"- {q['text']} _({q.get('date', 'Unknown')})_")
            lines.append('')
            lines.append('</details>')
            lines.append('')

        ungrouped = results.get('ungrouped_questions', [])
        if ungrouped:
            lines.append(f"## Unique Questions ({len(ungrouped)})")
            lines.append('')
            for q in ungrouped:
                lines.append(f"- {q['text']} _({q.get('date', 'Unknown')})_")
            lines.append('')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

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
        keywords = [word for word, freq in sorted_words[:5]]

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
        print(f"Similarity Threshold: {results['metadata']['similarity_threshold']}")
        print(f"Model Used: {results['metadata']['model']}")

        if results['groups']:
            print("\n" + "-"*80)
            print("TOP QUESTION GROUPS (Ranked by Frequency)")
            print("-"*80)

            for i, group in enumerate(results['groups'][:10], 1):  # Show top 10
                print(f"\n#{i} - Occurrences: {group['count']}")
                print(f"Representative Question: {group['representative_question']}")
                print(f"Keywords: {', '.join(group['keywords'])}")
                print(f"Average Similarity: {group['avg_similarity']:.2%}")

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
