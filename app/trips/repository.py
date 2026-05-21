from supabase import AsyncClient

from app.core.exceptions import TripNotFoundError


async def insert_trip(db: AsyncClient, payload: dict) -> dict:
    result = await db.table("trips").insert(payload).execute()
    return result.data[0]


async def fetch_trips(db: AsyncClient, user_id: str | None = None) -> list[dict]:
    query = db.table("trips").select("id, title, destination, total_days, status, created_at")
    if user_id:
        query = query.eq("user_id", user_id)
    result = await query.order("created_at", desc=True).execute()
    return result.data


async def fetch_trip_by_id(db: AsyncClient, trip_id: str) -> dict:
    result = (
        await db.table("trips")
        .select("*")
        .eq("id", trip_id)
        .single()
        .execute()
    )
    if not result.data:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return result.data


async def fetch_trip_detail(db: AsyncClient, trip_id: str) -> dict:
    """Joins trips with the active itinerary in a single query."""
    trip = await fetch_trip_by_id(db, trip_id)

    itinerary_result = (
        await db.table("itineraries")
        .select("itinerary_data, conflicts, reasoning, weather_data")
        .eq("trip_id", trip_id)
        .eq("is_active", True)
        .limit(1)
        .execute()
    )

    if itinerary_result.data:
        row = itinerary_result.data[0]
        trip["itinerary"] = row.get("itinerary_data")
        trip["conflicts"] = row.get("conflicts") or []
        trip["reasoning"] = row.get("reasoning") or {}
        trip["weather_data"] = row.get("weather_data")
    else:
        trip.setdefault("itinerary", None)
        trip.setdefault("conflicts", [])
        trip.setdefault("reasoning", {})
        trip.setdefault("weather_data", None)

    return trip


async def remove_trip(db: AsyncClient, trip_id: str) -> None:
    await db.table("trips").delete().eq("id", trip_id).execute()


async def update_trip_status(db: AsyncClient, trip_id: str, status: str) -> None:
    await db.table("trips").update({"status": status}).eq("id", trip_id).execute()
