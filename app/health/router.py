from fastapi import APIRouter, Request

from app.common.logger import get_logger

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


@router.get("/health")
async def health_check(request: Request, full: bool = False):
    """
    Returns app status. Pass ?full=true to also ping external APIs.
    Always checks DB. External API checks are opt-in to avoid latency on every probe.
    """
    result: dict = {"status": "ok", "services": {}}

    # --- Database ---
    try:
        await request.app.state.db.table("trips").select("id").limit(1).execute()
        result["services"]["database"] = "ok"
    except Exception as exc:
        logger.warning("DB health check failed: %s", exc)
        result["services"]["database"] = "error"
        result["status"] = "degraded"

    if not full:
        return result

    # --- Open-Meteo ---
    try:
        resp = await request.app.state.http.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": 0, "longitude": 0, "current": "temperature_2m"},
            timeout=5.0,
        )
        result["services"]["open_meteo"] = "ok" if resp.status_code == 200 else f"http_{resp.status_code}"
    except Exception:
        result["services"]["open_meteo"] = "unreachable"

    # --- Overpass ---
    try:
        resp = await request.app.state.http.get(
            "https://overpass-api.de/api/interpreter",
            params={"data": "[out:json];out 0;"},
            timeout=5.0,
        )
        result["services"]["overpass"] = "ok" if resp.status_code == 200 else f"http_{resp.status_code}"
    except Exception:
        result["services"]["overpass"] = "unreachable"

    return result
