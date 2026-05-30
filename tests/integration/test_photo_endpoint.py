"""
Integration tests for GET /api/v1/photos/search.

Strategy:
- Use the shared `client` fixture from conftest.py (FastAPI TestClient with
  mocked DB and HTTP).
- Patch `app.photos.service.fetch_photo` rather than the HTTP client — this
  exercises the full router → service interface without needing a real
  Unsplash response; individual service and client behaviours are already
  covered by unit tests.
- Clear the photo cache before every test so hits from earlier runs don't
  interfere.

Scenarios covered:
1.  Successful photo → 200 with all normalized fields.
2.  Fallback (Unsplash down) → 200 with image_url=null and source=fallback.
3.  Fallback (no results) → 200 with image_url=null.
4.  Missing query param → 422.
5.  Empty query string → 422.
6.  Query too long → 422.
7.  Curated query goes through → result comes back with correct query label.
8.  Cache hit → service is only called once across two identical requests.
9.  Response body shape → all required fields are present.
10. Attribution fields preserved → photographer_name, photographer_url,
    unsplash_page_url all forwarded.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.photos.cache import photo_cache
from app.photos.schemas import PhotoResult

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

_GOOD_RESULT = PhotoResult(
    query="Tokyo, Japan",
    image_url="https://images.unsplash.com/photo-abc123?w=1080",
    thumb_url="https://images.unsplash.com/photo-abc123?w=200",
    alt_text="Tokyo skyline at dusk",
    photographer_name="Jane Photographer",
    photographer_url="https://unsplash.com/@janephotographer",
    unsplash_page_url="https://unsplash.com/photos/abc123",
    source="unsplash",
)

_FALLBACK_RESULT = PhotoResult(query="Broken City", source="fallback")


@pytest.fixture(autouse=True)
def clear_cache():
    """Isolate each test from cached state left by previous tests."""
    photo_cache.clear()
    yield
    photo_cache.clear()


# ---------------------------------------------------------------------------
# 1 — Successful photo response
# ---------------------------------------------------------------------------


def test_search_photo_returns_200_with_normalized_fields(client):
    with patch(
        "app.photos.service.fetch_photo",
        AsyncMock(return_value=_GOOD_RESULT),
    ):
        resp = client.get("/api/v1/photos/search?query=Tokyo%2C+Japan")

    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] == "unsplash"
    assert body["query"] == "Tokyo, Japan"
    assert "images.unsplash.com" in body["image_url"]
    assert body["photographer_name"] == "Jane Photographer"


# ---------------------------------------------------------------------------
# 2 — Fallback when service cannot reach Unsplash
# ---------------------------------------------------------------------------


def test_search_photo_returns_200_with_fallback_when_unsplash_down(client):
    with patch(
        "app.photos.service.fetch_photo",
        AsyncMock(return_value=_FALLBACK_RESULT),
    ):
        resp = client.get("/api/v1/photos/search?query=Broken+City")

    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] == "fallback"
    assert body["image_url"] is None


# ---------------------------------------------------------------------------
# 3 — Fallback when Unsplash returns zero results
# ---------------------------------------------------------------------------


def test_search_photo_returns_fallback_for_unknown_destination(client):
    no_results = PhotoResult(query="XYZNonexistent999", source="fallback")
    with patch(
        "app.photos.service.fetch_photo",
        AsyncMock(return_value=no_results),
    ):
        resp = client.get("/api/v1/photos/search?query=XYZNonexistent999")

    assert resp.status_code == 200
    assert resp.json()["source"] == "fallback"
    assert resp.json()["image_url"] is None


# ---------------------------------------------------------------------------
# 4-6 — Input validation
# ---------------------------------------------------------------------------


def test_search_photo_missing_query_returns_422(client):
    resp = client.get("/api/v1/photos/search")
    assert resp.status_code == 422


def test_search_photo_empty_query_returns_422(client):
    resp = client.get("/api/v1/photos/search?query=")
    assert resp.status_code == 422


def test_search_photo_query_too_long_returns_422(client):
    long_query = "A" * 201
    resp = client.get(f"/api/v1/photos/search?query={long_query}")
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 7 — Curated query goes through correctly
# ---------------------------------------------------------------------------


def test_search_photo_curated_destination_returns_correct_query_label(client):
    """The response query label must match the *original* user query, not the
    cleaned search term sent to Unsplash."""
    tokyo_result = PhotoResult(
        query="Tokyo",
        image_url="https://images.unsplash.com/photo-tokyo?w=1080",
        thumb_url="https://images.unsplash.com/photo-tokyo?w=200",
        alt_text="Tokyo city",
        photographer_name="Taro",
        photographer_url="https://unsplash.com/@taro",
        unsplash_page_url="https://unsplash.com/photos/tokyo",
        source="unsplash",
    )
    with patch(
        "app.photos.service.fetch_photo",
        AsyncMock(return_value=tokyo_result),
    ):
        resp = client.get("/api/v1/photos/search?query=Tokyo")

    assert resp.status_code == 200
    assert resp.json()["query"] == "Tokyo"
    assert resp.json()["source"] == "unsplash"


# ---------------------------------------------------------------------------
# 8 — Cache hit means service is called only once for identical requests
# ---------------------------------------------------------------------------


def test_second_request_for_same_query_uses_cache(client):
    """After a successful first call the cache should serve subsequent
    requests for the same query without hitting search_photos again."""
    from tests.mocks.mock_photo_data import UNSPLASH_SEARCH_RESPONSE_ONE_RESULT

    mock_search = AsyncMock(return_value=UNSPLASH_SEARCH_RESPONSE_ONE_RESULT)

    with patch("app.photos.service.search_photos", mock_search):
        resp1 = client.get("/api/v1/photos/search?query=Tokyo%2C+Japan")
        resp2 = client.get("/api/v1/photos/search?query=Tokyo%2C+Japan")

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    # The real cache inside fetch_photo should have served the second request,
    # so search_photos (the actual Unsplash HTTP call) is called only once.
    mock_search.assert_awaited_once()


# ---------------------------------------------------------------------------
# 9 — Response body shape
# ---------------------------------------------------------------------------


def test_search_photo_response_contains_all_required_fields(client):
    with patch(
        "app.photos.service.fetch_photo",
        AsyncMock(return_value=_GOOD_RESULT),
    ):
        resp = client.get("/api/v1/photos/search?query=Tokyo%2C+Japan")

    body = resp.json()
    required_keys = {
        "query",
        "image_url",
        "thumb_url",
        "alt_text",
        "photographer_name",
        "photographer_url",
        "unsplash_page_url",
        "source",
    }
    assert required_keys.issubset(body.keys()), (
        f"Missing keys: {required_keys - body.keys()}"
    )


# ---------------------------------------------------------------------------
# 10 — Attribution fields forwarded intact
# ---------------------------------------------------------------------------


def test_search_photo_attribution_fields_preserved(client):
    with patch(
        "app.photos.service.fetch_photo",
        AsyncMock(return_value=_GOOD_RESULT),
    ):
        resp = client.get("/api/v1/photos/search?query=Tokyo%2C+Japan")

    body = resp.json()
    assert body["photographer_name"] == "Jane Photographer"
    assert "janephotographer" in body["photographer_url"]
    assert "unsplash.com/photos/abc123" in body["unsplash_page_url"]


# ---------------------------------------------------------------------------
# 11 — Fallback response shape is also complete
# ---------------------------------------------------------------------------


def test_fallback_response_shape_is_complete(client):
    """Even the fallback must contain all fields (most will be null)."""
    with patch(
        "app.photos.service.fetch_photo",
        AsyncMock(return_value=_FALLBACK_RESULT),
    ):
        resp = client.get("/api/v1/photos/search?query=Broken+City")

    body = resp.json()
    assert body["source"] == "fallback"
    assert body["query"] == "Broken City"
    assert body["image_url"] is None
    assert body["thumb_url"] is None
    assert body["alt_text"] is None
    assert body["photographer_name"] is None
    assert body["photographer_url"] is None
    assert body["unsplash_page_url"] is None
