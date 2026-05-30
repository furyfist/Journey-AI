"""Unit tests for app/photos/service.py.

Tests cover:
- Successful fetch returns a normalized PhotoResult with source="unsplash".
- Known destination queries are cleaned via curated overrides.
- Generic "City, Country" queries get a cleaned search term.
- Empty Unsplash results return a fallback PhotoResult.
- Results with no usable URL return a fallback PhotoResult.
- RateLimitError from the client returns a fallback (does not raise).
- ExternalAPIError from the client returns a fallback (does not raise).
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import ExternalAPIError, RateLimitError
from app.photos import service as photos_service
from app.photos.schemas import PhotoResult
from tests.mocks.mock_photo_data import (
    UNSPLASH_SEARCH_RESPONSE_EMPTY,
    UNSPLASH_SEARCH_RESPONSE_NO_URL,
    UNSPLASH_SEARCH_RESPONSE_ONE_RESULT,
)


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
