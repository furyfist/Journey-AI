"""
Pure async research fetch — replaces ResearcherAgent in the primary pipeline.
0 Groq API calls: weather + places are fetched directly and run in parallel.
"""

import asyncio
from typing import Optional

import httpx

from app.common.logger import get_logger
from app.planning.schemas import ResearchBundle
from app.planning.tools.places_tool import search_places_direct
from app.planning.tools.weather_tool import fetch_weather_direct

logger = get_logger(__name__)

INTEREST_TO_CATEGORY: dict[str, list[str]] = {
    "food":         ["food", "cafe"],
    "culture":      ["culture", "museum"],
    "nature":       ["nature", "park"],
    "nightlife":    ["nightlife", "bar"],
    "shopping":     ["shopping"],
    "art":          ["museum", "culture"],
    "history":      ["attraction", "culture"],
    "beaches":      ["nature", "park"],
    "architecture": ["attraction"],
}

DEFAULT_CATEGORIES = ["attractions", "food", "culture", "nature"]


def _resolve_categories(interests: list[str] | None) -> list[str]:
    if not interests:
        return DEFAULT_CATEGORIES
    seen: set[str] = set()
    cats: list[str] = []
    for interest in interests:
        for cat in INTEREST_TO_CATEGORY.get(interest.lower(), []):
            if cat not in seen:
                seen.add(cat)
                cats.append(cat)
    return cats or DEFAULT_CATEGORIES


def _compress_places(raw_places: list[dict]) -> list[dict]:
    """Keep only what the LLM needs. Drop raw OSM noise."""
    compressed = []
    for p in raw_places:
        name = p.get("name")
        if not name:
            continue
        compressed.append(
            {
                "name": name,
                "category": p.get("category"),
                "lat": p.get("lat"),
                "lon": p.get("lon"),
            }
        )
    return compressed[:15]


async def fetch_research(
    http: httpx.AsyncClient,
    destination: str,
    total_days: int,
    start_date: Optional[str],
    budget: Optional[str],
    interests: Optional[list[str]],
    prompt: str,
    persona_hint: Optional[str] = None,
    constraints: Optional[list[str]] = None,
    travel_party: Optional[str] = None,
) -> ResearchBundle:
    """Fetch weather + places with 0 Groq calls. Parallel HTTP replaces the LLM tool loop."""

    weather_data = await fetch_weather_direct(http, city=destination, days=total_days, start_date=start_date)

    lat: Optional[float] = weather_data.get("lat")
    lon: Optional[float] = weather_data.get("lon")

    categories = _resolve_categories(interests)

    place_results = await asyncio.gather(
        *[search_places_direct(http, lat=lat, lon=lon, category=cat) for cat in categories],
        return_exceptions=True,
    )

    places: dict[str, list[dict]] = {}
    for cat, result in zip(categories, place_results):
        if isinstance(result, Exception):
            logger.warning("places fetch failed for %s: %s", cat, result)
            places[cat] = []
        else:
            raw_places = result.get("places", []) if isinstance(result, dict) else []
            places[cat] = _compress_places(raw_places)

    return ResearchBundle(
        destination=destination,
        prompt=prompt,
        total_days=total_days,
        weather=weather_data,
        places=places,
        budget=budget,
        start_date=start_date,
        persona_hint=persona_hint,
        interests=interests,
        constraints=constraints,
        travel_party=travel_party,
    )
