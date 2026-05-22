"""
Regeneration service — partial or full replanning of an existing trip.

All scopes use cached weather/places from the stored itinerary so there are
no extra API calls.  After regeneration the old itinerary row is flipped to
is_active=false and a new row is inserted with version + 1.
"""

import copy

import httpx
from supabase import AsyncClient

from app.common.logger import get_logger
from app.core.exceptions import TripNotFoundError
from app.planning.agents.critic_agent import CriticAgent
from app.planning.agents.planner_agent import PlannerAgent
from app.planning.agents.regeneration_agent import BlockRegenerationAgent, DayRegenerationAgent
from app.planning.agents.synthesizer_agent import SynthesizerAgent
from app.planning.conflict_checker import run_conflict_checks
from app.planning.prompt_builder import regen_full_user_message
from app.planning.schemas import Conflict, DayPlan, ItinerarySchema, ResearchBundle, TimeBlock
from app.regeneration import repository as regen_repo
from app.regeneration.schemas import RegenerateRequest, RegenerateScope
from app.trips import repository as trip_repo

logger = get_logger(__name__)


async def regenerate_trip(
    db: AsyncClient,
    http: httpx.AsyncClient,
    trip_id: str,
    request: RegenerateRequest,
) -> dict:
    """
    Regenerate a trip at the requested scope.
    Returns the updated TripDetail dict (same shape as GET /trips/{id}).
    """
    trip = await trip_repo.fetch_trip_by_id(db, trip_id)

    itinerary_row = await regen_repo.fetch_active_itinerary(db, trip_id)
    if not itinerary_row:
        raise TripNotFoundError(f"No active itinerary found for trip {trip_id} — run the stream pipeline first")

    current_itinerary = ItinerarySchema.model_validate(itinerary_row["itinerary_data"])
    current_version: int = itinerary_row.get("version", 1)

    # Restore ResearchBundle from cached data — no new API calls.
    research = ResearchBundle(
        destination=trip["destination"],
        prompt=trip["prompt"],
        total_days=trip.get("total_days", 5),
        weather=itinerary_row.get("weather_data"),
        places=itinerary_row.get("places_data") or {},
        budget=trip.get("budget"),
    )

    logger.info("trip=%s scope=%s version=%d→%d", trip_id, request.scope, current_version, current_version + 1)

    if request.scope == RegenerateScope.full_trip:
        new_itinerary = await _regen_full(http, trip, research, request.constraint)

    elif request.scope == RegenerateScope.day:
        new_itinerary = await _regen_day(
            http, current_itinerary, research, request.day_number, request.constraint  # type: ignore[arg-type]
        )

    else:  # single_block
        new_itinerary = await _regen_block(
            http, current_itinerary, research,
            request.day_number, request.block_label,  # type: ignore[arg-type]
            request.constraint,
        )

    # Run full conflict pass on the new itinerary.
    pre_conflicts = run_conflict_checks(new_itinerary)
    critic = CriticAgent(http)
    llm_conflicts = await critic.run_critique(new_itinerary, pre_conflicts, research)
    all_conflicts: list[Conflict] = pre_conflicts + llm_conflicts

    # Atomic version swap: deactivate old → insert new.
    await regen_repo.deactivate_itinerary(db, itinerary_row["id"])
    await regen_repo.insert_new_version(
        db, trip_id, current_version + 1, new_itinerary, research, all_conflicts
    )

    logger.info("trip=%s regeneration complete conflicts=%d", trip_id, len(all_conflicts))
    return await trip_repo.fetch_trip_detail(db, trip_id)


# ---------------------------------------------------------------------------
# Scope handlers
# ---------------------------------------------------------------------------

async def _regen_full(
    http: httpx.AsyncClient,
    trip: dict,
    research: ResearchBundle,
    constraint: str | None,
) -> ItinerarySchema:
    """Re-run planner + synthesizer with cached research + optional constraint."""
    planner = PlannerAgent(http)
    augmented_prompt = trip["prompt"]
    if constraint:
        augmented_prompt = f"{augmented_prompt}. Additional constraint: {constraint}"

    rough_plan: dict = await planner.run_planning(augmented_prompt, research)

    synthesizer = SynthesizerAgent(http)
    return await synthesizer.run_synthesis(augmented_prompt, research, rough_plan)


async def _regen_day(
    http: httpx.AsyncClient,
    itinerary: ItinerarySchema,
    research: ResearchBundle,
    day_number: int,
    constraint: str | None,
) -> ItinerarySchema:
    """Regenerate one day and return the full patched itinerary."""
    agent = DayRegenerationAgent(http)
    new_day: DayPlan = await agent.regenerate_day(day_number, itinerary, research, constraint)

    # Preserve original day_number and date to avoid drift.
    original_day = next((d for d in itinerary.days if d.day_number == day_number), None)
    if original_day:
        new_day = new_day.model_copy(update={
            "day_number": original_day.day_number,
            "date": original_day.date,
            "weather": original_day.weather,
        })

    patched = copy.deepcopy(itinerary)
    patched.days = [new_day if d.day_number == day_number else d for d in patched.days]
    return patched


async def _regen_block(
    http: httpx.AsyncClient,
    itinerary: ItinerarySchema,
    research: ResearchBundle,
    day_number: int,
    block_label: str,
    constraint: str | None,
) -> ItinerarySchema:
    """Regenerate one time block and return the full patched itinerary."""
    agent = BlockRegenerationAgent(http)
    new_block: TimeBlock = await agent.regenerate_block(
        day_number, block_label, itinerary, research, constraint
    )

    # Preserve start/end times so the block stays in its window.
    original_day = next((d for d in itinerary.days if d.day_number == day_number), None)
    if original_day:
        original_block: TimeBlock = getattr(original_day, block_label)
        new_block = new_block.model_copy(update={
            "label": original_block.label,
            "start_time": original_block.start_time,
            "end_time": original_block.end_time,
        })

    patched = copy.deepcopy(itinerary)
    new_days = []
    for day in patched.days:
        if day.day_number == day_number:
            day = day.model_copy(update={block_label: new_block})
        new_days.append(day)
    patched = patched.model_copy(update={"days": new_days})
    return patched
