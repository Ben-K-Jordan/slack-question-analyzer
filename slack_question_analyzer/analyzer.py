"""
Main analyzer module that orchestrates question extraction, grouping, and ranking.
"""

import os
import json
import math
import logging
from pathlib import Path
from typing import List, Dict, Optional, Literal
from datetime import datetime, timezone
import numpy as np
from dotenv import load_dotenv
from .question_extractor import QuestionExtractor
from .similarity_analyzer import SimilarityAnalyzer
from .group_labeler import GroupLabeler
from .topic_bank import TopicBank
from .exporters import to_csv, to_markdown

logger = logging.getLogger(__name__)

# Caps keep the optional LLM passes fast on huge transcripts
MAX_LABELED_GROUPS = 20
MAX_DETECTED_MESSAGES = 40
DETECT_BATCH_SIZE = 8
MAX_ANSWER_CHECKS = 20
MIN_DETECT_MESSAGE_CHARS = 20
# 'auto' extraction uses the LLM for everything up to this many messages
MAX_FULL_EXTRACT_MESSAGES = 150


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

        # LLM-first extraction: best quality, so it's the default ('auto') for
        # normal-sized transcripts; 'full' forces it regardless of size
        use_full = (self._detect_mode == 'full'
                    or (self._detect_mode == 'auto'
                        and len(messages) <= MAX_FULL_EXTRACT_MESSAGES))
        did_full = False
        if use_full and self._llm_enabled('auto'):
            # Load the model BEFORE the first timed call: an 8B model's load
            # time alone can blow a per-call timeout and silently downgrade
            # the whole extraction to regex
            self.labeler.warm_up()
            questions = self._extract_questions_llm(messages, report)
            did_full = True
        else:
            questions = self.extractor.questions_from_messages(messages)
        logger.info("Found %d questions", len(questions))
        report('extracting', 1, 1)

        # Optional LLM pass: catch implicit help requests the regex missed
        # (already covered when the LLM did the whole extraction)
        if not did_full and self._detect_mode in ('auto', 'on') \
                and self._llm_enabled(self._detect_mode):
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

        verify_on = self._llm_enabled(self._verify_mode)
        verifier = self.labeler.verify_same_topic if verify_on else None
        auditor = self.labeler.audit_group if verify_on else None

        # First run ever: pre-load the bank with curated starter topics so
        # groups get good names from day one
        self._seed_topic_bank_if_empty()

        logger.info("Step 2: Grouping similar questions using AI...")
        groups = self.similarity_analyzer.group_similar_questions(
            questions,
            progress_callback=(lambda done, total: report('embedding', done, total)),
            verifier=verifier,
            auditor=auditor
        )
        logger.info("Created %d question groups", len(groups))
        report('grouping', 1, 1)

        # Add keywords and date ranges to each group. Keywords are scored
        # against the whole corpus: a word common to every group ("just",
        # "need") characterizes nothing.
        logger.info("Step 3: Extracting keywords from groups...")
        corpus_df = self._corpus_doc_freq(questions)
        for group in groups:
            group['keywords'] = self._extract_keywords(
                group['questions'], corpus_df, len(questions))
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

    def _extract_questions_llm(self, messages: List[Dict], report) -> List[Dict]:
        """
        LLM-first extraction (LLM_EXTRACTION=full): every message goes to the
        LLM, which extracts and cleanly rewrites each question. Batches where
        the LLM fails fall back to the regex extractor, so a flaky model never
        loses questions.
        """
        candidates = []
        for message in messages:
            text = ' '.join(self.extractor.clean_slack_markup(message['text']).split())
            if text:
                candidates.append((text, message))

        batches = [candidates[i:i + DETECT_BATCH_SIZE]
                   for i in range(0, len(candidates), DETECT_BATCH_SIZE)]
        logger.info("LLM-first extraction over %d message(s) in %d batch(es)...",
                    len(candidates), len(batches))

        questions = []
        report('detecting', 0, len(batches))
        for batch_num, batch in enumerate(batches, 1):
            hits = self.labeler.extract_questions([text for text, _ in batch])
            if hits is not None:  # [] is a real answer: "no questions here"
                for hit in hits:
                    text, message = batch[hit['index']]
                    cleaned = self.extractor.strip_greeting(hit['question'])
                    question = {
                        'text': cleaned,
                        'normalized_text': self.extractor.normalize_question(cleaned),
                        'date': message.get('date') or 'Unknown',
                        'original_message': text[:200],
                        'llm_extracted': True,
                    }
                    if message.get('replies'):
                        question['replies'] = message['replies']
                    questions.append(question)
            else:
                # LLM failed for this batch: regex keeps us from losing questions
                questions.extend(self.extractor.questions_from_messages(
                    [message for _, message in batch]))
            report('detecting', batch_num, len(batches))
        return questions

    def _detect_missed_questions(self, messages: List[Dict], questions: List[Dict],
                                 report) -> List[Dict]:
        """LLM pass over messages where the regex extractor found nothing."""
        matched = {q['original_message'] for q in questions}
        unmatched = []
        for message in messages:
            text = ' '.join(self.extractor.clean_slack_markup(message['text']).split())
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
            'provider': self.similarity_analyzer.provider,
            # Pairwise similarity distribution — similarity scales differ
            # between embedding models, so this is how users tune the threshold
            'similarity_stats': self.similarity_analyzer.last_similarity_stats,
            'threshold_auto_adjusted': self.similarity_analyzer.threshold_auto_adjusted,
            # The bar actually used: threshold raised above corpus noise (p90)
            'effective_threshold': self.similarity_analyzer.effective_threshold,
            'noise_gate': self.similarity_analyzer.noise_gate,
        }

    @staticmethod
    def suggested_threshold(results: Dict) -> Optional[float]:
        """
        When nothing grouped, suggest a threshold just below the most similar
        pair so the next run produces at least one group. None when the
        current threshold already groups things (or there's nothing to group).
        """
        metadata = results.get('metadata', {})
        stats = metadata.get('similarity_stats')
        if not stats or results.get('total_groups', 0) > 0:
            return None
        threshold = metadata.get('effective_threshold') or metadata['similarity_threshold']
        if stats['max'] >= threshold:
            return None
        suggestion = round(stats['max'] - 0.02, 2)
        return suggestion if 0 < suggestion < threshold else None

    def _label_groups(self, groups: List[Dict], report):
        """
        Give each group a 'topic' (and, when an LLM is available, a 'summary').

        The topic bank is consulted first: groups matching a known topic keep
        its established name (stable labels across analyses, no LLM call).
        Remaining multi-question groups get LLM-generated labels when a
        generation model is reachable; everything else falls back to keywords.
        """
        candidates = [g for g in groups if g['count'] > 1][:MAX_LABELED_GROUPS]

        # Pass 1: the bank labels topics it has seen before. Bank matching has
        # its own strict floor: auto-threshold may relax grouping, but a loose
        # match inheriting a curated name would be worse than no name.
        bank = TopicBank(model=self.similarity_analyzer.embedding_model)
        bank_matches = {}  # id(group) -> (centroid, matched entry or None)
        labeled_by = {}    # id(group) -> 'bank' | 'llm' | 'keywords'
        if bank.enabled:
            threshold = max(self.similarity_analyzer.similarity_threshold,
                            float(os.getenv('BANK_MATCH_THRESHOLD', '0.85')))
            for group in candidates:
                centroid = self._group_centroid(group)
                matched = bank.match(centroid, threshold)
                bank_matches[id(group)] = (centroid, matched)
                if matched and matched.get('topic'):
                    group['topic'] = matched['topic']
                    group['summary'] = matched.get('summary')
                    labeled_by[id(group)] = 'bank'
            known = sum(1 for _, m in bank_matches.values() if m)
            if known:
                logger.info("Topic bank recognized %d of %d group(s)",
                            known, len(candidates))

        # Pass 2: LLM labels for topics the bank didn't know
        unlabeled = [g for g in candidates if not g.get('topic')]
        use_llm = self.labeler is not None and (self._labels_forced or self.labeler.available())
        if use_llm and unlabeled:
            logger.info("Step 4: Generating topic labels with %s...", self.labeler.model)
            report('labeling', 0, len(unlabeled))
            for i, group in enumerate(unlabeled, 1):
                sample = self._diverse_sample(group['questions'])
                label = self.labeler.label_group([q['text'] for q in sample],
                                                 keywords=group.get('keywords'))
                if label:
                    group['topic'] = label['topic']
                    group['summary'] = label['summary']
                    labeled_by[id(group)] = 'llm'
                report('labeling', i, len(unlabeled))

        # Keyword fallback for anything the LLM didn't (or couldn't) label
        for group in groups:
            if not group.get('topic'):
                group['topic'] = self._keyword_topic(group)
                group['summary'] = None

        # Pass 3: teach the bank — but only quality names. Keyword-fallback
        # topics are never banked: a junk name that sticks is worse than
        # relabeling next time.
        if bank.enabled:
            for group in candidates:
                centroid, matched = bank_matches.get(id(group), (None, None))
                if matched is None and labeled_by.get(id(group)) != 'llm':
                    continue
                entry = bank.record(group, centroid, matched)
                if entry:
                    group['seen_in_analyses'] = entry['analysis_count']
                    group['topic_id'] = entry['id']  # enables renaming in the UI
            bank.save()

    def _seed_topic_bank_if_empty(self):
        """
        Pre-load an empty topic bank from seed_topics.json (curated
        {topic, question} pairs). Embeddings are computed locally on first
        use and cached; failures are non-fatal (the bank just starts empty).
        """
        bank = TopicBank(model=self.similarity_analyzer.embedding_model)
        if not bank.enabled or bank.entries:
            return
        seed_path = Path(os.getenv('SEED_TOPICS_PATH', 'seed_topics.json'))
        if not seed_path.is_file():
            return

        try:
            with open(seed_path, 'r', encoding='utf-8') as f:
                seeds = json.load(f)
            texts = [self.extractor.normalize_question(s['question']) for s in seeds]
            logger.info("Seeding topic bank with %d starter topics "
                        "(embedding them now; one time only)...", len(seeds))
            embeddings = self.similarity_analyzer.get_embeddings_batch(texts)
            for seed, vector in zip(seeds, embeddings, strict=True):
                v = np.asarray(vector, dtype=float)
                norm = np.linalg.norm(v)
                if not norm:
                    continue
                entry = bank.record({'topic': seed['topic'],
                                     'summary': seed.get('summary'),
                                     'representative_question': seed['question'],
                                     'keywords': seed.get('keywords', []),
                                     'count': 0},
                                    (v / norm).tolist())
                if entry:
                    entry['analysis_count'] = 0  # seeds aren't sightings yet
            bank.save()
        except Exception as e:
            logger.warning("Topic bank seeding skipped: %s", e)

    def _group_centroid(self, group: Dict) -> Optional[List[float]]:
        """Mean unit vector of the group's distinct questions (from cache)."""
        cache = self.similarity_analyzer.embeddings_cache
        prefix = self.similarity_analyzer.embed_prefix
        vectors = []
        seen = set()
        for q in group['questions']:
            text = q['normalized_text']
            if text in seen:
                continue
            seen.add(text)
            vector = cache.get(prefix + text)
            if vector is not None:
                v = np.asarray(vector, dtype=float)
                norm = np.linalg.norm(v)
                if norm:
                    vectors.append(v / norm)
        if not vectors:
            return None
        centroid = np.mean(vectors, axis=0)
        norm = np.linalg.norm(centroid)
        return (centroid / norm).tolist() if norm else None

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
        prefix = self.similarity_analyzer.embed_prefix
        vectors = [cache.get(prefix + q['normalized_text']) for q in distinct]
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

    # Words that characterize nothing in a support channel
    KEYWORD_STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
        'who', 'when', 'where', 'why', 'how', 'there', 'here',
        'just', 'need', 'needs', 'needed', 'want', 'wants', 'wanted', 'like',
        'also', 'some', 'any', 'anyone', 'anybody', 'someone', 'something',
        'anything', 'thoughts', 'idea', 'ideas', 'way', 'ways', 'good', 'best',
        'really', 'please', 'thanks', 'know', 'knows', 'one', 'use', 'using',
        'used', 'get', 'gets', 'getting', 'make', 'makes', 'possible', 'able',
        'support', 'supports', 'supported', 'work', 'works', 'working',
        'question', 'questions', 'help', 'team', 'guys', 'mean', 'means',
        'instead', 'either', 'other', 'following', 'right', 'currently',
    }

    @classmethod
    def _question_words(cls, question: Dict) -> set:
        """Distinct meaningful words in one question."""
        words = set()
        for word in question['normalized_text'].lower().split():
            word = ''.join(c for c in word if c.isalnum())
            if len(word) > 3 and word not in cls.KEYWORD_STOP_WORDS:
                words.add(word)
        return words

    def _corpus_doc_freq(self, questions: List[Dict]) -> Dict[str, int]:
        """How many questions in the whole corpus contain each word."""
        df: Dict[str, int] = {}
        for q in questions:
            for word in self._question_words(q):
                df[word] = df.get(word, 0) + 1
        return df

    def _extract_keywords(self, questions: List[Dict],
                          corpus_df: Optional[Dict[str, int]] = None,
                          n_corpus: int = 0) -> List[str]:
        """
        Keywords that characterize THIS group: frequent within the group,
        rare across the REST of the corpus (the group's own questions must
        not penalize its defining word).
        """
        word_freq: Dict[str, int] = {}
        for q in questions:
            for word in self._question_words(q):
                word_freq[word] = word_freq.get(word, 0) + 1

        n_outside = max(0, n_corpus - len(questions)) if corpus_df else 0

        def score(item):
            word, freq = item
            if corpus_df and n_outside:
                df_outside = max(0, corpus_df.get(word, 0) - freq)
                idf = math.log((n_outside + 1) / (df_outside + 1))
                return (freq * idf, freq)
            return (float(freq), freq)

        ranked = sorted(word_freq.items(), key=score, reverse=True)
        return [word for word, _ in ranked[:5]]

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

        suggestion = self.suggested_threshold(results)
        if suggestion is not None:
            stats = results['metadata']['similarity_stats']
            print(f"\nTIP: No questions grouped at threshold "
                  f"{results['metadata']['similarity_threshold']}. Your most "
                  f"similar pair scored {stats['max']} — similarity scales vary "
                  f"by embedding model. Try: --threshold {suggestion}")

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
