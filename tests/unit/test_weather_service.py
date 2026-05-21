from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.constants import WMO_WEATHER_CODES
from app.weather import service
from app.weather.schemas import DayWeather, WeatherResponse
from tests.mocks.mock_weather_data import OPEN_METEO_FORECAST_RESPONSE


def _make_http(json_response: dict) -> AsyncMock:
    resp = MagicMock()
    resp.json.return_value = json_response
    resp.raise_for_status = MagicMock()
    http = AsyncMock()
    http.get = AsyncMock(return_value=resp)
    return http


@pytest.mark.asyncio
async def test_fetch_weather_returns_response_model():
    http = _make_http(OPEN_METEO_FORECAST_RESPONSE)
    result = await service.fetch_weather(http, 35.67, 139.65, None, 3)

    assert isinstance(result, WeatherResponse)
    assert result.lat == 35.67
    assert result.lon == 139.65
    assert result.timezone == "Asia/Tokyo"
    assert len(result.days) == 3


@pytest.mark.asyncio
async def test_wmo_codes_mapped_to_descriptions():
    http = _make_http(OPEN_METEO_FORECAST_RESPONSE)
    result = await service.fetch_weather(http, 35.67, 139.65, None, 3)

    assert result.days[0].description == WMO_WEATHER_CODES[0]   # "Clear sky"
    assert result.days[1].description == WMO_WEATHER_CODES[61]  # "Slight rain"
    assert result.days[2].description == WMO_WEATHER_CODES[3]   # "Overcast"


@pytest.mark.asyncio
async def test_unknown_wmo_code_returns_unknown():
    raw = {
        **OPEN_METEO_FORECAST_RESPONSE,
        "daily": {
            **OPEN_METEO_FORECAST_RESPONSE["daily"],
            "time": ["2026-06-01"],
            "temperature_2m_max": [25.0],
            "temperature_2m_min": [18.0],
            "precipitation_sum": [0.0],
            "weathercode": [999],
        },
    }
    http = _make_http(raw)
    result = await service.fetch_weather(http, 35.67, 139.65, None, 1)
    assert result.days[0].description == "Unknown"


@pytest.mark.asyncio
async def test_null_precipitation_coerced_to_zero():
    http = _make_http(OPEN_METEO_FORECAST_RESPONSE)
    result = await service.fetch_weather(http, 35.67, 139.65, None, 3)
    # Third day has None precipitation in the fixture
    assert result.days[2].precipitation_mm == 0.0


@pytest.mark.asyncio
async def test_day_weather_schema_fields():
    http = _make_http(OPEN_METEO_FORECAST_RESPONSE)
    result = await service.fetch_weather(http, 35.67, 139.65, None, 3)
    day = result.days[0]

    assert isinstance(day, DayWeather)
    assert day.date == "2026-06-01"
    assert day.temperature_max == 28.5
    assert day.temperature_min == 21.0
    assert day.weather_code == 0


@pytest.mark.asyncio
async def test_city_triggers_geocode_then_forecast():
    geocode_resp = MagicMock()
    geocode_resp.json.return_value = {
        "results": [{"latitude": 35.6895, "longitude": 139.6917, "name": "Tokyo"}]
    }
    geocode_resp.raise_for_status = MagicMock()

    forecast_resp = MagicMock()
    forecast_resp.json.return_value = OPEN_METEO_FORECAST_RESPONSE
    forecast_resp.raise_for_status = MagicMock()

    http = AsyncMock()
    http.get = AsyncMock(side_effect=[geocode_resp, forecast_resp])

    result = await service.fetch_weather(http, None, None, "Tokyo", 3)
    assert isinstance(result, WeatherResponse)
    assert http.get.call_count == 2
