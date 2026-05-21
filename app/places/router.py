from fastapi import APIRouter, Query

from app.common.constants import OSM_TAG_GROUPS
from app.core.dependencies import HttpDep
from app.core.exceptions import ExternalAPIError
from app.places import service
from app.places.schemas import PlacesResponse

router = APIRouter(prefix="/places", tags=["places"])

_VALID_CATEGORIES = sorted(OSM_TAG_GROUPS.keys())


@router.get("", response_model=PlacesResponse)
async def get_places(
    http: HttpDep,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    category: str = Query(..., description=f"One of: {', '.join(_VALID_CATEGORIES)}"),
    radius: int = Query(1000, ge=100, le=50000),
):
    """
    Return nearby places for a given category using the Overpass API.
    Valid categories: attractions, food, nature, nightlife.
    """
    if category not in OSM_TAG_GROUPS:
        raise ExternalAPIError(f"Unknown category {category!r}. Valid: {_VALID_CATEGORIES}")
    return await service.fetch_places(http, lat, lon, category, radius)
