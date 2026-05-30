"""Unit tests for app/photos/cache.py.

Tests cover:
- Cache miss returns None.
- Cache hit returns the stored PhotoResult.
- Cache normalizes the key (strips, lowercases).
- Expired entries are evicted on get and return None.
- Fallback results are not stored.
- clear() empties the store.
- size() counts only non-expired entries.
"""

import time

import pytest

from app.photos.cache import PhotoCache, _CacheEntry
from app.photos.schemas import PhotoResult


def _make_result(query: str = "Tokyo", source: str = "unsplash") -> PhotoResult:
    if source == "unsplash":
        return PhotoResult(
            query=query,
            image_url="https://images.unsplash.com/photo-abc?w=1080",
            thumb_url="https://images.unsplash.com/photo-abc?w=200",
            alt_text="Tokyo skyline",
            photographer_name="Jane",
            photographer_url="https://unsplash.com/@jane",
            unsplash_page_url="https://unsplash.com/photos/abc",
            source="unsplash",
        )
    return PhotoResult(query=query, source="fallback")


@pytest.fixture(autouse=True)
def fresh_cache(monkeypatch):
    """Give each test a fresh cache store so tests don't bleed into each other."""
    monkeypatch.setattr("app.photos.cache.PhotoCache._store", {})
    yield


# ---------------------------------------------------------------------------
# Basic get / set
# ---------------------------------------------------------------------------


def test_cache_miss_returns_none():
    cache = PhotoCache()
    assert cache.get("unknown destination") is None


def test_cache_hit_returns_stored_result():
    cache = PhotoCache()
    result = _make_result("Tokyo")
    cache.set("Tokyo", result)
    assert cache.get("Tokyo") is result


def test_cache_normalizes_key_on_set_and_get():
    cache = PhotoCache()
    result = _make_result("Tokyo")
    cache.set("  Tokyo  ", result)  # extra whitespace on set
    assert cache.get("tokyo") is result  # lowercase on get
    assert cache.get("TOKYO") is result  # uppercase on get


# ---------------------------------------------------------------------------
# TTL / expiry
# ---------------------------------------------------------------------------


def test_expired_entry_returns_none(monkeypatch):
    cache = PhotoCache(ttl_seconds=1)
    result = _make_result("Paris")
    cache.set("Paris", result)

    # Manually backdate the expiry so the entry appears expired
    key = "paris"
    cache._store[key] = _CacheEntry(result=result, expires_at=time.monotonic() - 1)

    assert cache.get("Paris") is None


def test_non_expired_entry_is_still_returned():
    cache = PhotoCache(ttl_seconds=3600)
    result = _make_result("London")
    cache.set("London", result)
    assert cache.get("London") is result


# ---------------------------------------------------------------------------
# Fallback not cached
# ---------------------------------------------------------------------------


def test_fallback_result_is_not_stored():
    cache = PhotoCache()
    fallback = _make_result("Nowhere", source="fallback")
    cache.set("Nowhere", fallback)
    assert cache.get("Nowhere") is None


def test_unsplash_result_is_stored():
    cache = PhotoCache()
    result = _make_result("Bali", source="unsplash")
    cache.set("Bali", result)
    assert cache.get("Bali") is result


# ---------------------------------------------------------------------------
# clear() and size()
# ---------------------------------------------------------------------------


def test_clear_empties_all_entries():
    cache = PhotoCache()
    cache.set("Tokyo", _make_result("Tokyo"))
    cache.set("Paris", _make_result("Paris"))
    assert cache.size() == 2
    cache.clear()
    assert cache.size() == 0
    assert cache.get("Tokyo") is None


def test_size_excludes_expired_entries(monkeypatch):
    cache = PhotoCache(ttl_seconds=3600)
    result_live = _make_result("Tokyo")
    result_dead = _make_result("Paris")
    cache.set("Tokyo", result_live)
    cache.set("Paris", result_dead)

    # Expire the Paris entry manually
    cache._store["paris"] = _CacheEntry(result=result_dead, expires_at=time.monotonic() - 1)

    assert cache.size() == 1  # only Tokyo is alive
