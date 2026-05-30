"""Photo service layer.

Responsibilities:
- Apply query-cleaning heuristics before hitting Unsplash.
- Call the client and normalize the raw response into the app's internal
  PhotoResult schema.
- Return a safe fallback object when no result is found or the upstream
  call fails, so a missing photo never breaks a page render.
"""

import httpx

from app.common.logger import get_logger
from app.core.exceptions import ExternalAPIError, RateLimitError
from app.photos.client import search_photos
from app.photos.schemas import PhotoResult

logger = get_logger(__name__)

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

    This function never raises — it logs failures and returns a fallback
    PhotoResult so that the absence of a photo never causes a 500.

    Args:
        http: Shared async HTTP client.
        query: Raw destination or search query from the caller.

    Returns:
        A PhotoResult with source="unsplash" on success, or source="fallback"
        when Unsplash is unavailable or returned no matching photos.
    """
    search_query = _clean_query(query)
    logger.debug("Fetching Unsplash photo: original=%r search=%r", query, search_query)

    try:
        data = await search_photos(http, search_query)
    except RateLimitError:
        logger.warning("Unsplash rate limit — returning fallback for query=%r", query)
        return _fallback(query)
    except ExternalAPIError as exc:
        logger.warning("Unsplash error for query=%r: %s — returning fallback", query, exc)
        return _fallback(query)

    result = _normalize(query, data)
    if result is None:
        logger.info("No Unsplash results for query=%r (searched %r)", query, search_query)
        return _fallback(query)

    logger.debug("Photo fetched: query=%r url=%s", query, result.image_url)
    return result
