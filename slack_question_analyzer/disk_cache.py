"""
Persistent JSON-value cache backed by a single file, keyed by hashed strings.

Used for embeddings (which never change for a given model+text) and LLM
outputs (deterministic at temperature 0 with a fixed seed), so repeat
analyses skip provider calls entirely.
"""

import os
import json
import logging
import hashlib
import tempfile
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class JsonDiskCache:
    """Maps arbitrary strings to JSON-serializable values, persisted to disk."""

    def __init__(self, provider: str, model: str, cache_dir: str,
                 enabled: bool = True):
        self.enabled = enabled
        self._memory = {}
        self._dirty = False

        safe_model = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in model)
        self.cache_path = Path(cache_dir) / f"{provider}_{safe_model}.json"

        if self.enabled and self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    self._memory = json.load(f)
            except (json.JSONDecodeError, OSError):
                # Corrupt or unreadable cache: start fresh rather than failing
                self._memory = {}

    @staticmethod
    def _key(text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def get(self, text: str) -> Optional[Any]:
        return self._memory.get(self._key(text))

    def set(self, text: str, value: Any):
        self._memory[self._key(text)] = value
        self._dirty = True

    def save(self):
        """Persist the cache to disk (atomic write)."""
        if not self.enabled or not self._dirty:
            return
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(dir=self.cache_path.parent, suffix='.tmp')
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(self._memory, f)
            os.replace(tmp_path, self.cache_path)
            self._dirty = False
        except OSError as e:
            # Cache persistence is best-effort; results are unaffected
            logger.warning("Could not save cache %s: %s", self.cache_path.name, e)
