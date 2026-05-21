from pydantic import BaseModel, Field


class PlaceQuery(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    category: str
    radius: int = Field(1000, ge=100, le=50000)


class PlaceResult(BaseModel):
    osm_id: int
    name: str
    lat: float
    lon: float
    category: str
    tags: dict[str, str] = {}


class PlacesResponse(BaseModel):
    lat: float
    lon: float
    category: str
    radius_m: int
    places: list[PlaceResult]
