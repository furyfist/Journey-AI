import httpx

from app.places.service import fetch_places

TOOL_NAME = "search_places"


async def execute(http: httpx.AsyncClient, args: dict) -> dict:
    lat = float(args["lat"])
    lon = float(args["lon"])
    category = args.get("category", "attractions")
    radius = max(500, min(int(args.get("radius", 5000)), 20000))
    response = await fetch_places(http, lat=lat, lon=lon, category=category, radius_m=radius)
    return response.model_dump()
