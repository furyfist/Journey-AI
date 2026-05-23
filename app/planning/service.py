import uuid
from typing import Optional

import httpx
from supabase import AsyncClient

from app.common.logger import get_logger
from app.planning.agents.critic_agent import CriticAgent
from app.planning.agents.planner_agent import PlannerAgent
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

        logger.info("trip=%s step=planner", trip_id)
        planner = PlannerAgent(http)
        rough_plan: dict = await planner.run_planning(prompt, research)

        logger.info("trip=%s step=synthesizer", trip_id)
        synthesizer = SynthesizerAgent(http)
        itinerary: ItinerarySchema = await synthesizer.run_synthesis(prompt, research, rough_plan)

        logger.info("trip=%s step=conflict_check", trip_id)
        pre_conflicts = run_conflict_checks(itinerary)

        logger.info("trip=%s step=critic pre_conflicts=%d", trip_id, len(pre_conflicts))
        critic = CriticAgent(http)
        llm_conflicts = await critic.run_critique(itinerary, pre_conflicts, research)

        all_conflicts = pre_conflicts + llm_conflicts
        logger.info("trip=%s total_conflicts=%d", trip_id, len(all_conflicts))

        await _persist(
            db, trip_id, itinerary, research,
            rough_plan.get("persona", itinerary.persona),
            all_conflicts,
        )
        return itinerary

    except Exception as exc:
        logger.error("trip=%s pipeline failed: %s", trip_id, exc)
        await trip_repo.update_trip_status(db, trip_id, "failed")
        raise


async def _persist(
    db: AsyncClient,
    trip_id: str,
    itinerary: ItinerarySchema,
    research: ResearchBundle,
    persona: str,
    conflicts: list[Conflict],
) -> None:
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

    await db.table("itineraries").insert(
        {
            "id": str(uuid.uuid4()),
            "trip_id": trip_id,
            "version": 1,
            "itinerary_data": itinerary.model_dump(),
            "weather_data": research.weather,
            "places_data": research.places,
            "conflicts": [c.model_dump() for c in conflicts],
            "reasoning": {},
            "is_active": True,
        }
    ).execute()
