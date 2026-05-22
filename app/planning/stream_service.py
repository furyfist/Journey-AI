"""
Streaming planning pipeline — async generator that yields SSEEvent objects.

Flow: agent_start → (tool_call / tool_result)* → agent_complete — for each agent.
After synthesizer: conflict_detected* → trip_complete (or error).
A keepalive is emitted every 15 s to satisfy proxies.
"""

import asyncio
from collections.abc import AsyncGenerator
from typing import Optional

import httpx
from supabase import AsyncClient

from app.common.logger import get_logger
from app.planning.agents.critic_agent import CriticAgent
from app.planning.agents.planner_agent import PlannerAgent
from app.planning.agents.researcher_agent import ResearcherAgent
from app.planning.agents.synthesizer_agent import SynthesizerAgent
from app.planning.conflict_checker import run_conflict_checks
from app.planning.schemas import Conflict, ItinerarySchema, ResearchBundle, SSEEvent
from app.trips import repository as trip_repo

logger = get_logger(__name__)

_KEEPALIVE_SECONDS = 15


async def stream_planning_pipeline(
    db: AsyncClient,
    http: httpx.AsyncClient,
    trip_id: str,
    prompt: str,
    destination: str,
    total_days: int,
    start_date: Optional[str] = None,
    budget: Optional[str] = None,
) -> AsyncGenerator[SSEEvent, None]:
    """
    Async generator — yield SSEEvent objects as each pipeline stage progresses.
    Saves the itinerary and conflicts to DB before yielding trip_complete.
    On any unrecoverable error, yields an error event and updates trip status.
    """
    await trip_repo.update_trip_status(db, trip_id, "generating")

    # Queue bridges agent callbacks → generator output.
    queue: asyncio.Queue[SSEEvent] = asyncio.Queue()

    async def on_event(payload: dict) -> None:
        await queue.put(SSEEvent(**payload))

    async def drain() -> AsyncGenerator[SSEEvent, None]:
        """Yield all events currently in the queue."""
        while not queue.empty():
            yield await queue.get()

    async def keepalive_loop(stop: asyncio.Event) -> None:
        while not stop.is_set():
            try:
                await asyncio.wait_for(stop.wait(), timeout=_KEEPALIVE_SECONDS)
            except asyncio.TimeoutError:
                await queue.put(SSEEvent(event="keepalive"))

    stop_keepalive = asyncio.Event()
    keepalive_task = asyncio.create_task(keepalive_loop(stop_keepalive))

    try:
        # ------------------------------------------------------------------ researcher
        yield SSEEvent(event="agent_start", agent="researcher", message="Gathering weather and places data")
        researcher = ResearcherAgent(http, on_event=on_event)
        research: ResearchBundle = await researcher.run_research(
            prompt=prompt, destination=destination, total_days=total_days,
            start_date=start_date, budget=budget,
        )
        async for ev in drain():
            yield ev
        yield SSEEvent(event="agent_complete", agent="researcher", message="Research complete")

        # ------------------------------------------------------------------ planner
        yield SSEEvent(event="agent_start", agent="planner", message="Building day-by-day schedule")
        planner = PlannerAgent(http, on_event=on_event)
        rough_plan: dict = await planner.run_planning(prompt, research)
        async for ev in drain():
            yield ev
        yield SSEEvent(event="agent_complete", agent="planner", message="Day structure ready")

        # ------------------------------------------------------------------ synthesizer
        yield SSEEvent(event="agent_start", agent="synthesizer", message="Generating full itinerary")
        synthesizer = SynthesizerAgent(http, on_event=on_event)
        itinerary: ItinerarySchema = await synthesizer.run_synthesis(prompt, research, rough_plan)
        async for ev in drain():
            yield ev
        yield SSEEvent(event="agent_complete", agent="synthesizer", message="Itinerary generated")

        # ------------------------------------------------------------------ conflict detection
        yield SSEEvent(event="agent_start", agent="conflict_checker", message="Running conflict checks")
        pre_conflicts = run_conflict_checks(itinerary)
        for c in pre_conflicts:
            yield SSEEvent(event="conflict_detected", agent="conflict_checker", data=c.model_dump())

        # ------------------------------------------------------------------ critic
        yield SSEEvent(event="agent_start", agent="critic", message="LLM quality review")
        critic = CriticAgent(http, on_event=on_event)
        llm_conflicts = await critic.run_critique(itinerary, pre_conflicts, research)
        async for ev in drain():
            yield ev
        for c in llm_conflicts:
            yield SSEEvent(event="conflict_detected", agent="critic", data=c.model_dump())
        yield SSEEvent(event="agent_complete", agent="critic", message=f"{len(llm_conflicts)} LLM conflict(s) found")

        # ------------------------------------------------------------------ persist
        all_conflicts: list[Conflict] = pre_conflicts + llm_conflicts
        await _persist(
            db, trip_id, itinerary, research,
            rough_plan.get("persona", itinerary.persona),
            all_conflicts,
        )

        yield SSEEvent(
            event="trip_complete",
            data={
                "trip_id": trip_id,
                "total_conflicts": len(all_conflicts),
                "destination": itinerary.destination,
                "title": itinerary.title,
            },
        )

    except Exception as exc:
        logger.error("trip=%s stream pipeline failed: %s", trip_id, exc)
        await trip_repo.update_trip_status(db, trip_id, "failed")
        yield SSEEvent(event="error", message=str(exc))

    finally:
        stop_keepalive.set()
        keepalive_task.cancel()
        try:
            await keepalive_task
        except asyncio.CancelledError:
            pass


async def _persist(
    db: AsyncClient,
    trip_id: str,
    itinerary: ItinerarySchema,
    research: ResearchBundle,
    persona: str,
    conflicts: list[Conflict],
) -> None:
    import uuid

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

    # Deactivate any existing active itinerary and determine next version number.
    existing = (
        await db.table("itineraries")
        .select("version")
        .eq("trip_id", trip_id)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )
    if existing.data:
        await db.table("itineraries").update({"is_active": False}).eq("trip_id", trip_id).eq("is_active", True).execute()
        next_version = existing.data[0]["version"] + 1
    else:
        next_version = 1

    await db.table("itineraries").insert(
        {
            "id": str(uuid.uuid4()),
            "trip_id": trip_id,
            "version": next_version,
            "itinerary_data": itinerary.model_dump(),
            "weather_data": research.weather,
            "places_data": research.places,
            "conflicts": [c.model_dump() for c in conflicts],
            "reasoning": {},
            "is_active": True,
        }
    ).execute()
