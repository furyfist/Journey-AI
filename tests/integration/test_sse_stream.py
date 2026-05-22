"""
Integration tests for GET /api/v1/trips/{trip_id}/stream.

Strategy:
- Mock openai.AsyncOpenAI, Supabase, and HTTP calls
- Drive stream_planning_pipeline with controlled mock responses
- Verify event sequence, types, and conflict emission
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.planning.schemas import ItinerarySchema, SSEEvent
from tests.mocks.mock_groq_responses import MOCK_PLANNER_JSON, MOCK_SYNTHESIZER_JSON

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

PENDING_TRIP = {
    "id": "00000000-0000-0000-0000-000000000010",
    "prompt": "3-day Tokyo trip, budget street food lover",
    "destination": "Tokyo",
    "budget": "budget",
    "total_days": 3,
    "title": "Trip to Tokyo",
    "summary": None,
    "persona": None,
    "status": "pending",
    "travel_dates": None,
    "created_at": "2026-06-01T00:00:00+00:00",
    "updated_at": "2026-06-01T00:00:00+00:00",
}


def _wire_db(mock_db: MagicMock, trip: dict = PENDING_TRIP) -> None:
    tb = mock_db.table.return_value
    tb.insert.return_value.execute = AsyncMock(return_value=MagicMock(data=[trip]))
    tb.update.return_value.eq.return_value.execute = AsyncMock(return_value=MagicMock(data=[trip]))
    tb.select.return_value.eq.return_value.single.return_value.execute = AsyncMock(
        return_value=MagicMock(data=trip)
    )
    tb.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[])
    )
    tb.select.return_value.limit.return_value.execute = AsyncMock(return_value=MagicMock(data=[]))


def _make_text_response(content: str):
    choice = MagicMock()
    choice.message.content = content
    choice.message.tool_calls = None
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _make_tool_response(tool_name: str, args: dict, call_id: str = "call_1"):
    tc = MagicMock()
    tc.id = call_id
    tc.type = "function"
    tc.function.name = tool_name
    tc.function.arguments = json.dumps(args)
    choice = MagicMock()
    choice.message.content = None
    choice.message.tool_calls = [tc]
    resp = MagicMock()
    resp.choices = [choice]
    return resp


# ---------------------------------------------------------------------------
# stream_planning_pipeline — unit tests (pure async generator)
# ---------------------------------------------------------------------------

class TestStreamPipelineGenerator:
    @pytest.mark.asyncio
    async def test_yields_agent_start_events(self, mock_http):
        """Generator must emit agent_start for researcher, planner, synthesizer, critic."""
        mock_db = MagicMock()
        _wire_db(mock_db)

        critic_output = json.dumps({"conflicts": []})
        groq_responses = [
            _make_text_response("Research done."),
            _make_text_response(json.dumps(MOCK_PLANNER_JSON)),
            _make_text_response(json.dumps(MOCK_SYNTHESIZER_JSON)),
            _make_text_response(critic_output),
        ]

        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=groq_responses)
            mock_cls.return_value = mock_client

            with (
                patch("app.planning.tools.weather_tool.fetch_weather", AsyncMock(
                    return_value=MagicMock(model_dump=lambda: {"lat": 35.67, "lon": 139.65, "timezone": "Asia/Tokyo", "days": []})
                )),
                patch("app.planning.tools.places_tool.fetch_places", AsyncMock(
                    return_value=MagicMock(model_dump=lambda: {"lat": 35.67, "lon": 139.65, "category": "food", "radius_m": 5000, "places": []})
                )),
            ):
                from app.planning.stream_service import stream_planning_pipeline

                events: list[SSEEvent] = []
                async for ev in stream_planning_pipeline(
                    db=mock_db, http=mock_http,
                    trip_id="00000000-0000-0000-0000-000000000010",
                    prompt="3-day Tokyo trip",
                    destination="Tokyo", total_days=3,
                ):
                    events.append(ev)

        event_types = [e.event for e in events]
        assert "agent_start" in event_types
        assert "agent_complete" in event_types
        assert "trip_complete" in event_types

        agents_started = {e.agent for e in events if e.event == "agent_start"}
        assert "researcher" in agents_started
        assert "planner" in agents_started
        assert "synthesizer" in agents_started
        assert "critic" in agents_started

    @pytest.mark.asyncio
    async def test_yields_error_event_on_pipeline_failure(self, mock_http):
        """When the researcher raises, an error event should be emitted."""
        mock_db = MagicMock()
        _wire_db(mock_db)

        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=Exception("Groq down"))
            mock_cls.return_value = mock_client

            from app.planning.stream_service import stream_planning_pipeline

            events: list[SSEEvent] = []
            async for ev in stream_planning_pipeline(
                db=mock_db, http=mock_http,
                trip_id="00000000-0000-0000-0000-000000000010",
                prompt="3-day Tokyo trip",
                destination="Tokyo", total_days=3,
            ):
                events.append(ev)

        error_events = [e for e in events if e.event == "error"]
        assert len(error_events) >= 1
        assert error_events[0].message  # must carry a description

    @pytest.mark.asyncio
    async def test_conflict_detected_events_emitted(self, mock_http):
        """Trips with deterministic conflicts should emit conflict_detected events."""
        import copy
        mock_db = MagicMock()
        _wire_db(mock_db)

        # Inject a timing conflict: force morning block to be overbooked
        bad_synthesizer = copy.deepcopy(MOCK_SYNTHESIZER_JSON)
        bad_synthesizer["days"][0]["morning"]["activities"][0]["duration_minutes"] = 500

        groq_responses = [
            _make_text_response("Research done."),
            _make_text_response(json.dumps(MOCK_PLANNER_JSON)),
            _make_text_response(json.dumps(bad_synthesizer)),
            _make_text_response(json.dumps({"conflicts": []})),
        ]

        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=groq_responses)
            mock_cls.return_value = mock_client

            with (
                patch("app.planning.tools.weather_tool.fetch_weather", AsyncMock(
                    return_value=MagicMock(model_dump=lambda: {"lat": 35.67, "lon": 139.65, "timezone": "Asia/Tokyo", "days": []})
                )),
                patch("app.planning.tools.places_tool.fetch_places", AsyncMock(
                    return_value=MagicMock(model_dump=lambda: {"lat": 35.67, "lon": 139.65, "category": "food", "radius_m": 5000, "places": []})
                )),
            ):
                from app.planning.stream_service import stream_planning_pipeline

                events: list[SSEEvent] = []
                async for ev in stream_planning_pipeline(
                    db=mock_db, http=mock_http,
                    trip_id="00000000-0000-0000-0000-000000000010",
                    prompt="3-day Tokyo trip",
                    destination="Tokyo", total_days=3,
                ):
                    events.append(ev)

        conflict_events = [e for e in events if e.event == "conflict_detected"]
        assert len(conflict_events) >= 1
        c = conflict_events[0].data
        assert c["type"] == "timing"
        assert c["day_number"] == 1

    @pytest.mark.asyncio
    async def test_tool_call_events_emitted(self, mock_http):
        """Tool calls made during researcher should surface as tool_call events."""
        mock_db = MagicMock()
        _wire_db(mock_db)

        weather_result = {"lat": 35.67, "lon": 139.65, "timezone": "Asia/Tokyo", "days": []}
        places_result = {"lat": 35.67, "lon": 139.65, "category": "food", "radius_m": 5000, "places": []}

        groq_responses = [
            _make_tool_response("get_weather", {"city": "Tokyo", "days": 3}, "call_w"),
            _make_tool_response("search_places", {"lat": 35.67, "lon": 139.65, "category": "food"}, "call_p"),
            _make_text_response("Research done."),
            _make_text_response(json.dumps(MOCK_PLANNER_JSON)),
            _make_text_response(json.dumps(MOCK_SYNTHESIZER_JSON)),
            _make_text_response(json.dumps({"conflicts": []})),
        ]

        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=groq_responses)
            mock_cls.return_value = mock_client

            with (
                patch("app.planning.tools.weather_tool.fetch_weather", AsyncMock(
                    return_value=MagicMock(model_dump=lambda: weather_result)
                )),
                patch("app.planning.tools.places_tool.fetch_places", AsyncMock(
                    return_value=MagicMock(model_dump=lambda: places_result)
                )),
            ):
                from app.planning.stream_service import stream_planning_pipeline

                events: list[SSEEvent] = []
                async for ev in stream_planning_pipeline(
                    db=mock_db, http=mock_http,
                    trip_id="00000000-0000-0000-0000-000000000010",
                    prompt="3-day Tokyo trip",
                    destination="Tokyo", total_days=3,
                ):
                    events.append(ev)

        tool_call_events = [e for e in events if e.event == "tool_call"]
        tool_names = [e.data["tool"] for e in tool_call_events]
        assert "get_weather" in tool_names
        assert "search_places" in tool_names


# ---------------------------------------------------------------------------
# GET /api/v1/trips/{trip_id}/stream — HTTP endpoint tests
# ---------------------------------------------------------------------------

class TestStreamEndpoint:
    def test_stream_endpoint_requires_existing_trip(self, client, mock_db):
        """Requesting a non-existent trip_id should return 404 (via repo.fetch_trip_by_id)."""
        mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute = (
            AsyncMock(return_value=MagicMock(data=None))
        )
        resp = client.get("/api/v1/trips/00000000-0000-0000-0000-000000000099/stream")
        assert resp.status_code == 404

    def test_stream_endpoint_emits_text_event_stream_content_type(self, client, mock_db):
        """The SSE endpoint must set Content-Type: text/event-stream."""
        _wire_db(mock_db)

        async def _noop_gen(*args, **kwargs):
            from app.planning.schemas import SSEEvent
            import json
            yield SSEEvent(event="trip_complete", data={"trip_id": "x"})

        with patch("app.trips.router.stream_planning_pipeline", new=_noop_gen):
            resp = client.get(
                "/api/v1/trips/00000000-0000-0000-0000-000000000010/stream",
                headers={"Accept": "text/event-stream"},
            )

        assert "text/event-stream" in resp.headers.get("content-type", "")

    def test_stream_endpoint_sse_body_contains_typed_events(self, client, mock_db):
        """Raw SSE body should contain 'event:' lines with our typed event names."""
        _wire_db(mock_db)

        async def _events(*args, **kwargs):
            from app.planning.schemas import SSEEvent
            yield SSEEvent(event="agent_start", agent="researcher", message="Starting")
            yield SSEEvent(event="trip_complete", data={"trip_id": "x"})

        with patch("app.trips.router.stream_planning_pipeline", new=_events):
            resp = client.get(
                "/api/v1/trips/00000000-0000-0000-0000-000000000010/stream",
                headers={"Accept": "text/event-stream"},
            )

        body = resp.text
        assert "agent_start" in body
        assert "trip_complete" in body
