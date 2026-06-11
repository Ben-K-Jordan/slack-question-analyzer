"""
Export analysis results as CSV or Markdown strings.

Used by both the CLI (writing files) and the API server (download endpoint).
"""

import csv
import io
from typing import Dict


def to_csv(results: Dict) -> str:
    """Flat CSV: one row per question."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
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
    return buffer.getvalue()


def to_markdown(results: Dict) -> str:
    """Readable Markdown report."""
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
    ]
    if results.get('executive_summary'):
        lines += ['## Executive Summary', '', results['executive_summary'], '']
    lines += ['## Top Question Groups', '']

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

    feedback = results.get('feature_requests', [])
    if feedback:
        lines.append(f"## Product Feedback ({len(feedback)})")
        lines.append('')
        lines.append('Feature requests routed out of the support funnel:')
        lines.append('')
        for q in feedback:
            lines.append(f"- {q['text']} _({q.get('date', 'Unknown')})_")
        lines.append('')

    return '\n'.join(lines)
