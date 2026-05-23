import httpx

from app.weather.service import fetch_weather

TOOL_NAME = "get_weather"


async def execute(http: httpx.AsyncClient, args: dict) -> dict:
    city = args.get("city")
    days = max(1, min(int(args.get("days", 5)), 16))
    response = await fetch_weather(http, lat=None, lon=None, city=city, days=days)
    return response.model_dump()


async def fetch_weather_direct(
    http: httpx.AsyncClient,
    city: str,
    days: int,
    start_date: str | None = None,
) -> dict:
    """Direct call — no LLM overhead. Returns weather dict with lat/lon."""
    days = max(1, min(days, 16))
    response = await fetch_weather(http, lat=None, lon=None, city=city, days=days)
    return response.model_dump()
