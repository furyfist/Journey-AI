import httpx

from app.core.config import settings
from app.core.exceptions import ExternalAPIError


async def get_forecast(http: httpx.AsyncClient, lat: float, lon: float, days: int) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
        "forecast_days": days,
        "timezone": "auto",
    }
    try:
        resp = await http.get(f"{settings.open_meteo_base_url}/forecast", params=params)
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ExternalAPIError(f"Open-Meteo forecast error: {exc.response.status_code}") from exc
    except httpx.RequestError as exc:
        raise ExternalAPIError(f"Open-Meteo request failed: {exc}") from exc
    return resp.json()


async def geocode_city(http: httpx.AsyncClient, city_name: str) -> tuple[float, float]:
    params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
    try:
        resp = await http.get(settings.geocoding_api_url, params=params)
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ExternalAPIError(f"Geocoding error: {exc.response.status_code}") from exc
    except httpx.RequestError as exc:
        raise ExternalAPIError(f"Geocoding request failed: {exc}") from exc

    data = resp.json()
    results = data.get("results")
    if not results:
        raise ExternalAPIError(f"No geocoding results for city: {city_name!r}")
    return results[0]["latitude"], results[0]["longitude"]
