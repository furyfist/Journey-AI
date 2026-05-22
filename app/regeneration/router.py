from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import DBDep, HttpDep
from app.regeneration import service
from app.regeneration.schemas import RegenerateRequest
from app.trips.schemas import TripDetail

router = APIRouter(prefix="/trips", tags=["regeneration"])


@router.post("/{trip_id}/regenerate", response_model=TripDetail)
async def regenerate_trip(trip_id: UUID, payload: RegenerateRequest, db: DBDep, http: HttpDep):
    """
    Partially or fully replan an existing trip.

    - scope=full_trip   — re-run planner + synthesizer with optional constraint
    - scope=day         — regenerate one day (day_number required)
    - scope=single_block — regenerate one time block (day_number + block_label required)

    The previous itinerary version is preserved (is_active=false). The new version
    is returned immediately with updated conflicts.
    """
    return await service.regenerate_trip(db, http, str(trip_id), payload)
