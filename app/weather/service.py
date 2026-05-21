import httpx

from app.common.constants import WMO_WEATHER_CODES
from app.weather.client import geocode_city, get_forecast
from app.weather.schemas import DayWeather, WeatherResponse


async def fetch_weather(
    http: httpx.AsyncClient,
    lat: float | None,
    lon: float | None,
    city: str | None,
    days: int,
) -> WeatherResponse:
    if city and (lat is None or lon is None):
        lat, lon = await geocode_city(http, city)

    raw = await get_forecast(http, lat, lon, days)

    daily = raw["daily"]
    day_list = [
        DayWeather(
            date=daily["time"][i],
            temperature_max=daily["temperature_2m_max"][i],
            temperature_min=daily["temperature_2m_min"][i],
            precipitation_mm=daily["precipitation_sum"][i] or 0.0,
            weather_code=daily["weathercode"][i],
            description=WMO_WEATHER_CODES.get(daily["weathercode"][i], "Unknown"),
        )
        for i in range(len(daily["time"]))
    ]

    return WeatherResponse(
        lat=raw["latitude"],
        lon=raw["longitude"],
        timezone=raw["timezone"],
        days=day_list,
    )
