"""
Unit tests for app/trips/schemas.py.
Pure Pydantic validation — no I/O, no mocks needed.
"""
import pytest
from pydantic import ValidationError

from app.trips.schemas import TripCreate, TripDetail, TripListItem, TripResponse

# ---------------------------------------------------------------------------
# TripCreate
# ---------------------------------------------------------------------------

class TestTripCreate:
    def test_minimal_valid(self):
        t = TripCreate(prompt="I want to visit Tokyo for 5 days and eat street food")
        assert t.destination is None
        assert t.budget is None
        assert t.total_days is None

    def test_full_valid(self):
        t = TripCreate(
            prompt="5-day Tokyo trip, budget, loves street food",
            destination="Tokyo",
            budget="budget",
            start_date="2026-07-01",
            end_date="2026-07-05",
            total_days=5,
        )
        assert t.destination == "Tokyo"
        assert t.total_days == 5

    def test_prompt_too_short(self):
        with pytest.raises(ValidationError) as exc_info:
            TripCreate(prompt="short")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("prompt",) for e in errors)

    def test_prompt_at_minimum_length(self):
        # Exactly 10 characters — should pass
        t = TripCreate(prompt="1234567890")
        assert len(t.prompt) == 10

    def test_prompt_too_long(self):
        with pytest.raises(ValidationError):
            TripCreate(prompt="x" * 2001)

    def test_total_days_zero_rejected(self):
        with pytest.raises(ValidationError):
            TripCreate(
                prompt="Valid prompt that is long enough to pass validation",
                total_days=0,
            )

    def test_total_days_over_limit_rejected(self):
        with pytest.raises(ValidationError):
            TripCreate(
                prompt="Valid prompt that is long enough to pass validation",
                total_days=31,
            )

    def test_total_days_at_max(self):
        t = TripCreate(
            prompt="Valid prompt that is long enough to pass validation",
            total_days=30,
        )
        assert t.total_days == 30


# ---------------------------------------------------------------------------
# TripResponse
# ---------------------------------------------------------------------------

class TestTripResponse:
    BASE = {
        "id": "00000000-0000-0000-0000-000000000001",
        "prompt": "5-day Tokyo trip",
        "destination": "Tokyo",
        "title": "Trip to Tokyo",
        "summary": None,
        "persona": None,
        "status": "pending",
        "total_days": 5,
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    }

    def test_valid_response(self):
        r = TripResponse(**self.BASE)
        assert str(r.id) == "00000000-0000-0000-0000-000000000001"
        assert r.status == "pending"

    def test_optional_summary_none(self):
        r = TripResponse(**self.BASE)
        assert r.summary is None

    def test_optional_persona_none(self):
        r = TripResponse(**self.BASE)
        assert r.persona is None


# ---------------------------------------------------------------------------
# TripDetail
# ---------------------------------------------------------------------------

class TestTripDetail:
    BASE = {
        "id": "00000000-0000-0000-0000-000000000001",
        "prompt": "5-day Tokyo trip",
        "destination": "Tokyo",
        "title": "Trip to Tokyo",
        "summary": None,
        "persona": None,
        "status": "completed",
        "total_days": 5,
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    }

    def test_defaults_to_empty_conflicts_and_reasoning(self):
        d = TripDetail(**self.BASE)
        assert d.conflicts == []
        assert d.reasoning == {}
        assert d.itinerary is None
        assert d.weather_data is None

    def test_accepts_itinerary_dict(self):
        d = TripDetail(**self.BASE, itinerary={"days": []})
        assert d.itinerary == {"days": []}

    def test_accepts_conflict_list(self):
        conflict = {"day": 2, "block": "afternoon", "severity": "warning", "message": "Rain expected"}
        d = TripDetail(**self.BASE, conflicts=[conflict])
        assert len(d.conflicts) == 1
        assert d.conflicts[0]["severity"] == "warning"


# ---------------------------------------------------------------------------
# TripListItem
# ---------------------------------------------------------------------------

class TestTripListItem:
    def test_valid(self):
        item = TripListItem(
            id="00000000-0000-0000-0000-000000000001",
            title="Trip to Tokyo",
            destination="Tokyo",
            total_days=5,
            status="completed",
            created_at="2026-01-01T00:00:00+00:00",
        )
        assert item.destination == "Tokyo"
        assert item.total_days == 5
