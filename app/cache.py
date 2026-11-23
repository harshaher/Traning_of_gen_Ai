"""
cache.py - Lightweight In-Memory Response Cache for ShellSathi (S1)

Provides:
  - Thread-safe in-memory LRU response caching with Time-To-Live (TTL) expiration
  - Query normalization for consistent key generation across whitespace and casing
  - Inclusion of retrieval configuration (top_k, mode) in cache keys
  - Cache invalidation mechanism on dataset and document updates to prevent stale answers
  - Detailed cache hit/miss logging

Note:
  This in-memory cache resets upon application restart and is scoped to a single process.
  It is not distributed across separate worker processes.
"""

import logging
import os
import re
import threading
import time
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("shellsathi.cache")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

DEFAULT_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
DEFAULT_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "256"))


class ResponseCache:
    """
    Thread-safe in-memory cache with TTL expiration and LRU-style eviction.
    """

    def __init__(
        self,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        max_size: int = DEFAULT_MAX_SIZE,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.Lock()

    @staticmethod
    def normalize_query(query: str) -> str:
        """
        Normalize query string:
          - lowercase
          - trim leading and trailing whitespace
          - collapse multiple internal whitespace characters to a single space
          - remove trailing punctuation marks (?, ., !) for equivalent matching
        """
        if not query:
            return ""
        q = query.strip().lower()
        q = re.sub(r"\s+", " ", q)
        q = re.sub(r"[?!.]+$", "", q).strip()
        return q

    def build_key(self, query: str, **kwargs: Any) -> str:
        """Construct deterministic cache key combining normalized query and retrieval options."""
        norm_q = self.normalize_query(query)
        sorted_params = sorted((k, str(v)) for k, v in kwargs.items())
        params_str = ";".join(f"{k}={v}" for k, v in sorted_params)
        return f"q={norm_q}|{params_str}"

    def get(self, query: str, **kwargs: Any) -> Optional[Any]:
        """
        Retrieve cached value for a query if present and not expired.
        Logs cache hit or miss.
        """
        key = self.build_key(query, **kwargs)
        now = time.time()

        with self._lock:
            if key in self._cache:
                value, expire_at = self._cache[key]
                if now < expire_at:
                    ttl_remaining = round(expire_at - now, 1)
                    logger.info(f"cache_status=HIT key='{key}' ttl_remaining_sec={ttl_remaining}")
                    return value
                else:
                    del self._cache[key]

        logger.info(f"cache_status=MISS key='{key}'")
        return None

    def set(self, query: str, value: Any, **kwargs: Any) -> None:
        """Store a response in cache with configured TTL, evicting oldest if max size reached."""
        key = self.build_key(query, **kwargs)
        expire_at = time.time() + self.ttl_seconds

        with self._lock:
            if len(self._cache) >= self.max_size and key not in self._cache:
                first_key = next(iter(self._cache))
                del self._cache[first_key]

            self._cache[key] = (value, expire_at)
            logger.info(f"cache_status=STORE key='{key}' ttl_sec={self.ttl_seconds}")

    def invalidate(self) -> int:
        """Clear all cached responses (e.g. after document ingestion or updates)."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"cache_status=INVALIDATED entries_cleared={count}")
            return count

    def size(self) -> int:
        """Return the current number of valid (unexpired) entries in cache."""
        now = time.time()
        with self._lock:
            return sum(1 for _, exp in self._cache.values() if now < exp)


response_cache = ResponseCache()
