"""
Similarity analysis module using AI embeddings.
Supports Azure OpenAI, OpenAI, and local Ollama.
Groups similar questions together using semantic similarity.
"""

import os
import json
import time
import hashlib
import tempfile
from pathlib import Path
from typing import List, Dict, Literal, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv


class EmbeddingError(Exception):
    """Raised when embeddings could not be retrieved from the provider."""


class EmbeddingCache:
    """
    Persistent embedding cache backed by a JSON file.

    Embeddings never change for a given (model, text) pair, so caching them on
    disk makes repeat analyses near-instant and avoids paying for the same
    API calls twice.
    """

    def __init__(self, provider: str, model: str, cache_dir: Optional[str] = None,
                 enabled: bool = True):
        self.enabled = enabled
        self._memory: Dict[str, List[float]] = {}
        self._dirty = False

        cache_dir = cache_dir or os.getenv('EMBEDDING_CACHE_DIR', '.embedding_cache')
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

    def get(self, text: str) -> Optional[List[float]]:
        return self._memory.get(self._key(text))

    def set(self, text: str, embedding: List[float]):
        self._memory[self._key(text)] = embedding
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
            # Cache persistence is best-effort; analysis results are unaffected
            print(f"Warning: could not save embedding cache: {e}")


class SimilarityAnalyzer:
    """Analyzes question similarity using AI embeddings."""

    MAX_RETRIES = 3
    RETRY_BACKOFF_SECONDS = 1.0
    REQUEST_TIMEOUT_SECONDS = 30

    def __init__(self, provider: Literal['azure', 'openai', 'ollama'] = 'ollama',
                 use_disk_cache: bool = True, threshold: Optional[float] = None):
        """
        Initialize the similarity analyzer.

        Args:
            provider: AI provider to use ('azure', 'openai', or 'ollama')
            use_disk_cache: Persist embeddings to disk so repeat runs are fast
            threshold: Similarity threshold (0-1). Overrides the
                       SIMILARITY_THRESHOLD env variable when given.
        """
        load_dotenv()

        if provider not in ('azure', 'openai', 'ollama'):
            raise ValueError(
                f"Unknown provider '{provider}'. Expected 'azure', 'openai', or 'ollama'."
            )

        self.provider = provider
        if threshold is not None:
            if not 0.0 <= threshold <= 1.0:
                raise ValueError(f"threshold must be between 0 and 1, got {threshold}")
            self.similarity_threshold = float(threshold)
        else:
            self.similarity_threshold = self._read_threshold()

        if provider == 'azure':
            # Azure OpenAI configuration
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            if not api_key or not endpoint:
                raise EmbeddingError(
                    "Azure provider requires AZURE_OPENAI_API_KEY and "
                    "AZURE_OPENAI_ENDPOINT to be set (see 'setup' command)."
                )
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
                azure_endpoint=endpoint
            )
            self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
            self.embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
        elif provider == 'openai':
            # Standard OpenAI configuration
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise EmbeddingError(
                    "OpenAI provider requires OPENAI_API_KEY to be set "
                    "(see 'setup' command)."
                )
            self.client = OpenAI(api_key=api_key)
            self.deployment_name = None
            self.embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
        else:  # ollama
            # Local Ollama configuration
            self.client = None
            self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434').rstrip('/')
            self.embedding_model = os.getenv('OLLAMA_MODEL', 'nomic-embed-text')
            self.deployment_name = None

        cache_enabled = use_disk_cache and os.getenv('EMBEDDING_CACHE', 'on').lower() not in ('off', '0', 'false')
        self.embeddings_cache = EmbeddingCache(
            provider=provider,
            model=self.embedding_model,
            enabled=cache_enabled
        )

    @staticmethod
    def _read_threshold() -> float:
        raw = os.getenv('SIMILARITY_THRESHOLD', '0.85')
        try:
            threshold = float(raw)
        except ValueError:
            raise ValueError(f"SIMILARITY_THRESHOLD must be a number, got '{raw}'")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"SIMILARITY_THRESHOLD must be between 0 and 1, got {threshold}")
        return threshold

    def _with_retries(self, fn, description: str):
        """Run fn() with retries and exponential backoff on transient errors."""
        last_error = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                return fn()
            except Exception as e:
                last_error = e
                if attempt < self.MAX_RETRIES:
                    delay = self.RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1))
                    print(f"Warning: {description} failed (attempt {attempt}/"
                          f"{self.MAX_RETRIES}): {e}. Retrying in {delay:.0f}s...")
                    time.sleep(delay)
        raise EmbeddingError(f"{description} failed after {self.MAX_RETRIES} attempts: {last_error}") from last_error

    def _ollama_embedding(self, text: str) -> List[float]:
        """Fetch a single embedding from Ollama with timeout and retries."""
        def call():
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
                timeout=self.REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            data = response.json()
            if 'embedding' not in data or not data['embedding']:
                raise EmbeddingError(
                    f"Ollama returned no embedding (is model "
                    f"'{self.embedding_model}' pulled? Try: ollama pull {self.embedding_model})"
                )
            return data['embedding']

        return self._with_retries(call, f"Ollama embedding request ({self.ollama_url})")

    def _openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Fetch a batch of embeddings from OpenAI/Azure with retries."""
        model = self.deployment_name if self.provider == 'azure' else self.embedding_model

        def call():
            response = self.client.embeddings.create(input=texts, model=model)
            return [item.embedding for item in response.data]

        return self._with_retries(call, f"{self.provider} embeddings request")

    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats

        Raises:
            EmbeddingError: If the embedding could not be retrieved
        """
        cached = self.embeddings_cache.get(text)
        if cached is not None:
            return cached

        if self.provider == 'ollama':
            embedding = self._ollama_embedding(text)
        else:
            embedding = self._openai_embeddings([text])[0]

        self.embeddings_cache.set(text, embedding)
        self.embeddings_cache.save()
        return embedding

    def _get_ollama_embeddings_parallel(self, texts: List[str], max_workers: int = 5,
                                        on_each=None):
        """
        Get embeddings from Ollama in parallel for better performance.

        Args:
            texts: List of texts to embed
            max_workers: Number of parallel requests (default: 5)
            on_each: Optional callback invoked after each embedding completes

        Raises:
            EmbeddingError: If any embedding could not be retrieved
        """
        errors = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._ollama_embedding, text): text for text in texts}

            for future in as_completed(futures):
                text = futures[future]
                try:
                    self.embeddings_cache.set(text, future.result())
                except Exception as e:
                    errors.append((text, e))
                if on_each:
                    on_each()

        if errors:
            sample_text, sample_error = errors[0]
            raise EmbeddingError(
                f"Failed to embed {len(errors)} of {len(texts)} texts. "
                f"First failure ('{sample_text[:60]}...'): {sample_error}"
            )

    def get_embeddings_batch(self, texts: List[str], progress_callback=None) -> np.ndarray:
        """
        Get embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed
            progress_callback: Optional fn(completed, total) called as
                               embeddings are fetched

        Returns:
            2D numpy array of embeddings

        Raises:
            EmbeddingError: If embeddings could not be retrieved
        """
        if not texts:
            return np.empty((0, 0))

        # Embed each unique text only once
        unique_uncached = []
        seen = set()
        for text in texts:
            if text not in seen and self.embeddings_cache.get(text) is None:
                unique_uncached.append(text)
                seen.add(text)

        if unique_uncached:
            print(f"Fetching {len(unique_uncached)} new embeddings "
                  f"({len(texts) - len(unique_uncached)} cached)...")

        total = len(unique_uncached)
        completed = 0

        def report():
            nonlocal completed
            completed += 1
            if progress_callback:
                progress_callback(completed, total)

        if progress_callback:
            progress_callback(0, total)

        # Process in batches to avoid rate limits
        batch_size = 100 if self.provider != 'ollama' else 10  # Smaller batches for Ollama

        for i in range(0, len(unique_uncached), batch_size):
            batch = unique_uncached[i:i + batch_size]

            if self.provider == 'ollama':
                # Ollama only supports one prompt per request; parallelize for speed
                self._get_ollama_embeddings_parallel(batch, on_each=report)
            else:
                for text, embedding in zip(batch, self._openai_embeddings(batch)):
                    self.embeddings_cache.set(text, embedding)
                    report()

        self.embeddings_cache.save()

        embeddings = []
        for text in texts:
            embedding = self.embeddings_cache.get(text)
            if embedding is None:
                raise EmbeddingError(f"Missing embedding for text: '{text[:80]}'")
            embeddings.append(embedding)

        return np.array(embeddings)

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        vec1 = np.array(embedding1).reshape(1, -1)
        vec2 = np.array(embedding2).reshape(1, -1)
        return cosine_similarity(vec1, vec2)[0][0]

    @staticmethod
    def _lexical_similarity(text1: str, text2: str) -> float:
        """Token-set Jaccard similarity — a cheap, AI-free first pass."""
        tokens1, tokens2 = set(text1.split()), set(text2.split())
        if not tokens1 or not tokens2:
            return 0.0
        return len(tokens1 & tokens2) / len(tokens1 | tokens2)

    def _dedupe_questions(self, questions: List[Dict]) -> List[List[Dict]]:
        """
        Merge exact and near-duplicate questions WITHOUT any AI calls.

        Tier 1: identical normalized text.
        Tier 2: token-set Jaccard similarity >= LEXICAL_DEDUP_THRESHOLD
                (default 0.9 — strict enough that only rewordings merge).

        Returns buckets of questions; only one embedding is needed per bucket.
        """
        # Tier 1: exact duplicates
        buckets: Dict[str, List[Dict]] = {}
        order = []
        for q in questions:
            key = q['normalized_text']
            if key not in buckets:
                buckets[key] = []
                order.append(key)
            buckets[key].append(q)

        # Tier 2: lexical near-duplicates
        lexical_threshold = float(os.getenv('LEXICAL_DEDUP_THRESHOLD', '0.9'))
        canonical = []
        for key in order:
            target = None
            for ckey in canonical:
                if self._lexical_similarity(key, ckey) >= lexical_threshold:
                    target = ckey
                    break
            if target is not None:
                buckets[target].extend(buckets.pop(key))
            else:
                canonical.append(key)

        return [buckets[key] for key in canonical]

    def group_similar_questions(self, questions: List[Dict],
                                progress_callback=None, verifier=None) -> List[Dict]:
        """
        Group similar questions together.

        Exact and near-duplicate questions are merged with cheap string
        comparison first, so the AI provider is only called for genuinely
        distinct questions. When a verifier is given, group pairs whose
        similarity falls just below the threshold are double-checked by it.

        Args:
            questions: List of question dictionaries with 'text' and 'normalized_text'
            progress_callback: Optional fn(completed, total) for embedding progress
            verifier: Optional fn(texts_a, texts_b) -> Optional[bool] used to
                      decide borderline merges (e.g. an LLM yes/no check)

        Returns:
            List of question groups with representative questions
        """
        if not questions:
            return []

        print(f"Analyzing {len(questions)} questions...")

        # Tiers 1-2: merge duplicates without AI
        buckets = self._dedupe_questions(questions)
        if len(buckets) < len(questions):
            print(f"Deduplicated to {len(buckets)} distinct questions "
                  f"({len(questions) - len(buckets)} duplicates merged without AI)")

        # A single distinct question needs no embeddings at all
        if len(buckets) == 1:
            if progress_callback:
                progress_callback(0, 0)
            bucket = buckets[0]
            return [{
                'representative_question': bucket[0]['text'],
                'questions': bucket,
                'count': len(bucket),
                'avg_similarity': 1.0
            }]

        # Tier 3: semantic grouping — embed one representative per bucket
        texts = [bucket[0]['normalized_text'] for bucket in buckets]
        embeddings = self.get_embeddings_batch(texts, progress_callback=progress_callback)

        # Calculate similarity matrix between distinct questions
        similarity_matrix = cosine_similarity(embeddings)

        clusters = self._cluster_buckets(len(buckets), similarity_matrix)

        # Tier 4: LLM double-check for merges embeddings couldn't decide
        if verifier is not None and len(clusters) > 1:
            clusters = self._merge_borderline_clusters(clusters, similarity_matrix,
                                                       buckets, verifier)

        groups = [self._build_group(indices, buckets, embeddings, similarity_matrix)
                  for indices in clusters]

        # Sort groups by count (most common first)
        groups.sort(key=lambda x: x['count'], reverse=True)

        return groups

    def _cluster_buckets(self, n: int, similarity_matrix) -> List[List[int]]:
        """Greedy clustering of bucket indices by the similarity threshold."""
        clusters = []
        assigned = set()

        for i in range(n):
            if i in assigned:
                continue

            group_indices = [i]
            assigned.add(i)

            for j in range(i + 1, n):
                if j in assigned:
                    continue

                max_similarity = max(similarity_matrix[j][idx] for idx in group_indices)
                if max_similarity >= self.similarity_threshold:
                    group_indices.append(j)
                    assigned.add(j)

            clusters.append(group_indices)

        return clusters

    def _merge_borderline_clusters(self, clusters: List[List[int]], similarity_matrix,
                                   buckets: List[List[Dict]], verifier) -> List[List[int]]:
        """
        Ask the verifier about cluster pairs whose best cross-similarity falls
        just below the threshold — the zone where embeddings are unreliable.
        """
        margin = float(os.getenv('LLM_VERIFY_MARGIN', '0.03'))
        max_checks = int(os.getenv('LLM_VERIFY_MAX', '10'))

        candidates = []
        for a in range(len(clusters)):
            for b in range(a + 1, len(clusters)):
                best = max(similarity_matrix[i][j]
                           for i in clusters[a] for j in clusters[b])
                if self.similarity_threshold - margin <= best < self.similarity_threshold:
                    candidates.append((best, a, b))
        candidates.sort(reverse=True)
        candidates = candidates[:max_checks]

        if not candidates:
            return clusters

        print(f"Verifying {len(candidates)} borderline group pair(s) with the LLM...")
        parent = list(range(len(clusters)))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        merged_count = 0
        for _, a, b in candidates:
            ra, rb = find(a), find(b)
            if ra == rb:
                continue
            texts_a = [buckets[idx][0]['text'] for idx in clusters[ra][:3]]
            texts_b = [buckets[idx][0]['text'] for idx in clusters[rb][:3]]
            if verifier(texts_a, texts_b) is True:
                parent[rb] = ra
                clusters[ra] = clusters[ra] + clusters[rb]
                merged_count += 1

        if merged_count:
            print(f"LLM verification merged {merged_count} borderline group pair(s)")
        return [clusters[i] for i in range(len(clusters)) if find(i) == i]

    def _build_group(self, group_indices: List[int], buckets: List[List[Dict]],
                     embeddings, similarity_matrix) -> Dict:
        """Construct the result dict for one cluster of buckets."""
        # Expand buckets back into their member questions
        group_questions = [q for idx in group_indices for q in buckets[idx]]

        # Find the most representative bucket (closest to centroid)
        if len(group_indices) > 1:
            group_embeddings = embeddings[group_indices]
            centroid = np.mean(group_embeddings, axis=0)

            distances = [np.linalg.norm(emb - centroid) for emb in group_embeddings]
            representative_idx = group_indices[int(np.argmin(distances))]
            representative = buckets[representative_idx][0]['text']
        else:
            representative = buckets[group_indices[0]][0]['text']

        # Average pairwise similarity between the distinct questions
        if len(group_indices) > 1:
            similarities = []
            for a in range(len(group_indices)):
                for b in range(a + 1, len(group_indices)):
                    similarities.append(similarity_matrix[group_indices[a]][group_indices[b]])
            avg_sim = float(np.mean(similarities)) if similarities else 1.0
        else:
            avg_sim = 1.0

        return {
            'representative_question': representative,
            'questions': group_questions,
            'count': len(group_questions),
            'avg_similarity': avg_sim
        }
