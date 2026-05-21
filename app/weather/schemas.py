from pydantic import BaseModel, Field


class WeatherRequest(BaseModel):
    lat: float | None = Field(None, ge=-90, le=90)
    lon: float | None = Field(None, ge=-180, le=180)
    city: str | None = None
    days: int = Field(5, ge=1, le=16)


class DayWeather(BaseModel):
    date: str
    temperature_max: float
    temperature_min: float
    precipitation_mm: float
    weather_code: int
    description: str


class WeatherResponse(BaseModel):
    lat: float
    lon: float
    timezone: str
    days: list[DayWeather]
