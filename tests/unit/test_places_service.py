from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.constants import OSM_TAG_GROUPS
from app.places import service
from app.places.client import _build_overpass_query
from app.places.schemas import PlaceResult, PlacesResponse
from app.core.exceptions import ExternalAPIError
from tests.mocks.mock_places_data import OVERPASS_EMPTY_RESPONSE, OVERPASS_RESPONSE


def _make_http(json_response: dict) -> AsyncMock:
    resp = MagicMock()
    resp.json.return_value = json_response
    resp.raise_for_status = MagicMock()
    http = AsyncMock()
    http.post = AsyncMock(return_value=resp)
    return http


# ---------------------------------------------------------------------------
# Overpass QL builder
# ---------------------------------------------------------------------------

def test_ql_builder_contains_radius_and_coords():
    ql = _build_overpass_query(35.67, 139.65, "food", 1000)
    assert "1000,35.67,139.65" in ql


def test_ql_builder_contains_all_tag_filters_for_category():
    ql = _build_overpass_query(35.67, 139.65, "food", 500)
    for tag in OSM_TAG_GROUPS["food"]:
        # Strip the surrounding `node[...]` wrapper to check the filter string
        core = tag.split("(")[0]
        assert core in ql


def test_ql_builder_output_format():
    ql = _build_overpass_query(0.0, 0.0, "nature", 2000)
    assert ql.startswith("[out:json]")
    assert "out body;" in ql


def test_ql_builder_unknown_category_raises():
    with pytest.raises(ExternalAPIError, match="Unknown place category"):
        _build_overpass_query(0.0, 0.0, "nonexistent", 500)


# ---------------------------------------------------------------------------
# Node transform
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fetch_places_returns_response_model():
    http = _make_http(OVERPASS_RESPONSE)
    result = await service.fetch_places(http, 35.67, 139.65, "food", 1000)

    assert isinstance(result, PlacesResponse)
    assert result.category == "food"
    assert result.radius_m == 1000
    assert result.lat == 35.67
    assert result.lon == 139.65


@pytest.mark.asyncio
async def test_unnamed_nodes_filtered_out():
    http = _make_http(OVERPASS_RESPONSE)
    result = await service.fetch_places(http, 35.67, 139.65, "food", 1000)
    # Fixture has 3 nodes; one has no "name" tag — only 2 should appear
    assert len(result.places) == 2
    for place in result.places:
        assert place.name != ""


@pytest.mark.asyncio
async def test_place_result_fields():
    http = _make_http(OVERPASS_RESPONSE)
    result = await service.fetch_places(http, 35.67, 139.65, "food", 1000)
    place = result.places[0]

    assert isinstance(place, PlaceResult)
    assert place.osm_id == 123456
    assert place.name == "Ramen Ichiran"
    assert place.lat == 35.6812
    assert place.lon == 139.7671
    assert place.category == "food"
    assert place.tags.get("amenity") == "restaurant"
    assert "name" not in place.tags


@pytest.mark.asyncio
async def test_empty_overpass_result_returns_empty_list():
    http = _make_http(OVERPASS_EMPTY_RESPONSE)
    result = await service.fetch_places(http, 35.67, 139.65, "nature", 5000)

    assert isinstance(result, PlacesResponse)
    assert result.places == []
