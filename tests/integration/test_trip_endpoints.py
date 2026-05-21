"""
Integration tests for Trip CRUD endpoints.
Supabase and Groq are mocked — only FastAPI routing + service logic are exercised.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

SAMPLE_TRIP = {
    "id": "00000000-0000-0000-0000-000000000001",
    "prompt": "5-day trip to Tokyo, budget traveler who loves street food",
    "destination": "Tokyo",
    "title": "Trip to Tokyo",
    "summary": None,
    "persona": None,
    "status": "pending",
    "total_days": 5,
    "budget": "budget",
    "travel_dates": None,
    "created_at": "2026-01-01T00:00:00+00:00",
    "updated_at": "2026-01-01T00:00:00+00:00",
}


def _wire_db(mock_db: MagicMock, trip: dict = SAMPLE_TRIP) -> None:
    """Configure a mock_db so every repository call returns predictable data."""
    tb = mock_db.table.return_value

    # INSERT
    tb.insert.return_value.execute = AsyncMock(return_value=MagicMock(data=[trip]))

    # SELECT * list
    tb.select.return_value.order.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[trip])
    )
    tb.select.return_value.eq.return_value.order.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[trip])
    )

    # SELECT single trip
    tb.select.return_value.eq.return_value.single.return_value.execute = AsyncMock(
        return_value=MagicMock(data=trip)
    )

    # SELECT active itinerary join (returns empty — no itinerary yet)
    tb.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[])
    )

    # Health check probe
    tb.select.return_value.limit.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[])
    )

    # DELETE
    tb.delete.return_value.eq.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[])
    )


# ---------------------------------------------------------------------------
# POST /api/v1/trips
# ---------------------------------------------------------------------------

def test_create_trip_returns_201(client, mock_db):
    _wire_db(mock_db)
    resp = client.post(
        "/api/v1/trips",
        json={
            "prompt": "5-day trip to Tokyo, budget traveler who loves street food",
            "destination": "Tokyo",
            "total_days": 5,
            "budget": "budget",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["destination"] == "Tokyo"
    assert body["status"] == "pending"
    assert body["total_days"] == 5


def test_create_trip_infers_unknown_destination(client, mock_db):
    """When no destination is given the service uses 'Unknown' as placeholder."""
    no_dest = {**SAMPLE_TRIP, "destination": "Unknown", "title": "Trip to Unknown"}
    _wire_db(mock_db, trip=no_dest)
    resp = client.post(
        "/api/v1/trips",
        json={"prompt": "I want to go somewhere really cool for a week"},
    )
    assert resp.status_code == 201
    assert resp.json()["destination"] == "Unknown"


def test_create_trip_rejects_short_prompt(client, mock_db):
    resp = client.post("/api/v1/trips", json={"prompt": "short"})
    assert resp.status_code == 422


def test_create_trip_rejects_days_over_limit(client, mock_db):
    resp = client.post(
        "/api/v1/trips",
        json={"prompt": "Long trip prompt that is definitely long enough", "total_days": 31},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/trips
# ---------------------------------------------------------------------------

def test_list_trips_returns_list(client, mock_db):
    _wire_db(mock_db)
    resp = client.get("/api/v1/trips")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert resp.json()[0]["destination"] == "Tokyo"


# ---------------------------------------------------------------------------
# GET /api/v1/trips/{trip_id}
# ---------------------------------------------------------------------------

def test_get_trip_returns_detail(client, mock_db):
    _wire_db(mock_db)
    resp = client.get("/api/v1/trips/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "00000000-0000-0000-0000-000000000001"
    assert body["itinerary"] is None       # no itinerary saved yet
    assert body["conflicts"] == []


def test_get_trip_not_found_returns_404(client, mock_db):
    """When Supabase returns no data for the ID, we expect 404."""
    mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute = (
        AsyncMock(return_value=MagicMock(data=None))
    )
    resp = client.get("/api/v1/trips/00000000-0000-0000-0000-000000000099")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/v1/trips/{trip_id}
# ---------------------------------------------------------------------------

def test_delete_trip_returns_204(client, mock_db):
    _wire_db(mock_db)
    resp = client.delete("/api/v1/trips/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 204
