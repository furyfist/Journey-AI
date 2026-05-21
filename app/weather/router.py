from fastapi import APIRouter, Query

from app.core.dependencies import HttpDep
from app.core.exceptions import ExternalAPIError
from app.weather import service
from app.weather.schemas import WeatherResponse

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("", response_model=WeatherResponse)
async def get_weather(
    http: HttpDep,
    lat: float | None = Query(None, ge=-90, le=90),
    lon: float | None = Query(None, ge=-180, le=180),
    city: str | None = Query(None),
    days: int = Query(5, ge=1, le=16),
):
    """
    Fetch a multi-day weather forecast.
    Supply either lat+lon or city name (geocoded automatically).
    """
    if city is None and (lat is None or lon is None):
        raise ExternalAPIError("Provide either lat+lon or city query parameter")
    return await service.fetch_weather(http, lat, lon, city, days)
