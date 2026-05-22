"""
Unit tests for haversine util and deterministic conflict checker.
No network calls, no DB, no LLM — pure Python logic.
"""

import copy

import pytest

from app.common.haversine import haversine_km
from app.planning.conflict_checker import run_conflict_checks
from app.planning.schemas import ItinerarySchema
from tests.mocks.mock_groq_responses import MOCK_SYNTHESIZER_JSON


# ---------------------------------------------------------------------------
# haversine
# ---------------------------------------------------------------------------

class TestHaversine:
    def test_same_point_is_zero(self):
        assert haversine_km(35.67, 139.65, 35.67, 139.65) == pytest.approx(0.0)

    def test_known_distance_tokyo_osaka(self):
        # Tokyo (35.68, 139.69) to Osaka (34.69, 135.50) ≈ 402 km
        dist = haversine_km(35.68, 139.69, 34.69, 135.50)
        assert 395 < dist < 410

    def test_short_intra_city_distance(self):
        # Senso-ji to Nakamise (same block in mock data) — should be < 1 km
        dist = haversine_km(35.7148, 139.7967, 35.7126, 139.7964)
        assert dist < 1.0

    def test_cross_hemisphere(self):
        # Sydney to London — sanity check that a large distance comes back > 10 000 km
        dist = haversine_km(-33.87, 151.21, 51.51, -0.13)
        assert dist > 10_000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _itinerary(overrides: dict | None = None) -> ItinerarySchema:
    """Parse the shared mock JSON, with optional dict-level overrides."""
    data = copy.deepcopy(MOCK_SYNTHESIZER_JSON)
    if overrides:
        data.update(overrides)
    return ItinerarySchema.model_validate(data)


# ---------------------------------------------------------------------------
# run_conflict_checks — no conflicts on clean data
# ---------------------------------------------------------------------------

class TestNoConflictsOnCleanItinerary:
    def test_mock_itinerary_has_no_distance_conflicts(self):
        """The mock Tokyo itinerary has all activities in nearby areas — no distance flags expected."""
        itinerary = _itinerary()
        conflicts = run_conflict_checks(itinerary)
        distance_conflicts = [c for c in conflicts if c.type == "distance"]
        assert distance_conflicts == []

    def test_mock_itinerary_timing_fits_blocks(self):
        """The mock itinerary's activity durations fit inside each time block."""
        itinerary = _itinerary()
        conflicts = run_conflict_checks(itinerary)
        timing_conflicts = [c for c in conflicts if c.type == "timing"]
        assert timing_conflicts == []


# ---------------------------------------------------------------------------
# Distance conflict
# ---------------------------------------------------------------------------

class TestDistanceConflict:
    def test_far_apart_activities_flagged(self):
        """Two consecutive activities 20+ km apart in the same block should produce a distance conflict."""
        data = copy.deepcopy(MOCK_SYNTHESIZER_JSON)
        # Shove Osaka coordinates into the second morning activity of day 1
        data["days"][0]["morning"]["activities"][1]["latitude"] = 34.693
        data["days"][0]["morning"]["activities"][1]["longitude"] = 135.502

        itinerary = ItinerarySchema.model_validate(data)
        conflicts = run_conflict_checks(itinerary)
        distance_conflicts = [c for c in conflicts if c.type == "distance"]
        assert len(distance_conflicts) >= 1
        assert "Nakamise Shopping Street" in distance_conflicts[0].activities

    def test_missing_coords_skip_distance_check(self):
        """Activities with no lat/lon should not produce distance conflicts."""
        data = copy.deepcopy(MOCK_SYNTHESIZER_JSON)
        data["days"][0]["morning"]["activities"][0]["latitude"] = None
        data["days"][0]["morning"]["activities"][0]["longitude"] = None

        itinerary = ItinerarySchema.model_validate(data)
        conflicts = run_conflict_checks(itinerary)
        assert all(c.type != "distance" for c in conflicts)


# ---------------------------------------------------------------------------
# Timing conflict
# ---------------------------------------------------------------------------

class TestTimingConflict:
    def test_overbooked_block_flagged(self):
        """If total activity duration exceeds the block window a timing conflict is raised."""
        data = copy.deepcopy(MOCK_SYNTHESIZER_JSON)
        # Morning block is 09:00-12:00 (180 min). Set one activity to 200 min.
        data["days"][0]["morning"]["activities"][0]["duration_minutes"] = 200

        itinerary = ItinerarySchema.model_validate(data)
        conflicts = run_conflict_checks(itinerary)
        timing_conflicts = [c for c in conflicts if c.type == "timing"]
        assert len(timing_conflicts) >= 1
        assert timing_conflicts[0].day_number == 1

    def test_exactly_full_block_no_conflict(self):
        """Activities summing to exactly the block length are not flagged."""
        data = copy.deepcopy(MOCK_SYNTHESIZER_JSON)
        # Morning block day 1: 09:00-12:00 = 180 min.  Set both activities to fit exactly.
        data["days"][0]["morning"]["activities"][0]["duration_minutes"] = 135
        data["days"][0]["morning"]["activities"][1]["duration_minutes"] = 45

        itinerary = ItinerarySchema.model_validate(data)
        conflicts = run_conflict_checks(itinerary)
        timing_conflicts = [c for c in conflicts if c.type == "timing" and c.day_number == 1]
        assert timing_conflicts == []


# ---------------------------------------------------------------------------
# Weather conflict
# ---------------------------------------------------------------------------

class TestWeatherConflict:
    def test_outdoor_activity_on_thunderstorm_day_flagged(self):
        """An outdoor activity scheduled on a thunderstorm day should produce a weather conflict."""
        data = copy.deepcopy(MOCK_SYNTHESIZER_JSON)
        data["days"][0]["weather"] = {"description": "Thunderstorm", "temperature_max": 22.0}
        # day 1 morning has 'shopping' (Nakamise) which is outdoor
        data["days"][0]["morning"]["activities"][1]["category"] = "shopping"

        itinerary = ItinerarySchema.model_validate(data)
        conflicts = run_conflict_checks(itinerary)
        weather_conflicts = [c for c in conflicts if c.type == "weather"]
        assert len(weather_conflicts) >= 1

    def test_indoor_activity_on_bad_weather_not_flagged(self):
        """Culture/food activities are not considered outdoor and should not trigger weather flags."""
        data = copy.deepcopy(MOCK_SYNTHESIZER_JSON)
        data["days"][0]["weather"] = {"description": "Heavy rain", "temperature_max": 18.0}
        # Ensure all day-1 activities are culture or food (indoor)
        for block_key in ("morning", "afternoon", "evening"):
            for act in data["days"][0][block_key]["activities"]:
                act["category"] = "culture"

        itinerary = ItinerarySchema.model_validate(data)
        conflicts = run_conflict_checks(itinerary)
        weather_conflicts = [c for c in conflicts if c.type == "weather" and c.day_number == 1]
        assert weather_conflicts == []

    def test_no_weather_data_no_weather_conflicts(self):
        """Days without weather snapshots never produce weather conflicts."""
        data = copy.deepcopy(MOCK_SYNTHESIZER_JSON)
        for day in data["days"]:
            day["weather"] = None

        itinerary = ItinerarySchema.model_validate(data)
        conflicts = run_conflict_checks(itinerary)
        assert all(c.type != "weather" for c in conflicts)


# ---------------------------------------------------------------------------
# Conflict fields
# ---------------------------------------------------------------------------

class TestConflictFields:
    def test_conflict_has_required_fields(self):
        data = copy.deepcopy(MOCK_SYNTHESIZER_JSON)
        data["days"][0]["morning"]["activities"][0]["duration_minutes"] = 300

        itinerary = ItinerarySchema.model_validate(data)
        conflicts = run_conflict_checks(itinerary)
        assert conflicts
        c = conflicts[0]
        assert c.type in ("distance", "timing", "weather", "budget", "persona")
        assert c.severity in ("warning", "error")
        assert isinstance(c.day_number, int)
        assert isinstance(c.description, str) and c.description
        assert isinstance(c.activities, list)
