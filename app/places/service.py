import httpx

from app.places.client import query_places
from app.places.schemas import PlaceResult, PlacesResponse


async def fetch_places(
    http: httpx.AsyncClient,
    lat: float,
    lon: float,
    category: str,
    radius_m: int,
) -> PlacesResponse:
    raw = await query_places(http, lat, lon, category, radius_m)

    results: list[PlaceResult] = []
    for node in raw.get("elements", []):
        tags: dict = node.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
        results.append(
            PlaceResult(
                osm_id=node["id"],
                name=name,
                lat=node["lat"],
                lon=node["lon"],
                category=category,
                tags={k: v for k, v in tags.items() if k != "name"},
            )
        )

    return PlacesResponse(
        lat=lat,
        lon=lon,
        category=category,
        radius_m=radius_m,
        places=results,
    )
