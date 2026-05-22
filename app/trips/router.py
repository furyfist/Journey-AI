import json
from uuid import UUID

from fastapi import APIRouter, status
from sse_starlette.sse import EventSourceResponse

from app.core.dependencies import DBDep, HttpDep
from app.planning.schemas import SSEEvent
from app.planning.stream_service import stream_planning_pipeline
from app.trips import service
from app.trips.schemas import TripCreate, TripDetail, TripListItem, TripResponse

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(payload: TripCreate, db: DBDep):
    """
    Create a pending trip row.
    Connect to GET /api/v1/trips/{trip_id}/stream to run the AI pipeline.
    """
    return await service.create_trip(db, payload)


@router.get("/{trip_id}/stream")
async def stream_trip(trip_id: UUID, db: DBDep, http: HttpDep):
    """
    SSE endpoint — runs the full AI pipeline for an existing pending trip and
    streams typed events to the client in real time.

    Event types: agent_start | tool_call | tool_result | agent_complete |
                 conflict_detected | trip_complete | error | keepalive
    """
    # Fetch trip to resolve prompt / destination / days before streaming.
    from app.trips import repository as repo
    trip = await repo.fetch_trip_by_id(db, str(trip_id))

    travel_dates = trip.get("travel_dates") or {}
    start_date = travel_dates.get("start") if isinstance(travel_dates, dict) else None

    async def event_generator():
        async for event in stream_planning_pipeline(
            db=db,
            http=http,
            trip_id=str(trip_id),
            prompt=trip["prompt"],
            destination=trip["destination"],
            total_days=trip.get("total_days", 5),
            start_date=start_date,
            budget=trip.get("budget"),
        ):
            yield {
                "event": event.event,
                "data": json.dumps(event.model_dump(exclude_none=True), default=str),
            }

    return EventSourceResponse(event_generator())


@router.get("", response_model=list[TripListItem])
async def list_trips(db: DBDep):
    """List all trips. Will be scoped by user in Session 5 (auth)."""
    return await service.list_trips(db)


@router.get("/{trip_id}", response_model=TripDetail)
async def get_trip(trip_id: UUID, db: DBDep):
    """Full trip detail including the active itinerary if generation is complete."""
    return await service.get_trip(db, str(trip_id))


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(trip_id: UUID, db: DBDep):
    await service.delete_trip(db, str(trip_id))
