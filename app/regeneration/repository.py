import uuid

from supabase import AsyncClient

from app.planning.schemas import Conflict, ItinerarySchema, ResearchBundle


async def fetch_active_itinerary(db: AsyncClient, trip_id: str) -> dict | None:
    result = (
        await db.table("itineraries")
        .select("*")
        .eq("trip_id", trip_id)
        .eq("is_active", True)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


async def deactivate_active_itineraries(db: AsyncClient, trip_id: str) -> None:
    await (
        db.table("itineraries")
        .update({"is_active": False})
        .eq("trip_id", trip_id)
        .eq("is_active", True)
        .execute()
    )


async def insert_new_version(
    db: AsyncClient,
    trip_id: str,
    version: int,
    itinerary: ItinerarySchema,
    research: ResearchBundle,
    conflicts: list[Conflict],
) -> None:
    await db.table("itineraries").insert(
        {
            "id": str(uuid.uuid4()),
            "trip_id": trip_id,
            "version": version,
            "itinerary_data": itinerary.model_dump(),
            "weather_data": research.weather,
            "places_data": research.places,
            "conflicts": [c.model_dump() for c in conflicts],
            "reasoning": {},
            "is_active": True,
        }
    ).execute()
