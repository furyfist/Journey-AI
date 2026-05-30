"""Low-level Unsplash API client.

Responsibilities:
- Attach the Client-ID auth header required by Unsplash.
- Call the search/photos endpoint.
- Surface HTTP and network errors as ExternalAPIError so callers never
  need to know the shape of an httpx exception.
"""

import httpx

from app.common.logger import get_logger
from app.core.config import settings
from app.core.exceptions import ExternalAPIError, RateLimitError

logger = get_logger(__name__)

_SEARCH_PATH = "/search/photos"


async def search_photos(
    http: httpx.AsyncClient,
    query: str,
    per_page: int = 1,
) -> dict:
    """Return the raw Unsplash search/photos JSON for *query*.

    Args:
        http: Shared async HTTP client (injected by FastAPI lifespan).
        query: Search term sent to Unsplash.
        per_page: Number of results to request.  Defaults to 1 because the
            service layer only ever uses the first result.

    Returns:
        The full parsed JSON response dict from Unsplash.

    Raises:
        ExternalAPIError: On any HTTP or network failure.
        RateLimitError: When Unsplash returns 429.
    """
    if not settings.unsplash_access_key:
        raise ExternalAPIError("Unsplash access key is not configured")

    headers = {"Authorization": f"Client-ID {settings.unsplash_access_key}"}
    params = {"query": query, "per_page": per_page}
    url = f"{settings.unsplash_base_url}{_SEARCH_PATH}"

    try:
        resp = await http.get(url, headers=headers, params=params)
    except httpx.TimeoutException as exc:
        logger.warning("Unsplash request timed out for query=%r: %s", query, exc)
        raise ExternalAPIError(f"Unsplash request timed out: {exc}") from exc
    except httpx.RequestError as exc:
        logger.warning("Unsplash network error for query=%r: %s", query, exc)
        raise ExternalAPIError(f"Unsplash network error: {exc}") from exc

    if resp.status_code == 429:
        logger.warning("Unsplash rate limit hit for query=%r", query)
        raise RateLimitError("Unsplash rate limit reached")

    if resp.status_code == 401:
        logger.error("Unsplash rejected credentials (401)")
        raise ExternalAPIError("Unsplash: invalid credentials (check UNSPLASH_ACCESS_KEY)")

    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Unsplash HTTP error for query=%r: status=%s", query, exc.response.status_code
        )
        raise ExternalAPIError(
            f"Unsplash error: {exc.response.status_code}"
        ) from exc

    return resp.json()
