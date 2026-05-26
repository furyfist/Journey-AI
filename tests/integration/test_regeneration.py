"""
Integration tests for POST /api/v1/trips/{trip_id}/regenerate.

Strategy:
- Mock openai.AsyncOpenAI (no real Groq calls)
- Mock Supabase (no real DB)
- Verify routing, schema validation, and service orchestration
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.planning.schemas import ItinerarySchema
from tests.mocks.mock_groq_responses import MOCK_SYNTHESIZER_JSON

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

TRIP_ID = "00000000-0000-0000-0000-000000000020"

BASE_TRIP = {
    "id": TRIP_ID,
    "prompt": "3-day Tokyo trip, budget street food lover",
    "destination": "Tokyo",
    "budget": "budget",
    "total_days": 3,
    "travel_dates": {"start": "2026-06-01", "end": "2026-06-03"},
    "title": "Trip to Tokyo",
    "summary": "A great trip.",
    "persona": "Foodie",
    "persona_hint": "Foodie",
    "interests": ["food", "culture"],
    "constraints": ["vegetarian"],
    "travel_party": "solo",
    "status": "completed",
    "created_at": "2026-06-01T00:00:00+00:00",
    "updated_at": "2026-06-01T00:00:00+00:00",
}

ITINERARY_ROW = {
    "id": "aaaa0000-0000-0000-0000-000000000001",
    "trip_id": TRIP_ID,
    "version": 1,
    "itinerary_data": MOCK_SYNTHESIZER_JSON,
    "weather_data": {"lat": 35.67, "lon": 139.65, "timezone": "Asia/Tokyo", "days": []},
    "places_data": {
        "food": [{"name": "Tsukiji", "lat": 35.66, "lon": 139.77, "osm_id": 1, "category": "food", "tags": {}}]
    },
    "conflicts": [],
    "reasoning": {},
    "is_active": True,
}

DETAIL_TRIP = {
    **BASE_TRIP,
    "itinerary": MOCK_SYNTHESIZER_JSON,
    "conflicts": [
        {
            "type": "timing",
            "severity": "warning",
            "day_number": 1,
            "description": "Too many activities in the block",
            "activities": ["Senso-ji Temple", "Nakamise Shopping Street"],
        }
    ],
    "reasoning": {},
    "weather_data": None,
}


def _wire_db(mock_db: MagicMock) -> None:
    """Wire all DB call chains used by regenerate_trip."""
    tb = mock_db.table.return_value

    # fetch_trip_by_id  (select * eq single)
    tb.select.return_value.eq.return_value.single.return_value.execute = AsyncMock(
        return_value=MagicMock(data=BASE_TRIP)
    )
    # fetch_active_itinerary  (select * eq eq limit)
    tb.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[ITINERARY_ROW])
    )
    # fetch_trip_detail — active itinerary join (second eq.eq.limit call returns empty for detail)
    # We need the detail call to work too — wire update and insert
    tb.update.return_value.eq.return_value.execute = AsyncMock(return_value=MagicMock(data=[]))
    tb.update.return_value.eq.return_value.eq.return_value.execute = AsyncMock(return_value=MagicMock(data=[]))
    tb.insert.return_value.execute = AsyncMock(return_value=MagicMock(data=[ITINERARY_ROW]))
    # Health check probe
    tb.select.return_value.limit.return_value.execute = AsyncMock(return_value=MagicMock(data=[]))


def _text_response(content: str):
    choice = MagicMock()
    choice.message.content = content
    choice.message.tool_calls = None
    resp = MagicMock()
    resp.choices = [choice]
    return resp


# ---------------------------------------------------------------------------
# Schema validation tests (no DB/LLM needed)
# ---------------------------------------------------------------------------

class TestRegenerateRequestValidation:
    def test_full_trip_no_day_required(self, client, mock_db):
        """scope=full_trip is valid without day_number or block_label."""
        _wire_db(mock_db)
        with patch("app.regeneration.service.regenerate_trip", new=AsyncMock(return_value=DETAIL_TRIP)):
            resp = client.post(
                f"/api/v1/trips/{TRIP_ID}/regenerate",
                json={"scope": "full_trip"},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == TRIP_ID
        assert body["itinerary"]["destination"] == "Tokyo"
        assert body["conflicts"][0]["type"] == "timing"

    def test_day_scope_requires_day_number(self, client, mock_db):
        resp = client.post(
            f"/api/v1/trips/{TRIP_ID}/regenerate",
            json={"scope": "day"},
        )
        assert resp.status_code == 422

    def test_single_block_requires_day_number_and_block_label(self, client, mock_db):
        # Missing block_label
        resp = client.post(
            f"/api/v1/trips/{TRIP_ID}/regenerate",
            json={"scope": "single_block", "day_number": 1},
        )
        assert resp.status_code == 422

    def test_single_block_valid_payload(self, client, mock_db):
        _wire_db(mock_db)
        with patch("app.regeneration.service.regenerate_trip", new=AsyncMock(return_value=DETAIL_TRIP)):
            resp = client.post(
                f"/api/v1/trips/{TRIP_ID}/regenerate",
                json={"scope": "single_block", "day_number": 1, "block_label": "morning"},
            )
        assert resp.status_code == 200

    def test_invalid_block_label_rejected(self, client, mock_db):
        resp = client.post(
            f"/api/v1/trips/{TRIP_ID}/regenerate",
            json={"scope": "single_block", "day_number": 1, "block_label": "midnight"},
        )
        assert resp.status_code == 422

    def test_constraint_accepted(self, client, mock_db):
        _wire_db(mock_db)
        with patch("app.regeneration.service.regenerate_trip", new=AsyncMock(return_value=DETAIL_TRIP)):
            resp = client.post(
                f"/api/v1/trips/{TRIP_ID}/regenerate",
                json={"scope": "full_trip", "constraint": "make it vegetarian"},
            )
        assert resp.status_code == 200

    def test_trip_not_found_returns_404(self, client, mock_db):
        mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute = (
            AsyncMock(return_value=MagicMock(data=None))
        )
        resp = client.post(
            f"/api/v1/trips/00000000-0000-0000-0000-000000000099/regenerate",
            json={"scope": "full_trip"},
        )
        assert resp.status_code == 404

    def test_day_scope_rejects_nonexistent_day(self, client, mock_db):
        _wire_db(mock_db)
        resp = client.post(
            f"/api/v1/trips/{TRIP_ID}/regenerate",
            json={"scope": "day", "day_number": 9},
        )
        assert resp.status_code == 400
        assert "Cannot regenerate day 9" in resp.json()["detail"]

    def test_single_block_rejects_nonexistent_day(self, client, mock_db):
        _wire_db(mock_db)
        resp = client.post(
            f"/api/v1/trips/{TRIP_ID}/regenerate",
            json={"scope": "single_block", "day_number": 9, "block_label": "morning"},
        )
        assert resp.status_code == 400
        assert "Cannot regenerate day 9" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Service unit tests — regeneration logic
# ---------------------------------------------------------------------------

class TestRegenerationService:
    @pytest.mark.asyncio
    async def test_full_trip_regen_uses_synthesizer_only_pipeline(self, mock_http):
        """full_trip scope should use the current synthesizer-only planning flow."""
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)

        groq_responses = [
            _text_response(json.dumps(MOCK_SYNTHESIZER_JSON)),  # synthesizer
            _text_response(json.dumps({"conflicts": []})),      # critic
        ]

        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=groq_responses)
            mock_cls.return_value = mock_client

            from app.regeneration.service import regenerate_trip
            result = await regenerate_trip(
                db=mock_db,
                http=mock_http,
                trip_id=TRIP_ID,
                request=RegenerateRequest(scope=RegenerateScope.full_trip),
            )

        assert result["destination"] == "Tokyo"

    @pytest.mark.asyncio
    async def test_full_trip_regen_restores_structured_trip_context(self, mock_http):
        """Structured trip fields should be restored into ResearchBundle during regeneration."""
        from app.planning.schemas import ItinerarySchema
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)

        with patch("app.regeneration.service.SynthesizerAgent.run_synthesis", new=AsyncMock()) as mock_synthesis:
            mock_synthesis.return_value = ItinerarySchema.model_validate(MOCK_SYNTHESIZER_JSON)
            with patch("app.regeneration.service.CriticAgent.run_critique", new=AsyncMock(return_value=[])):
                from app.regeneration.service import regenerate_trip
                await regenerate_trip(
                    db=mock_db,
                    http=mock_http,
                    trip_id=TRIP_ID,
                    request=RegenerateRequest(scope=RegenerateScope.full_trip, constraint="more vegetarian"),
                )

        call_args = mock_synthesis.await_args
        prompt_passed = call_args.args[0]
        research_passed = call_args.args[1]

        assert "Additional constraint: more vegetarian" in prompt_passed
        assert research_passed.start_date == "2026-06-01"
        assert research_passed.end_date == "2026-06-03"
        assert research_passed.persona_hint == "Foodie"
        assert research_passed.interests == ["food", "culture"]
        assert research_passed.constraints == ["vegetarian"]
        assert research_passed.travel_party == "solo"

    @pytest.mark.asyncio
    async def test_day_regen_replaces_only_specified_day(self, mock_http):
        """scope=day should only modify the targeted day_number."""
        import copy
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)

        # Build a modified day 1 JSON
        modified_day1 = copy.deepcopy(MOCK_SYNTHESIZER_JSON["days"][0])
        modified_day1["title"] = "REGENERATED DAY"

        # Critic returns empty
        groq_responses = [
            _text_response(json.dumps(modified_day1)),     # day_regenerator
            _text_response(json.dumps({"conflicts": []})), # critic
        ]

        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=groq_responses)
            mock_cls.return_value = mock_client

            from app.regeneration.service import regenerate_trip
            await regenerate_trip(
                db=mock_db,
                http=mock_http,
                trip_id=TRIP_ID,
                request=RegenerateRequest(scope=RegenerateScope.day, day_number=1),
            )

        # Verify a new itinerary version was inserted
        mock_db.table.return_value.insert.assert_called_once()
        # Verify the old one was deactivated
        mock_db.table.return_value.update.assert_called()

    @pytest.mark.asyncio
    async def test_day_regen_forwards_constraint_to_agent(self, mock_http):
        """Day regeneration should forward the optional natural-language constraint."""
        from app.planning.schemas import DayPlan
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)

        regenerated_day = DayPlan.model_validate(MOCK_SYNTHESIZER_JSON["days"][0])

        with patch("app.regeneration.service.DayRegenerationAgent.regenerate_day", new=AsyncMock(return_value=regenerated_day)) as mock_regen:
            with patch("app.regeneration.service.CriticAgent.run_critique", new=AsyncMock(return_value=[])):
                from app.regeneration.service import regenerate_trip
                await regenerate_trip(
                    db=mock_db,
                    http=mock_http,
                    trip_id=TRIP_ID,
                    request=RegenerateRequest(
                        scope=RegenerateScope.day,
                        day_number=1,
                        constraint="avoid temples",
                    ),
                )

        assert mock_regen.await_args.args[3] == "avoid temples"

    @pytest.mark.asyncio
    async def test_block_regen_preserves_start_end_times(self, mock_http):
        """Regenerated block must keep original start_time and end_time."""
        import copy
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)

        # Return a block with different times — service should override them
        fake_block = copy.deepcopy(MOCK_SYNTHESIZER_JSON["days"][0]["morning"])
        fake_block["start_time"] = "06:00"
        fake_block["end_time"] = "08:00"

        groq_responses = [
            _text_response(json.dumps(fake_block)),
            _text_response(json.dumps({"conflicts": []})),
        ]

        inserted_data: dict = {}

        async def capture_insert(data):
            inserted_data.update(data)
            return MagicMock(data=[ITINERARY_ROW])

        mock_db.table.return_value.insert.return_value.execute = AsyncMock(
            side_effect=lambda: capture_insert({})
        )

        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=groq_responses)
            mock_cls.return_value = mock_client

            from app.regeneration.service import _regen_block
            original_itinerary = ItinerarySchema.model_validate(MOCK_SYNTHESIZER_JSON)
            from app.planning.schemas import ResearchBundle
            research = ResearchBundle(destination="Tokyo", prompt="test", total_days=3)

            patched_itinerary = await _regen_block(
                mock_http, original_itinerary, research, 1, "morning", None
            )

        morning = patched_itinerary.days[0].morning
        # Times should be preserved from original (09:00 / 12:00)
        assert morning.start_time == "09:00"
        assert morning.end_time == "12:00"
        # Other days untouched
        assert patched_itinerary.days[1].day_number == 2
        assert patched_itinerary.days[2].day_number == 3

    @pytest.mark.asyncio
    async def test_block_regen_forwards_constraint_to_agent(self, mock_http):
        """Block regeneration should forward the optional natural-language constraint."""
        from app.planning.schemas import TimeBlock
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)

        regenerated_block = TimeBlock.model_validate(MOCK_SYNTHESIZER_JSON["days"][0]["morning"])

        with patch("app.regeneration.service.BlockRegenerationAgent.regenerate_block", new=AsyncMock(return_value=regenerated_block)) as mock_regen:
            with patch("app.regeneration.service.CriticAgent.run_critique", new=AsyncMock(return_value=[])):
                from app.regeneration.service import regenerate_trip
                await regenerate_trip(
                    db=mock_db,
                    http=mock_http,
                    trip_id=TRIP_ID,
                    request=RegenerateRequest(
                        scope=RegenerateScope.single_block,
                        day_number=1,
                        block_label="morning",
                        constraint="make breakfast lighter",
                    ),
                )

        assert mock_regen.await_args.args[4] == "make breakfast lighter"

    @pytest.mark.asyncio
    async def test_regen_increments_version(self, mock_http):
        """New itinerary row should have version = current_version + 1."""
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)

        groq_responses = [
            _text_response(json.dumps(MOCK_SYNTHESIZER_JSON)),
            _text_response(json.dumps({"conflicts": []})),
        ]

        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=groq_responses)
            mock_cls.return_value = mock_client

            with patch("app.regeneration.repository.insert_new_version", new=AsyncMock()) as mock_insert:
                from app.regeneration.service import regenerate_trip
                await regenerate_trip(
                    db=mock_db,
                    http=mock_http,
                    trip_id=TRIP_ID,
                    request=RegenerateRequest(scope=RegenerateScope.full_trip),
                )

            # version arg is the 3rd positional arg to insert_new_version
            call_args = mock_insert.call_args
            version_passed = call_args.args[2]  # (db, trip_id, version, ...)
            assert version_passed == ITINERARY_ROW["version"] + 1

    @pytest.mark.asyncio
    async def test_regen_persists_combined_pre_and_llm_conflicts(self, mock_http):
        """insert_new_version should receive deterministic and critic conflicts together."""
        from app.planning.schemas import Conflict, ItinerarySchema
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)

        pre_conflict = Conflict(
            type="timing",
            severity="warning",
            day_number=1,
            description="Block is too packed",
            activities=["Senso-ji Temple"],
        )
        llm_conflict = Conflict(
            type="persona",
            severity="warning",
            day_number=2,
            description="Nightlife choice is too intense for this traveler",
            activities=["Golden Gai"],
        )

        with patch("app.regeneration.service.SynthesizerAgent.run_synthesis", new=AsyncMock(return_value=ItinerarySchema.model_validate(MOCK_SYNTHESIZER_JSON))):
            with patch("app.regeneration.service.run_conflict_checks", return_value=[pre_conflict]):
                with patch("app.regeneration.service.CriticAgent.run_critique", new=AsyncMock(return_value=[llm_conflict])):
                    with patch("app.regeneration.repository.insert_new_version", new=AsyncMock()) as mock_insert:
                        from app.regeneration.service import regenerate_trip
                        await regenerate_trip(
                            db=mock_db,
                            http=mock_http,
                            trip_id=TRIP_ID,
                            request=RegenerateRequest(scope=RegenerateScope.full_trip),
                        )

        persisted_conflicts = mock_insert.await_args.args[5]
        assert [c.type for c in persisted_conflicts] == ["timing", "persona"]
        assert persisted_conflicts[0].description == "Block is too packed"
        assert persisted_conflicts[1].description.startswith("Nightlife choice")

    @pytest.mark.asyncio
    async def test_missing_itinerary_raises_trip_not_found(self, mock_http):
        """If no active itinerary exists, TripNotFoundError should be raised."""
        from app.core.exceptions import TripNotFoundError
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)
        # Override active itinerary query to return empty
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute = (
            AsyncMock(return_value=MagicMock(data=[]))
        )

        from app.regeneration.service import regenerate_trip
        with pytest.raises(TripNotFoundError):
            await regenerate_trip(
                db=mock_db,
                http=mock_http,
                trip_id=TRIP_ID,
                request=RegenerateRequest(scope=RegenerateScope.full_trip),
            )

    @pytest.mark.asyncio
    async def test_day_regen_invalid_target_raises_before_agent_call(self, mock_http):
        """Invalid day_number should fail before the day regeneration agent is called."""
        from app.core.exceptions import InvalidRegenerationTargetError
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)

        with patch("app.regeneration.service.DayRegenerationAgent.regenerate_day", new=AsyncMock()) as mock_regen:
            from app.regeneration.service import regenerate_trip
            with pytest.raises(InvalidRegenerationTargetError):
                await regenerate_trip(
                    db=mock_db,
                    http=mock_http,
                    trip_id=TRIP_ID,
                    request=RegenerateRequest(scope=RegenerateScope.day, day_number=9),
                )

        mock_regen.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_regen_deactivates_all_active_versions_for_trip(self, mock_http):
        """Version swap should deactivate all active rows for the trip, not a single itinerary id."""
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)

        groq_responses = [
            _text_response(json.dumps(MOCK_SYNTHESIZER_JSON)),
            _text_response(json.dumps({"conflicts": []})),
        ]

        with patch("app.planning.agents.base_agent.openai.AsyncOpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(side_effect=groq_responses)
            mock_cls.return_value = mock_client

            from app.regeneration.service import regenerate_trip
            await regenerate_trip(
                db=mock_db,
                http=mock_http,
                trip_id=TRIP_ID,
                request=RegenerateRequest(scope=RegenerateScope.full_trip),
            )

        mock_db.table.return_value.update.assert_any_call({"is_active": False})
        deactivate_chain = mock_db.table.return_value.update.return_value.eq.return_value.eq.return_value
        deactivate_chain.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_block_regen_invalid_target_raises_before_agent_call(self, mock_http):
        """Invalid day_number should fail before the block regeneration agent is called."""
        from app.core.exceptions import InvalidRegenerationTargetError
        from app.regeneration.schemas import RegenerateRequest, RegenerateScope

        mock_db = MagicMock()
        _wire_db(mock_db)

        with patch("app.regeneration.service.BlockRegenerationAgent.regenerate_block", new=AsyncMock()) as mock_regen:
            from app.regeneration.service import regenerate_trip
            with pytest.raises(InvalidRegenerationTargetError):
                await regenerate_trip(
                    db=mock_db,
                    http=mock_http,
                    trip_id=TRIP_ID,
                    request=RegenerateRequest(scope=RegenerateScope.single_block, day_number=9, block_label="morning"),
                )

        mock_regen.assert_not_awaited()
