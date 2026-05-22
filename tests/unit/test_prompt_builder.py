"""Unit tests for prompt_builder — pure string/logic checks, no I/O."""

import json

import pytest

from app.planning.prompt_builder import (
    planner_system_prompt,
    planner_user_message,
    researcher_system_prompt,
    researcher_user_message,
    synthesizer_system_prompt,
    synthesizer_user_message,
)
from app.planning.schemas import ResearchBundle


@pytest.fixture
def research() -> ResearchBundle:
    return ResearchBundle(
        destination="Tokyo",
        prompt="5-day Tokyo trip, street food lover",
        total_days=5,
        budget="budget",
        weather={"days": [{"date": "2026-06-01", "description": "Clear sky"}]},
        places={"food": [{"name": "Tsukiji Market", "lat": 35.66, "lon": 139.77}]},
    )


class TestResearcherPrompt:
    def test_system_prompt_instructs_tool_order(self):
        prompt = researcher_system_prompt()
        assert "get_weather" in prompt
        assert "search_places" in prompt
        # Step ordering should be mentioned
        assert "Step 1" in prompt and "Step 2" in prompt

    def test_user_message_includes_destination(self):
        msg = researcher_user_message("Tokyo trip", "Tokyo", 5, None, None)
        assert "Tokyo" in msg
        assert "5-day" in msg

    def test_user_message_includes_start_date(self):
        msg = researcher_user_message("Tokyo trip", "Tokyo", 3, "2026-07-01", None)
        assert "2026-07-01" in msg

    def test_user_message_includes_budget(self):
        msg = researcher_user_message("Tokyo trip", "Tokyo", 3, None, "luxury")
        assert "luxury" in msg

    def test_user_message_includes_original_prompt(self):
        original = "I love street food and temples"
        msg = researcher_user_message(original, "Tokyo", 4, None, None)
        assert original in msg


class TestPlannerPrompt:
    def test_system_prompt_lists_all_personas(self):
        prompt = planner_system_prompt()
        for persona in ["Budget Backpacker", "Luxury Explorer", "Culture Seeker", "Foodie"]:
            assert persona in prompt

    def test_system_prompt_requires_json_output(self):
        prompt = planner_system_prompt()
        assert "persona" in prompt
        assert "days" in prompt

    def test_user_message_includes_research_data(self, research):
        msg = planner_user_message("street food trip", research)
        assert "Tokyo" in msg
        assert "weather" in msg.lower() or "Weather" in msg
        assert "Tsukiji Market" in msg

    def test_user_message_includes_total_days(self, research):
        msg = planner_user_message("my trip", research)
        assert "5-day" in msg


class TestSynthesizerPrompt:
    def test_system_prompt_contains_schema(self):
        prompt = synthesizer_system_prompt()
        # Schema JSON should be embedded
        assert "ItinerarySchema" in prompt or "title" in prompt
        assert "activities" in prompt
        assert "tips" in prompt

    def test_system_prompt_enforces_rules(self):
        prompt = synthesizer_system_prompt()
        assert "JSON" in prompt
        assert "3" in prompt  # min tips count

    def test_user_message_includes_all_sections(self, research):
        rough_plan = {"persona": "Foodie", "days": []}
        msg = synthesizer_user_message("street food trip", research, rough_plan)
        assert "Tokyo" in msg
        assert "Foodie" in msg
        assert "weather" in msg.lower() or "Weather" in msg
        assert "Tsukiji Market" in msg
