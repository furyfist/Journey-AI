import uuid
from typing import Optional

from supabase import AsyncClient

from app.trips import repository
from app.trips.schemas import TripCreate


async def create_trip(db: AsyncClient, payload: TripCreate) -> dict:
    """Insert a pending trip row and return it. Pipeline is triggered via GET /trips/{id}/stream."""
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
    return await repository.insert_trip(db, data)


async def list_trips(db: AsyncClient, user_id: Optional[str] = None) -> list[dict]:
    return await repository.fetch_trips(db, user_id)


async def get_trip(db: AsyncClient, trip_id: str) -> dict:
    return await repository.fetch_trip_detail(db, trip_id)


async def delete_trip(db: AsyncClient, trip_id: str) -> None:
    await repository.fetch_trip_by_id(db, trip_id)
    await repository.remove_trip(db, trip_id)
