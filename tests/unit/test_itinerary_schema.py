"""Unit tests for ItinerarySchema and nested models — validation only, no I/O."""

import pytest
from pydantic import ValidationError

from app.planning.schemas import Activity, DayPlan, ItinerarySchema, ResearchBundle, TimeBlock
from tests.mocks.mock_groq_responses import MOCK_SYNTHESIZER_JSON


def make_activity(**overrides) -> dict:
    base = {
        "name": "Senso-ji Temple",
        "description": "Famous temple in Asakusa.",
        "location": "Asakusa, Tokyo",
        "duration_minutes": 60,
        "cost_estimate": "Free",
        "category": "culture",
        "reasoning": "Best visited early morning.",
    }
    return {**base, **overrides}


def make_block(label: str = "morning", **overrides) -> dict:
    base = {
        "label": label,
        "start_time": "09:00",
        "end_time": "12:00",
        "activities": [make_activity()],
        "block_summary": "A great morning block.",
    }
    return {**base, **overrides}


def make_day(day_number: int = 1, **overrides) -> dict:
    base = {
        "day_number": day_number,
        "title": "Day of Exploration",
        "morning": make_block("morning"),
        "afternoon": make_block("afternoon"),
        "evening": make_block("evening"),
        "day_summary": "A wonderful day in Tokyo.",
    }
    return {**base, **overrides}


def make_itinerary(**overrides) -> dict:
    base = {
        "title": "Tokyo Adventure",
        "destination": "Tokyo",
        "total_days": 1,
        "budget_level": "budget",
        "persona": "Foodie",
        "summary": "A great trip overview.",
        "days": [make_day()],
        "tips": ["Tip 1", "Tip 2", "Tip 3"],
    }
    return {**base, **overrides}


class TestActivity:
    def test_valid_activity(self):
        a = Activity(**make_activity())
        assert a.name == "Senso-ji Temple"
        assert a.latitude is None

    def test_optional_lat_lon(self):
        a = Activity(**make_activity(latitude=35.71, longitude=139.79))
        assert a.latitude == pytest.approx(35.71)

    def test_missing_required_field_raises(self):
        data = make_activity()
        del data["reasoning"]
        with pytest.raises(ValidationError):
            Activity(**data)


class TestTimeBlock:
    def test_valid_block(self):
        block = TimeBlock(**make_block())
        assert len(block.activities) == 1

    def test_empty_activities_raises(self):
        data = make_block(activities=[])
        with pytest.raises(ValidationError):
            TimeBlock(**data)

    def test_five_activities_raises(self):
        data = make_block(activities=[make_activity()] * 5)
        with pytest.raises(ValidationError):
            TimeBlock(**data)

    def test_four_activities_ok(self):
        data = make_block(activities=[make_activity()] * 4)
        block = TimeBlock(**data)
        assert len(block.activities) == 4


class TestItinerarySchema:
    def test_valid_itinerary(self):
        it = ItinerarySchema(**make_itinerary())
        assert it.destination == "Tokyo"
        assert it.total_days == 1
        assert len(it.tips) == 3

    def test_fewer_than_three_tips_raises(self):
        with pytest.raises(ValidationError):
            ItinerarySchema(**make_itinerary(tips=["Only one tip"]))

    def test_more_than_five_tips_raises(self):
        with pytest.raises(ValidationError):
            ItinerarySchema(**make_itinerary(tips=["T1", "T2", "T3", "T4", "T5", "T6"]))

    def test_mock_synthesizer_json_is_valid(self):
        """The fixture used in integration tests must be a valid schema."""
        it = ItinerarySchema.model_validate(MOCK_SYNTHESIZER_JSON)
        assert it.destination == "Tokyo"
        assert it.total_days == 3
        assert len(it.days) == 3
        assert len(it.tips) >= 3

    def test_model_dump_round_trip(self):
        it = ItinerarySchema(**make_itinerary())
        dumped = it.model_dump()
        restored = ItinerarySchema.model_validate(dumped)
        assert restored.title == it.title

    def test_missing_destination_raises(self):
        data = make_itinerary()
        del data["destination"]
        with pytest.raises(ValidationError):
            ItinerarySchema(**data)


class TestResearchBundle:
    def test_defaults(self):
        rb = ResearchBundle(destination="Paris", prompt="paris trip", total_days=3)
        assert rb.weather is None
        assert rb.places == {}
        assert rb.budget is None

    def test_with_data(self):
        rb = ResearchBundle(
            destination="Paris",
            prompt="paris trip",
            total_days=3,
            weather={"lat": 48.85},
            places={"food": [{"name": "Café de Flore"}]},
            budget="luxury",
        )
        assert rb.weather["lat"] == 48.85
        assert len(rb.places["food"]) == 1
