from uuid import UUID

from fastapi import APIRouter, status

from app.core.dependencies import DBDep
from app.trips import service
from app.trips.schemas import TripCreate, TripDetail, TripListItem, TripResponse

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(payload: TripCreate, db: DBDep):
    """
    Create a new trip from a natural language prompt.
    Returns immediately with status 'pending'. The AI pipeline will be
    triggered in Session 3 — for now the record is saved and ready.
    """
    trip = await service.create_trip(db, payload)
    return trip


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
