"""
Persistent topic bank: the analyzer learns across analyses.

Every analysis deposits its question groups here (topic, summary, and a
centroid embedding). Future analyses match new groups against the bank, so
recurring topics keep their established names (stable labels week over week),
skip redundant LLM labeling, and accumulate history ("seen in N analyses").
"""

import os
import json
import time
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class TopicBank:
    """JSON-backed store of known topics with centroid matching."""

    def __init__(self, path: Optional[str] = None, enabled: Optional[bool] = None):
        if enabled is None:
            enabled = os.getenv('TOPIC_BANK', 'on').lower() not in ('off', '0', 'false')
        self.enabled = enabled
        self.path = Path(path or os.getenv('TOPIC_BANK_PATH', 'topic_bank.json'))
        self.entries: List[Dict] = []

        if self.enabled and self.path.exists():
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.entries = json.load(f)
            except (json.JSONDecodeError, OSError):
                logger.warning("Topic bank at %s is unreadable; starting fresh", self.path)
                self.entries = []

    @staticmethod
    def _unit(vector) -> Optional[np.ndarray]:
        v = np.asarray(vector, dtype=float)
        norm = np.linalg.norm(v)
        return v / norm if norm else None

    def match(self, centroid, threshold: float) -> Optional[Dict]:
        """Best bank entry whose centroid similarity clears the threshold."""
        if not self.enabled or not self.entries or centroid is None:
            return None
        c = self._unit(centroid)
        if c is None:
            return None

        best, best_sim = None, threshold
        for entry in self.entries:
            v = self._unit(entry['centroid'])
            if v is None or v.shape != c.shape:
                continue  # embedding model changed; old entries can't match
            sim = float(c @ v)
            if sim >= best_sim:
                best, best_sim = entry, sim
        return best

    def record(self, group: Dict, centroid, matched: Optional[Dict] = None) -> Optional[Dict]:
        """
        Update the matched entry with this group's occurrence, or add a new
        entry. Established topic names are kept (that's the point: stability).
        """
        if not self.enabled or centroid is None:
            return None
        today = time.strftime('%Y-%m-%d')

        if matched is not None:
            old_n = matched.get('question_count', 1)
            blended = (np.asarray(matched['centroid'], dtype=float) * old_n
                       + np.asarray(centroid, dtype=float) * group['count'])
            unit = self._unit(blended)
            if unit is not None:
                matched['centroid'] = [round(float(x), 6) for x in unit]
            matched['question_count'] = old_n + group['count']
            matched['analysis_count'] = matched.get('analysis_count', 1) + 1
            matched['last_seen'] = today
            return matched

        entry = {
            'topic': group.get('topic'),
            'summary': group.get('summary'),
            'representative_question': group['representative_question'],
            'keywords': group.get('keywords', []),
            'centroid': [round(float(x), 6) for x in centroid],
            'question_count': group['count'],
            'analysis_count': 1,
            'first_seen': today,
            'last_seen': today,
        }
        self.entries.append(entry)
        return entry

    def save(self):
        """Persist the bank (atomic write; best-effort)."""
        if not self.enabled:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(dir=self.path.parent, suffix='.tmp')
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, ensure_ascii=False)
            os.replace(tmp_path, self.path)
        except OSError as e:
            logger.warning("Could not save topic bank: %s", e)
