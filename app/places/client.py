import httpx

from app.common.constants import OSM_TAG_GROUPS
from app.core.config import settings
from app.core.exceptions import ExternalAPIError


def _build_overpass_query(lat: float, lon: float, category: str, radius_m: int) -> str:
    tag_filters = OSM_TAG_GROUPS.get(category, [])
    if not tag_filters:
        raise ExternalAPIError(f"Unknown place category: {category!r}")

    union_parts = "\n  ".join(
        f"{tag}(around:{radius_m},{lat},{lon});" for tag in tag_filters
    )
    return f"[out:json][timeout:25];\n(\n  {union_parts}\n);\nout body;"


async def query_places(
    http: httpx.AsyncClient,
    lat: float,
    lon: float,
    category: str,
    radius_m: int,
) -> dict:
    ql = _build_overpass_query(lat, lon, category, radius_m)
    try:
        resp = await http.post(settings.overpass_api_url, data={"data": ql})
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ExternalAPIError(f"Overpass API error: {exc.response.status_code}") from exc
    except httpx.RequestError as exc:
        raise ExternalAPIError(f"Overpass request failed: {exc}") from exc
    return resp.json()
