"""Lightweight in-memory TTL cache for photo results.

Design notes:
- Process-scoped dict — no external dependency, no Redis, no setup.
- Cache key is the *normalized* query (stripped, lowercased) so that
  "Tokyo" and "tokyo " map to the same entry.
- TTL defaults to 12 hours; fallback results are never cached so a
  transient Unsplash outage doesn't poison the cache for the full TTL.
- Thread safety: CPython's GIL makes single dict reads/writes atomic at
  the bytecode level; this is sufficient for an async server where
  coroutines yield at I/O boundaries, not mid-dict-mutation.
"""

import time
from dataclasses import dataclass, field
from typing import ClassVar

from app.common.logger import get_logger
from app.photos.schemas import PhotoResult

logger = get_logger(__name__)

# Default TTL: 12 hours (seconds)
DEFAULT_TTL_SECONDS: int = 12 * 60 * 60


@dataclass
class _CacheEntry:
    result: PhotoResult
    expires_at: float  # unix timestamp


class PhotoCache:
    """TTL-keyed in-memory store for PhotoResult objects.

    Usage::

        cache = PhotoCache(ttl_seconds=43200)
        cached = cache.get("Tokyo, Japan")
        if cached is None:
            result = await fetch_from_unsplash(...)
            cache.set("Tokyo, Japan", result)
    """

    # Class-level singleton store — shared across all instances of this class.
    _store: ClassVar[dict[str, _CacheEntry]] = {}

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self.ttl_seconds = ttl_seconds

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, raw_query: str) -> PhotoResult | None:
        """Return a cached PhotoResult for *raw_query*, or None if absent/expired."""
        key = self._key(raw_query)
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.monotonic() > entry.expires_at:
            del self._store[key]
            logger.debug("Photo cache expired: key=%r", key)
            return None
        logger.debug("Photo cache hit: key=%r", key)
        return entry.result

    def set(self, raw_query: str, result: PhotoResult) -> None:
        """Store *result* under *raw_query* with the configured TTL.

        Fallback results (source='fallback') are intentionally not cached
        so that a temporary Unsplash outage does not block photos for the
        full TTL window.
        """
        if result.source == "fallback":
            logger.debug("Photo cache skip (fallback): query=%r", raw_query)
            return
        key = self._key(raw_query)
        self._store[key] = _CacheEntry(
            result=result,
            expires_at=time.monotonic() + self.ttl_seconds,
        )
        logger.debug("Photo cache set: key=%r ttl=%ds", key, self.ttl_seconds)

    def clear(self) -> None:
        """Evict all entries. Useful in tests."""
        self._store.clear()

    def size(self) -> int:
        """Return the number of non-expired entries currently stored."""
        now = time.monotonic()
        return sum(1 for e in self._store.values() if e.expires_at > now)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _key(raw_query: str) -> str:
        return raw_query.strip().lower()


# Module-level singleton used by the service layer.
photo_cache = PhotoCache()
