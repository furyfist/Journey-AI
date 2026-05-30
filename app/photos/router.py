"""Photos API router.

Exposes a single endpoint:
    GET /photos/search?query=<destination>

The backend fetches from Unsplash, normalizes the result, and returns
it to the frontend without ever exposing the Unsplash credentials.
A fallback object (image_url: null, source: "fallback") is returned
instead of an error when Unsplash is unavailable.
"""

from fastapi import APIRouter, Query

from app.core.dependencies import HttpDep
from app.photos import service
from app.photos.schemas import PhotoSearchResponse

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/search", response_model=PhotoSearchResponse)
async def search_photo(
    http: HttpDep,
    query: str = Query(..., min_length=1, max_length=200, description="Destination or search term"),
) -> PhotoSearchResponse:
    """Return one normalized destination photo from Unsplash.

    Always returns HTTP 200.  When no photo is available the response
    will have ``image_url: null`` and ``source: "fallback"``.
    """
    result = await service.fetch_photo(http, query)
    return PhotoSearchResponse(**result.model_dump())
