"""
Regression evaluation against a labeled fixture.

A fixture freezes one real run's questions with their CORRECT buckets and
groupings. Re-running it after every prompt, anchor, or threshold change
turns "seems better" into "measurably better" — without it, every tuning
change is a guess that may fix this run while silently breaking the last.

The topic bank is excluded on purpose: bank state differs per machine, and
the fixture measures taxonomy + clustering + prompts, not learned history.
"""

import json
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Set, FrozenSet

from .taxonomy import Taxonomy


def load_fixture(path: str) -> Dict:
    """Load and validate a fixture file."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    questions = data.get('questions')
    if not isinstance(questions, list) or not questions:
        raise ValueError('Fixture must contain a non-empty "questions" list')
    for q in questions:
        if not q.get('text') or not q.get('bucket'):
            raise ValueError(f"Every fixture question needs 'text' and 'bucket': {q}")
    return data


def _same_group_pairs(assignment: Dict[str, Optional[object]]) -> Set[FrozenSet]:
    """All unordered pairs of texts sharing a non-null group key."""
    items = [(text, key) for text, key in assignment.items() if key is not None]
    return {frozenset((a, b)) for (a, ka), (b, kb)
            in combinations(items, 2) if ka == kb}


def evaluate(analyzer, fixture: Dict) -> Dict:
    """
    Route + group the fixture questions through the real pipeline and score
    against the labels. Requires a taxonomy and a reachable embedding
    provider; uses the LLM verifier/auditor when available.
    """
    taxonomy = Taxonomy()
    if not taxonomy.enabled:
        raise ValueError('Evaluation needs taxonomy.json (routing taxonomy)')

    questions = [{
        'text': q['text'],
        'normalized_text': analyzer.extractor.normalize_question(q['text']),
        'date': q.get('date', 'Unknown'),
        'original_message': q['text'][:200],
    } for q in fixture['questions']]

    verify_on = analyzer._llm_enabled(analyzer._verify_mode)
    verifier = analyzer.labeler.verify_same_topic if verify_on else None
    auditor = analyzer.labeler.audit_group if verify_on else None

    groups = analyzer._group_with_taxonomy(
        questions, taxonomy, verifier, auditor,
        known_topics=None, report=lambda *args: None)

    predicted_bucket: Dict[str, Optional[str]] = {}
    predicted_group: Dict[str, Optional[int]] = {}
    for gi, group in enumerate(groups):
        for q in group['questions']:
            predicted_bucket[q['text']] = ('review' if q.get('needs_review')
                                           else group.get('bucket'))
            predicted_group[q['text']] = gi if group['count'] > 1 else None

    routing_mismatches: List[Dict] = []
    correct = 0
    for q in fixture['questions']:
        got = predicted_bucket.get(q['text'])
        if got == q['bucket']:
            correct += 1
        else:
            routing_mismatches.append({'text': q['text'],
                                       'expected': q['bucket'], 'got': got})

    expected_pairs = _same_group_pairs(
        {q['text']: q.get('group') for q in fixture['questions']})
    got_pairs = _same_group_pairs(predicted_group)
    true_pairs = expected_pairs & got_pairs

    return {
        'questions': len(fixture['questions']),
        'routing_correct': correct,
        'routing_accuracy': correct / len(fixture['questions']),
        'routing_mismatches': routing_mismatches,
        'pairs_expected': len(expected_pairs),
        'pairs_found': len(got_pairs),
        'pairs_correct': len(true_pairs),
        'pair_precision': (len(true_pairs) / len(got_pairs)) if got_pairs else 1.0,
        'pair_recall': (len(true_pairs) / len(expected_pairs)) if expected_pairs else 1.0,
        'missed_pairs': [sorted(p) for p in sorted(expected_pairs - got_pairs,
                                                   key=sorted)],
        'wrong_pairs': [sorted(p) for p in sorted(got_pairs - expected_pairs,
                                                  key=sorted)],
        'taxonomy_version': taxonomy.version,
        'fixture': str(Path(getattr(fixture, 'path', '') or '')),
    }


def format_report(result: Dict) -> str:
    """Human-readable evaluation report for the console."""
    lines = [
        f"Fixture: {result['questions']} questions · taxonomy v{result['taxonomy_version']}",
        f"Routing:  {result['routing_correct']}/{result['questions']} correct "
        f"({result['routing_accuracy']:.0%})",
        f"Grouping: {result['pairs_correct']}/{result['pairs_expected']} expected pairs found "
        f"(precision {result['pair_precision']:.0%}, recall {result['pair_recall']:.0%})",
    ]
    if result['routing_mismatches']:
        lines.append('\nRouting mismatches:')
        for m in result['routing_mismatches']:
            lines.append(f"  expected [{m['expected']}] got [{m['got']}]: {m['text'][:90]}")
    if result['missed_pairs']:
        lines.append('\nMissed pairs (should group, did not):')
        for a, b in result['missed_pairs']:
            lines.append(f"  - {a[:70]}\n    + {b[:70]}")
    if result['wrong_pairs']:
        lines.append('\nWrong pairs (grouped, should not):')
        for a, b in result['wrong_pairs']:
            lines.append(f"  - {a[:70]}\n    + {b[:70]}")
    if not (result['routing_mismatches'] or result['missed_pairs'] or result['wrong_pairs']):
        lines.append('\nPerfect score.')
    return '\n'.join(lines)
