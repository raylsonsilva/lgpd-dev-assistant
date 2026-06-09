from __future__ import annotations

import time
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_query(query: str) -> str:
    query = query.lower().strip()
    query = re.sub(r"\s+", " ", query)
    query = re.sub(r"[!?.,;:]+$", "", query)
    return query


@dataclass
class CacheStats:
    exact_hits: int = 0
    semantic_hits: int = 0
    misses: int = 0
    writes: int = 0

    @property
    def total(self) -> int:
        return self.exact_hits + self.semantic_hits + self.misses

    @property
    def hit_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.exact_hits + self.semantic_hits) / self.total


class ExactAndSemanticCache:
    """Cache em memória para reduzir custo e latência.

    - Exact cache: mesma pergunta normalizada.
    - Semantic cache: similaridade TF-IDF com perguntas anteriores.
    """

    def __init__(self, ttl_seconds: int = 3600, semantic_threshold: float = 0.84):
        self.ttl_seconds = ttl_seconds
        self.semantic_threshold = semantic_threshold
        self._store: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self.stats = CacheStats()

    def _is_fresh(self, ts: float) -> bool:
        return (time.time() - ts) <= self.ttl_seconds

    def get_exact(self, query: str) -> Optional[Dict[str, Any]]:
        key = normalize_query(query)
        item = self._store.get(key)
        if item and self._is_fresh(item[0]):
            self.stats.exact_hits += 1
            result = dict(item[1])
            result["cache"] = {"hit": True, "type": "exact"}
            return result
        return None

    def get_semantic(self, query: str) -> Optional[Dict[str, Any]]:
        active = [(k, v) for k, v in self._store.items() if self._is_fresh(v[0])]
        if len(active) < 2:
            return None
        keys = [k for k, _ in active]
        vectorizer = TfidfVectorizer(strip_accents="unicode", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(keys + [normalize_query(query)])
        sims = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
        best_idx = int(sims.argmax())
        best_score = float(sims[best_idx])
        if best_score >= self.semantic_threshold:
            self.stats.semantic_hits += 1
            cached = dict(active[best_idx][1][1])
            cached["cache"] = {"hit": True, "type": "semantic", "similarity": best_score, "matched_query": keys[best_idx]}
            return cached
        return None

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        exact = self.get_exact(query)
        if exact:
            return exact
        semantic = self.get_semantic(query)
        if semantic:
            return semantic
        self.stats.misses += 1
        return None

    def set(self, query: str, response: Dict[str, Any]) -> None:
        key = normalize_query(query)
        self._store[key] = (time.time(), dict(response))
        self.stats.writes += 1

    def report(self) -> Dict[str, Any]:
        return {
            "exact_hits": self.stats.exact_hits,
            "semantic_hits": self.stats.semantic_hits,
            "misses": self.stats.misses,
            "writes": self.stats.writes,
            "hit_rate": round(self.stats.hit_rate, 4),
            "ttl_seconds": self.ttl_seconds,
            "semantic_threshold": self.semantic_threshold,
        }
