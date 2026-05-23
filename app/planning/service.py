import uuid
from typing import Optional

import httpx
from supabase import AsyncClient

from app.common.logger import get_logger
from app.planning.agents.critic_agent import CriticAgent
from app.planning.agents.synthesizer_agent import SynthesizerAgent
from app.planning.conflict_checker import run_conflict_checks
from app.planning.research_fetcher import fetch_research
from app.planning.schemas import Conflict, ItinerarySchema, ResearchBundle
from app.trips import repository as trip_repo

logger = get_logger(__name__)


async def run_planning_pipeline(
    db: AsyncClient,
    http: httpx.AsyncClient,
    trip_id: str,
    prompt: str,
    destination: str,
    total_days: int,
    start_date: Optional[str] = None,
    budget: Optional[str] = None,
    persona_hint: Optional[str] = None,
    interests: Optional[list[str]] = None,
    constraints: Optional[list[str]] = None,
    travel_party: Optional[str] = None,
) -> ItinerarySchema:
    """Researcher → Planner → Synthesizer → Critic. Saves results to DB. Raises on failure."""
    await trip_repo.update_trip_status(db, trip_id, "generating")

    try:
        logger.info("trip=%s step=researcher", trip_id)
        research: ResearchBundle = await fetch_research(
            http=http,
            destination=destination,
            total_days=total_days,
            start_date=start_date,
            budget=budget,
            interests=interests,
            prompt=prompt,
            persona_hint=persona_hint,
            constraints=constraints,
            travel_party=travel_party,
        )

        logger.info("trip=%s step=synthesizer", trip_id)
        synthesizer = SynthesizerAgent(http)
        itinerary: ItinerarySchema = await synthesizer.run_synthesis(
            prompt=prompt,
            research=research,
            persona_hint=persona_hint,
            interests=interests,
            constraints=constraints,
            travel_party=travel_party,
        )

        logger.info("trip=%s step=conflict_check", trip_id)
        pre_conflicts = run_conflict_checks(itinerary)

        # Persist initial itinerary before critic so callers get the trip quickly.
        itinerary_id = await _persist_initial(db, trip_id, itinerary, research, itinerary.persona, pre_conflicts)

        logger.info("trip=%s step=critic pre_conflicts=%d", trip_id, len(pre_conflicts))
        critic = CriticAgent(http)
        llm_conflicts = await critic.run_critique(itinerary, pre_conflicts, research)

        logger.info("trip=%s total_conflicts=%d", trip_id, len(pre_conflicts) + len(llm_conflicts))
        await _persist_conflicts(db, itinerary_id, llm_conflicts)

        return itinerary

    except Exception as exc:
        logger.error("trip=%s pipeline failed: %s", trip_id, exc)
        await trip_repo.update_trip_status(db, trip_id, "failed")
        raise


async def _persist_initial(
    db: AsyncClient,
    trip_id: str,
    itinerary: ItinerarySchema,
    research: ResearchBundle,
    persona: str,
    pre_conflicts: list[Conflict],
) -> str:
    """Save trip + itinerary with deterministic conflicts. Returns itinerary_id."""
    await db.table("trips").update(
        {
            "title": itinerary.title,
            "summary": itinerary.summary,
            "persona": persona,
            "destination": itinerary.destination,
            "total_days": itinerary.total_days,
            "status": "completed",
        }
    ).eq("id", trip_id).execute()

    itinerary_id = str(uuid.uuid4())
    await db.table("itineraries").insert(
        {
            "id": itinerary_id,
            "trip_id": trip_id,
            "version": 1,
            "itinerary_data": itinerary.model_dump(),
            "weather_data": research.weather,
            "places_data": research.places,
            "conflicts": [c.model_dump() for c in pre_conflicts],
            "reasoning": {},
            "is_active": True,
        }
    ).execute()

    return itinerary_id


async def _persist_conflicts(
    db: AsyncClient,
    itinerary_id: str,
    llm_conflicts: list[Conflict],
) -> None:
    """Append LLM critic conflicts to the itinerary row."""
    if not llm_conflicts:
        return
    existing = await db.table("itineraries").select("conflicts").eq("id", itinerary_id).single().execute()
    current: list[dict] = existing.data.get("conflicts", []) if existing.data else []
    updated = current + [c.model_dump() for c in llm_conflicts]
    await db.table("itineraries").update({"conflicts": updated}).eq("id", itinerary_id).execute()
