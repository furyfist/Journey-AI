"""
Integration tests for the AI planning pipeline.

Strategy:
- Mock openai.AsyncOpenAI so no real Groq calls are made
- Mock the DB (via conftest fixture) so no Supabase calls
- Mock weather/places HTTP calls
- Verify the pipeline orchestration and endpoint behaviour
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.planning.agents.planner_agent import PlannerAgent
from app.planning.agents.researcher_agent import ResearcherAgent
from app.planning.agents.synthesizer_agent import SynthesizerAgent
from app.planning.schemas import ItinerarySchema, ResearchBundle
from tests.mocks.mock_groq_responses import MOCK_PLANNER_JSON, MOCK_SYNTHESIZER_JSON


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_groq_text_response(content: str):
    """Build a minimal fake openai ChatCompletion response with text content."""
    choice = MagicMock()
    choice.message.content = content
    choice.message.tool_calls = None
    response = MagicMock()
    response.choices = [choice]
    return response


def _make_groq_tool_response(tool_name: str, args: dict, call_id: str = "call_1"):
    """Build a fake response where the model requests a tool call."""
    tc = MagicMock()
    tc.id = call_id
    tc.type = "function"
    tc.function.name = tool_name
    tc.function.arguments = json.dumps(args)

    choice = MagicMock()
    choice.message.content = None
    choice.message.tool_calls = [tc]

    response = MagicMock()
    response.choices = [choice]
    return response


MOCK_RESEARCH = ResearchBundle(
    destination="Tokyo",
    prompt="3-day Tokyo trip, budget street food",
    total_days=3,
    budget="budget",
    weather={"lat": 35.67, "lon": 139.65, "timezone": "Asia/Tokyo", "days": []},
    places={"food": [{"name": "Tsukiji Market", "lat": 35.66, "lon": 139.77, "osm_id": 1, "category": "food", "tags": {}}]},
)


# ---------------------------------------------------------------------------
# ResearcherAgent unit tests
# ---------------------------------------------------------------------------

class TestResearcherAgent:
    @pytest.mark.asyncio
    async def test_run_research_collects_weather_and_places(self, mock_http):
        """Researcher should call tools and aggregate their results into a ResearchBundle."""
        weather_result = {
            "lat": 35.67,
            "lon": 139.65,
            "timezone": "Asia/Tokyo",
            "days": [{"date": "2026-06-01", "description": "Clear sky"}],
        }
        places_result = {
            "lat": 35.67,
            "lon": 139.65,
            "category": "food",
            "radius_m": 5000,
            "places": [{"name": "Tsukiji", "lat": 35.66, "lon": 139.77, "osm_id": 1, "category": "food", "tags": {}}],
        }

        # Groq: first call → weather tool_call, second call → places tool_call, third call → text
        groq_responses = [
            _make_groq_tool_response("get_weather", {"city": "Tokyo", "days": 3}, "call_w"),
            _make_groq_tool_response("search_places", {"lat": 35.67, "lon": 139.65, "category": "food"}, "call_p"),
            _make_groq_text_response("Research complete."),
        ]

        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=groq_responses)
            mock_openai_cls.return_value = mock_client

            with (
                patch("app.planning.tools.weather_tool.fetch_weather", new=AsyncMock(return_value=MagicMock(model_dump=lambda: weather_result))),
                patch("app.planning.tools.places_tool.fetch_places", new=AsyncMock(return_value=MagicMock(model_dump=lambda: places_result))),
            ):
                agent = ResearcherAgent(mock_http)
                bundle = await agent.run_research(
                    prompt="Tokyo street food trip",
                    destination="Tokyo",
                    total_days=3,
                    budget="budget",
                )

        assert bundle.destination == "Tokyo"
        assert bundle.weather is not None
        assert "food" in bundle.places

    @pytest.mark.asyncio
    async def test_run_research_returns_bundle_even_if_llm_fails(self, mock_http):
        """If the final LLM step fails, tool-collected data is still returned."""
        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=Exception("Groq down"))
            mock_openai_cls.return_value = mock_client

            agent = ResearcherAgent(mock_http)
            # Seed some data manually to simulate tool collection before failure
            agent._weather = {"lat": 35.67}
            agent._places = {"food": [{"name": "Test Place"}]}

            bundle = await agent.run_research("trip", "Tokyo", 3)

        assert bundle.destination == "Tokyo"
        assert bundle.weather == {"lat": 35.67}


# ---------------------------------------------------------------------------
# PlannerAgent unit tests
# ---------------------------------------------------------------------------

class TestPlannerAgent:
    @pytest.mark.asyncio
    async def test_run_planning_returns_valid_plan(self, mock_http):
        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_groq_text_response(json.dumps(MOCK_PLANNER_JSON))
            )
            mock_openai_cls.return_value = mock_client

            agent = PlannerAgent(mock_http)
            plan = await agent.run_planning("Tokyo street food trip", MOCK_RESEARCH)

        assert plan["persona"] == "Foodie"
        assert len(plan["days"]) == 3

    @pytest.mark.asyncio
    async def test_run_planning_raises_on_invalid_json(self, mock_http):
        from app.core.exceptions import SchemaValidationError

        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_groq_text_response("not valid json {{}")
            )
            mock_openai_cls.return_value = mock_client

            agent = PlannerAgent(mock_http)
            with pytest.raises(SchemaValidationError):
                await agent.run_planning("trip", MOCK_RESEARCH)

    @pytest.mark.asyncio
    async def test_run_planning_raises_when_persona_missing(self, mock_http):
        from app.core.exceptions import SchemaValidationError

        incomplete = {"days": []}  # missing persona
        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_groq_text_response(json.dumps(incomplete))
            )
            mock_openai_cls.return_value = mock_client

            agent = PlannerAgent(mock_http)
            with pytest.raises(SchemaValidationError):
                await agent.run_planning("trip", MOCK_RESEARCH)


# ---------------------------------------------------------------------------
# SynthesizerAgent unit tests
# ---------------------------------------------------------------------------

class TestSynthesizerAgent:
    @pytest.mark.asyncio
    async def test_run_synthesis_returns_valid_itinerary(self, mock_http):
        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_groq_text_response(json.dumps(MOCK_SYNTHESIZER_JSON))
            )
            mock_openai_cls.return_value = mock_client

            agent = SynthesizerAgent(mock_http)
            itinerary = await agent.run_synthesis("Tokyo trip", MOCK_RESEARCH, MOCK_PLANNER_JSON)

        assert isinstance(itinerary, ItinerarySchema)
        assert itinerary.destination == "Tokyo"
        assert itinerary.total_days == 3
        assert len(itinerary.days) == 3

    @pytest.mark.asyncio
    async def test_run_synthesis_raises_on_schema_mismatch(self, mock_http):
        from app.core.exceptions import SchemaValidationError

        # Missing required fields
        bad = {"title": "Oops"}
        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_groq_text_response(json.dumps(bad))
            )
            mock_openai_cls.return_value = mock_client

            agent = SynthesizerAgent(mock_http)
            with pytest.raises(SchemaValidationError):
                await agent.run_synthesis("trip", MOCK_RESEARCH, MOCK_PLANNER_JSON)


# ---------------------------------------------------------------------------
# Full pipeline via POST /api/v1/trips
# ---------------------------------------------------------------------------

def _wire_db(mock_db: MagicMock, trip: dict) -> None:
    """Wire all Supabase call chains used by create_trip."""
    tb = mock_db.table.return_value
    tb.insert.return_value.execute = AsyncMock(return_value=MagicMock(data=[trip]))
    tb.update.return_value.eq.return_value.execute = AsyncMock(return_value=MagicMock(data=[trip]))
    tb.delete.return_value.eq.return_value.execute = AsyncMock(return_value=MagicMock(data=[]))
    tb.select.return_value.eq.return_value.single.return_value.execute = AsyncMock(
        return_value=MagicMock(data=trip)
    )
    tb.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[])
    )
    tb.select.return_value.limit.return_value.execute = AsyncMock(return_value=MagicMock(data=[]))


COMPLETED_TRIP = {
    "id": "00000000-0000-0000-0000-000000000002",
    "prompt": "3-day Tokyo trip, budget street food lover",
    "destination": "Tokyo",
    "budget": "budget",
    "total_days": 3,
    "title": "Tokyo Street Food & Culture Adventure",
    "summary": "A great trip overview.",
    "persona": "Foodie",
    "status": "completed",
    "travel_dates": None,
    "created_at": "2026-06-01T00:00:00+00:00",
    "updated_at": "2026-06-01T00:00:00+00:00",
}

FAILED_TRIP = {
    "id": "00000000-0000-0000-0000-000000000003",
    "prompt": "A trip somewhere interesting and fun for a week",
    "destination": "Unknown",
    "budget": None,
    "total_days": 5,
    "title": "Trip to Unknown",
    "summary": None,
    "persona": None,
    "status": "failed",
    "travel_dates": None,
    "created_at": "2026-06-01T00:00:00+00:00",
    "updated_at": "2026-06-01T00:00:00+00:00",
}


class TestPlanningEndpointIntegration:
    def test_create_trip_triggers_pipeline_and_returns_completed(self, client, mock_db):
        """Successful pipeline run: endpoint returns 201 with completed trip data."""
        _wire_db(mock_db, COMPLETED_TRIP)

        with patch(
            "app.planning.service.run_planning_pipeline",
            new=AsyncMock(return_value=ItinerarySchema.model_validate(MOCK_SYNTHESIZER_JSON)),
        ):
            response = client.post(
                "/api/v1/trips",
                json={
                    "prompt": "3-day Tokyo trip, budget street food lover",
                    "destination": "Tokyo",
                    "total_days": 3,
                    "budget": "budget",
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["destination"] == "Tokyo"
        assert data["status"] == "completed"
        assert data["persona"] == "Foodie"

    def test_create_trip_pipeline_failure_returns_failed_status(self, client, mock_db):
        """When the pipeline raises, the endpoint still returns 201 with status 'failed'."""
        _wire_db(mock_db, FAILED_TRIP)

        from app.core.exceptions import GroqAPIError

        with patch(
            "app.planning.service.run_planning_pipeline",
            new=AsyncMock(side_effect=GroqAPIError("Groq down")),
        ):
            response = client.post(
                "/api/v1/trips",
                json={"prompt": "A trip somewhere interesting and fun for a week"},
            )

        assert response.status_code == 201
        assert response.json()["status"] == "failed"
