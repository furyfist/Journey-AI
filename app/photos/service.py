"""Photo service layer.

Responsibilities:
- Apply query-cleaning heuristics before hitting Unsplash.
- Check the in-memory TTL cache before making any upstream call.
- Call the client and normalize the raw response into the app's internal
  PhotoResult schema.
- Write successful results back to the cache.
- Guard against duplicate in-flight requests for the same query in a
  single event-loop cycle (dedup via an in-progress set).
- Return a safe fallback object when no result is found or the upstream
  call fails, so a missing photo never breaks a page render.
"""

import asyncio
import httpx

from app.common.logger import get_logger
from app.core.exceptions import ExternalAPIError, RateLimitError
from app.photos.cache import photo_cache
from app.photos.client import search_photos
from app.photos.schemas import PhotoResult

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# In-flight dedup guard
# Tracks queries whose Unsplash fetch is currently awaited.  Any second
# coroutine that arrives for the same query while the first is still in
# flight will wait for an asyncio.Event instead of issuing a duplicate
# upstream call.
# ---------------------------------------------------------------------------
_in_progress: dict[str, asyncio.Event] = {}
_in_progress_results: dict[str, PhotoResult] = {}


# ---------------------------------------------------------------------------
# Curated query overrides
# Swap generic destination names for search terms that reliably surface
# strong travel photography on Unsplash.
# ---------------------------------------------------------------------------
_QUERY_OVERRIDES: dict[str, str] = {
    "tokyo, japan": "Tokyo city skyline",
    "tokyo": "Tokyo city skyline",
    "shibuya": "Shibuya street Tokyo",
    "shibuya & harajuku": "Shibuya street Tokyo",
    "kyoto, japan": "Kyoto temples autumn",
    "kyoto": "Kyoto temples autumn",
    "paris, france": "Paris Eiffel Tower",
    "paris": "Paris Eiffel Tower",
    "new york, usa": "New York City skyline",
    "new york": "New York City skyline",
    "bali, indonesia": "Bali rice terraces",
    "bali": "Bali rice terraces",
    "rome, italy": "Rome Colosseum",
    "rome": "Rome Colosseum",
    "barcelona, spain": "Barcelona Sagrada Familia",
    "barcelona": "Barcelona Sagrada Familia",
    "london, uk": "London Tower Bridge",
    "london": "London Tower Bridge",
    "dubai, uae": "Dubai skyline desert",
    "dubai": "Dubai skyline desert",
    "singapore": "Singapore Gardens by the Bay",
    "bangkok, thailand": "Bangkok temples river",
    "bangkok": "Bangkok temples river",
}


def _clean_query(raw: str) -> str:
    """Return a search-optimized query for *raw* destination text."""
    normalized = raw.strip().lower()
    if normalized in _QUERY_OVERRIDES:
        return _QUERY_OVERRIDES[normalized]
    # Generic cleanup: remove trailing country suffixes that hurt image quality
    # e.g. "Osaka, Japan" → "Osaka Japan travel"
    cleaned = raw.strip()
    if "," in cleaned:
        parts = [p.strip() for p in cleaned.split(",")]
        cleaned = " ".join(parts) + " travel"
    return cleaned


def _normalize(raw_query: str, data: dict) -> PhotoResult | None:
    """Parse the first Unsplash result into a PhotoResult.

    Returns None when the response contains no usable photos.
    """
    results = data.get("results", [])
    if not results:
        return None

    photo = results[0]
    urls: dict = photo.get("urls", {})
    user: dict = photo.get("user", {})
    links: dict = photo.get("links", {})
    user_links: dict = user.get("links", {})

    image_url = urls.get("regular") or urls.get("full")
    thumb_url = urls.get("thumb") or urls.get("small")

    if not image_url:
        return None

    alt_text: str | None = photo.get("alt_description") or photo.get("description")
    photographer_name: str | None = user.get("name")
    photographer_url: str | None = user_links.get("html")
    unsplash_page_url: str | None = links.get("html")

    return PhotoResult(
        query=raw_query,
        image_url=image_url,
        thumb_url=thumb_url,
        alt_text=alt_text,
        photographer_name=photographer_name,
        photographer_url=photographer_url,
        unsplash_page_url=unsplash_page_url,
        source="unsplash",
    )


def _fallback(raw_query: str) -> PhotoResult:
    """Return a safe empty result so callers always get a usable object."""
    return PhotoResult(query=raw_query, source="fallback")


async def fetch_photo(http: httpx.AsyncClient, query: str) -> PhotoResult:
    """Return one normalized photo for *query*, or a fallback if unavailable.

    Lookup order:
    1. In-memory TTL cache (keyed by normalized query string).
    2. In-flight dedup: if another coroutine is already fetching the same
       query, wait for its result instead of issuing a duplicate request.
    3. Live Unsplash call via the client module.

    This function never raises — it logs failures and returns a fallback
    PhotoResult so that the absence of a photo never causes a 500.

    Args:
        http: Shared async HTTP client.
        query: Raw destination or search query from the caller.

    Returns:
        A PhotoResult with source="unsplash" on success, or source="fallback"
        when Unsplash is unavailable or returned no matching photos.
    """
    cache_key = query.strip().lower()

    # --- 1. Cache hit ---
    cached = photo_cache.get(query)
    if cached is not None:
        return cached

    # --- 2. In-flight dedup ---
    if cache_key in _in_progress:
        logger.debug("Photo fetch dedup: waiting for in-flight query=%r", query)
        event = _in_progress[cache_key]
        await event.wait()
        return _in_progress_results.get(cache_key, _fallback(query))

    # --- 3. Live fetch — register in-progress event ---
    event = asyncio.Event()
    _in_progress[cache_key] = event

    search_query = _clean_query(query)
    logger.debug("Fetching Unsplash photo: original=%r search=%r", query, search_query)

    try:
        data = await search_photos(http, search_query)
    except RateLimitError:
        logger.warning("Unsplash rate limit — returning fallback for query=%r", query)
        result = _fallback(query)
    except ExternalAPIError as exc:
        logger.warning("Unsplash error for query=%r: %s — returning fallback", query, exc)
        result = _fallback(query)
    else:
        normalized = _normalize(query, data)
        if normalized is None:
            logger.info("No Unsplash results for query=%r (searched %r)", query, search_query)
            result = _fallback(query)
        else:
            logger.debug("Photo fetched: query=%r url=%s", query, normalized.image_url)
            result = normalized
            photo_cache.set(query, result)   # only caches source="unsplash"

    # Signal waiting coroutines and clean up
    _in_progress_results[cache_key] = result
    event.set()
    _in_progress.pop(cache_key, None)
    _in_progress_results.pop(cache_key, None)

    return result
