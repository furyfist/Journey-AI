import uuid
from typing import Optional

import httpx
from supabase import AsyncClient

from app.trips import repository
from app.trips.schemas import TripCreate


async def create_trip(db: AsyncClient, http: httpx.AsyncClient, payload: TripCreate) -> dict:
    destination = payload.destination or "Unknown"
    data = {
        "id": str(uuid.uuid4()),
        "prompt": payload.prompt,
        "destination": destination,
        "budget": payload.budget,
        "travel_dates": (
            {"start": payload.start_date, "end": payload.end_date}
            if payload.start_date
            else None
        ),
        "total_days": payload.total_days or 5,
        "title": f"Trip to {destination}",
        "status": "pending",
    }
    trip = await repository.insert_trip(db, data)
    trip_id = trip["id"]

    from app.planning import service as planning_service
    from app.common.logger import get_logger

    logger = get_logger(__name__)
    try:
        await planning_service.run_planning_pipeline(
            db=db,
            http=http,
            trip_id=trip_id,
            prompt=payload.prompt,
            destination=destination,
            total_days=payload.total_days or 5,
            start_date=payload.start_date,
            budget=payload.budget,
        )
    except Exception as exc:
        logger.error("planning pipeline failed for trip=%s: %s", trip_id, exc)
        # Pipeline already set status to "failed" on its own error path

    return await repository.fetch_trip_by_id(db, trip_id)


async def list_trips(db: AsyncClient, user_id: Optional[str] = None) -> list[dict]:
    return await repository.fetch_trips(db, user_id)


async def get_trip(db: AsyncClient, trip_id: str) -> dict:
    return await repository.fetch_trip_detail(db, trip_id)


async def delete_trip(db: AsyncClient, trip_id: str) -> None:
    await repository.fetch_trip_by_id(db, trip_id)
    await repository.remove_trip(db, trip_id)
