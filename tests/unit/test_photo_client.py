"""Unit tests for app/photos/client.py.

Tests cover:
- Successful photo search returns raw JSON.
- Missing access key raises ExternalAPIError.
- 429 response raises RateLimitError.
- 401 response raises ExternalAPIError with a credentials message.
- Non-200 HTTP status raises ExternalAPIError.
- Timeout raises ExternalAPIError.
- Generic network error raises ExternalAPIError.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.exceptions import ExternalAPIError, RateLimitError
from app.photos import client as photos_client
from tests.mocks.mock_photo_data import UNSPLASH_SEARCH_RESPONSE_ONE_RESULT


def _make_http(json_response: dict, status_code: int = 200) -> AsyncMock:
    """Return a minimal mock httpx.AsyncClient for the photos client."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_response
    resp.raise_for_status = MagicMock()
    http = AsyncMock()
    http.get = AsyncMock(return_value=resp)
    return http


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_photos_returns_raw_json():
    http = _make_http(UNSPLASH_SEARCH_RESPONSE_ONE_RESULT)
    with patch.object(photos_client.settings, "unsplash_access_key", "test-key"):
        result = await photos_client.search_photos(http, "Tokyo skyline")

    assert result["results"][0]["id"] == "abc123"
    http.get.assert_awaited_once()
    call_kwargs = http.get.call_args
    assert "Client-ID test-key" in call_kwargs.kwargs["headers"]["Authorization"]


@pytest.mark.asyncio
async def test_search_photos_sends_correct_params():
    http = _make_http(UNSPLASH_SEARCH_RESPONSE_ONE_RESULT)
    with patch.object(photos_client.settings, "unsplash_access_key", "test-key"):
        await photos_client.search_photos(http, "Paris Eiffel Tower", per_page=3)

    params = http.get.call_args.kwargs["params"]
    assert params["query"] == "Paris Eiffel Tower"
    assert params["per_page"] == 3


# ---------------------------------------------------------------------------
# Missing credentials
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_photos_raises_when_no_access_key():
    http = _make_http({})
    with patch.object(photos_client.settings, "unsplash_access_key", ""):
        with pytest.raises(ExternalAPIError, match="access key"):
            await photos_client.search_photos(http, "Tokyo")


# ---------------------------------------------------------------------------
# HTTP error surfaces
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_photos_raises_rate_limit_error_on_429():
    http = _make_http({}, status_code=429)
    with patch.object(photos_client.settings, "unsplash_access_key", "test-key"):
        with pytest.raises(RateLimitError):
            await photos_client.search_photos(http, "Tokyo")


@pytest.mark.asyncio
async def test_search_photos_raises_external_api_error_on_401():
    http = _make_http({}, status_code=401)
    with patch.object(photos_client.settings, "unsplash_access_key", "bad-key"):
        with pytest.raises(ExternalAPIError, match="credentials"):
            await photos_client.search_photos(http, "Tokyo")


@pytest.mark.asyncio
async def test_search_photos_raises_external_api_error_on_500():
    resp = MagicMock()
    resp.status_code = 500
    resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=MagicMock(status_code=500)
    )
    http = AsyncMock()
    http.get = AsyncMock(return_value=resp)

    with patch.object(photos_client.settings, "unsplash_access_key", "test-key"):
        with pytest.raises(ExternalAPIError, match="500"):
            await photos_client.search_photos(http, "Tokyo")


# ---------------------------------------------------------------------------
# Network-level failures
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_photos_raises_on_timeout():
    http = AsyncMock()
    http.get = AsyncMock(side_effect=httpx.TimeoutException("timed out"))

    with patch.object(photos_client.settings, "unsplash_access_key", "test-key"):
        with pytest.raises(ExternalAPIError, match="timed out"):
            await photos_client.search_photos(http, "Tokyo")


@pytest.mark.asyncio
async def test_search_photos_raises_on_network_error():
    http = AsyncMock()
    http.get = AsyncMock(side_effect=httpx.ConnectError("connection refused"))

    with patch.object(photos_client.settings, "unsplash_access_key", "test-key"):
        with pytest.raises(ExternalAPIError, match="network error"):
            await photos_client.search_photos(http, "Tokyo")
