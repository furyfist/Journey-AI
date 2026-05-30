"""Unit tests for app/photos/service.py.

Tests cover:
- Successful fetch returns a normalized PhotoResult with source="unsplash".
- Known destination queries are cleaned via curated overrides.
- Generic "City, Country" queries get a cleaned search term.
- Empty Unsplash results return a fallback PhotoResult.
- Results with no usable URL return a fallback PhotoResult.
- RateLimitError from the client returns a fallback (does not raise).
- ExternalAPIError from the client returns a fallback (does not raise).
- Cache hit returns the stored result without calling Unsplash.
- Successful fetch result is written to the cache.
- Fallback result is NOT written to the cache.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import ExternalAPIError, RateLimitError
from app.photos import service as photos_service
from app.photos.cache import photo_cache
from app.photos.schemas import PhotoResult
from tests.mocks.mock_photo_data import (
    UNSPLASH_SEARCH_RESPONSE_EMPTY,
    UNSPLASH_SEARCH_RESPONSE_NO_URL,
    UNSPLASH_SEARCH_RESPONSE_ONE_RESULT,
)


@pytest.fixture(autouse=True)
def fresh_cache():
    """Clear the module-level photo cache before every test."""
    photo_cache.clear()
    yield
    photo_cache.clear()


def _make_http_with_data(json_response: dict) -> AsyncMock:
    """Patch search_photos to return *json_response* without a real HTTP call."""
    http = AsyncMock()
    return http


# ---------------------------------------------------------------------------
# Happy path — normalization
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_photo_returns_photo_result_with_unsplash_source():
    http = AsyncMock()
    with patch(
        "app.photos.service.search_photos",
        AsyncMock(return_value=UNSPLASH_SEARCH_RESPONSE_ONE_RESULT),
    ):
        result = await photos_service.fetch_photo(http, "Tokyo")

    assert isinstance(result, PhotoResult)
    assert result.source == "unsplash"
    assert result.query == "Tokyo"


@pytest.mark.asyncio
async def test_fetch_photo_normalizes_image_url():
    http = AsyncMock()
    with patch(
        "app.photos.service.search_photos",
        AsyncMock(return_value=UNSPLASH_SEARCH_RESPONSE_ONE_RESULT),
    ):
        result = await photos_service.fetch_photo(http, "Tokyo")

    assert str(result.image_url) == "https://images.unsplash.com/photo-abc123?w=1080"
    assert str(result.thumb_url) == "https://images.unsplash.com/photo-abc123?w=200"


@pytest.mark.asyncio
async def test_fetch_photo_preserves_attribution_fields():
    http = AsyncMock()
    with patch(
        "app.photos.service.search_photos",
        AsyncMock(return_value=UNSPLASH_SEARCH_RESPONSE_ONE_RESULT),
    ):
        result = await photos_service.fetch_photo(http, "Tokyo")

    assert result.photographer_name == "Jane Photographer"
    assert "janephotographer" in str(result.photographer_url)
    assert "unsplash.com/photos/abc123" in str(result.unsplash_page_url)


@pytest.mark.asyncio
async def test_fetch_photo_uses_alt_description_as_alt_text():
    http = AsyncMock()
    with patch(
        "app.photos.service.search_photos",
        AsyncMock(return_value=UNSPLASH_SEARCH_RESPONSE_ONE_RESULT),
    ):
        result = await photos_service.fetch_photo(http, "Tokyo")

    assert result.alt_text == "Tokyo skyline at dusk with Mount Fuji in the background"


# ---------------------------------------------------------------------------
# Query cleaning
# ---------------------------------------------------------------------------


def test_clean_query_applies_override_for_known_destination():
    assert photos_service._clean_query("Tokyo, Japan") == "Tokyo city skyline"
    assert photos_service._clean_query("tokyo, japan") == "Tokyo city skyline"


def test_clean_query_applies_override_for_short_city_name():
    assert photos_service._clean_query("paris") == "Paris Eiffel Tower"


def test_clean_query_appends_travel_for_unknown_city_country_pair():
    result = photos_service._clean_query("Lisbon, Portugal")
    assert "Lisbon" in result
    assert "Portugal" in result
    assert "travel" in result


def test_clean_query_passthrough_for_generic_string():
    raw = "mountain lake sunset"
    assert photos_service._clean_query(raw) == raw


# ---------------------------------------------------------------------------
# Fallback behaviour — empty / no-URL results
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_photo_returns_fallback_when_results_empty():
    http = AsyncMock()
    with patch(
        "app.photos.service.search_photos",
        AsyncMock(return_value=UNSPLASH_SEARCH_RESPONSE_EMPTY),
    ):
        result = await photos_service.fetch_photo(http, "NonexistentDestination123")

    assert result.source == "fallback"
    assert result.image_url is None


@pytest.mark.asyncio
async def test_fetch_photo_returns_fallback_when_no_url_in_result():
    http = AsyncMock()
    with patch(
        "app.photos.service.search_photos",
        AsyncMock(return_value=UNSPLASH_SEARCH_RESPONSE_NO_URL),
    ):
        result = await photos_service.fetch_photo(http, "GhostCity")

    assert result.source == "fallback"
    assert result.image_url is None


# ---------------------------------------------------------------------------
# Fallback behaviour — upstream errors are absorbed
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_photo_returns_fallback_on_rate_limit():
    http = AsyncMock()
    with patch(
        "app.photos.service.search_photos",
        AsyncMock(side_effect=RateLimitError()),
    ):
        result = await photos_service.fetch_photo(http, "Tokyo")

    assert result.source == "fallback"


@pytest.mark.asyncio
async def test_fetch_photo_returns_fallback_on_external_api_error():
    http = AsyncMock()
    with patch(
        "app.photos.service.search_photos",
        AsyncMock(side_effect=ExternalAPIError("Unsplash is down")),
    ):
        result = await photos_service.fetch_photo(http, "Tokyo")

    assert result.source == "fallback"


@pytest.mark.asyncio
async def test_fetch_photo_fallback_preserves_original_query():
    http = AsyncMock()
    with patch(
        "app.photos.service.search_photos",
        AsyncMock(side_effect=ExternalAPIError("network error")),
    ):
        result = await photos_service.fetch_photo(http, "My Special Destination")

    assert result.query == "My Special Destination"


# ---------------------------------------------------------------------------
# Cache integration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_hit_skips_unsplash_call():
    """A cached result must be returned without touching search_photos."""
    from app.photos.schemas import PhotoResult

    stored = PhotoResult(
        query="Tokyo",
        image_url="https://images.unsplash.com/photo-cached?w=1080",
        thumb_url="https://images.unsplash.com/photo-cached?w=200",
        alt_text="Cached Tokyo",
        photographer_name="Cache Person",
        photographer_url="https://unsplash.com/@cache",
        unsplash_page_url="https://unsplash.com/photos/cached",
        source="unsplash",
    )
    photo_cache.set("Tokyo", stored)

    mock_search = AsyncMock(return_value={})
    http = AsyncMock()
    with patch("app.photos.service.search_photos", mock_search):
        result = await photos_service.fetch_photo(http, "Tokyo")

    mock_search.assert_not_awaited()
    assert result is stored


@pytest.mark.asyncio
async def test_successful_fetch_populates_cache():
    """A successful Unsplash response must be written to the cache."""
    from tests.mocks.mock_photo_data import UNSPLASH_SEARCH_RESPONSE_ONE_RESULT

    http = AsyncMock()
    with patch(
        "app.photos.service.search_photos",
        AsyncMock(return_value=UNSPLASH_SEARCH_RESPONSE_ONE_RESULT),
    ):
        result = await photos_service.fetch_photo(http, "Tokyo")

    assert result.source == "unsplash"
    cached = photo_cache.get("Tokyo")
    assert cached is not None
    assert cached.source == "unsplash"


@pytest.mark.asyncio
async def test_fallback_result_not_cached():
    """A fallback result (Unsplash unavailable) must not be written to cache."""
    http = AsyncMock()
    with patch(
        "app.photos.service.search_photos",
        AsyncMock(side_effect=ExternalAPIError("down")),
    ):
        result = await photos_service.fetch_photo(http, "Ghostville")

    assert result.source == "fallback"
    assert photo_cache.get("Ghostville") is None
