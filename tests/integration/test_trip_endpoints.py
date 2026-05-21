"""
Integration tests for trip CRUD endpoints.
Groq and Supabase are mocked — only FastAPI routing and service logic are exercised.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock


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


def _make_db_mock(trip_data: dict | None = None):
    db = MagicMock()

    insert_mock = AsyncMock(return_value=MagicMock(data=[trip_data or SAMPLE_TRIP]))
    db.table.return_value.insert.return_value.execute = insert_mock

    select_mock = AsyncMock(return_value=MagicMock(data=[trip_data or SAMPLE_TRIP]))
    db.table.return_value.select.return_value.eq.return_value.single.return_value.execute = select_mock
    db.table.return_value.select.return_value.limit.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[])
    )
    db.table.return_value.select.return_value.order.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[trip_data or SAMPLE_TRIP])
    )
    db.table.return_value.delete.return_value.eq.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[])
    )

    # itinerary join used by fetch_trip_detail
    itinerary_mock = AsyncMock(return_value=MagicMock(data=[]))
    db.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute = itinerary_mock

    return db


def test_create_trip(client, mock_http):
    from app.main import app

    app.state.db = _make_db_mock()
    app.state.http = mock_http

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
    data = resp.json()
    assert data["destination"] == "Tokyo"
    assert data["status"] == "pending"


def test_list_trips(client, mock_http):
    from app.main import app

    app.state.db = _make_db_mock()
    app.state.http = mock_http

    resp = client.get("/api/v1/trips")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_delete_trip(client, mock_http):
    from app.main import app

    app.state.db = _make_db_mock()
    app.state.http = mock_http

    resp = client.delete("/api/v1/trips/00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 204
