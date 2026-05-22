"""
Deterministic conflict detection — pure Python, no LLM calls.
Runs before the critic agent to flag structural issues in the itinerary.
"""

from app.common.haversine import haversine_km
from app.planning.schemas import Conflict, DayPlan, ItinerarySchema, TimeBlock

# Activities more than this far apart back-to-back are flagged.
_MAX_DISTANCE_KM = 15.0

# Outdoor activity categories that are weather-sensitive.
_OUTDOOR_CATEGORIES = {"attraction", "nature", "shopping"}

# Substrings in WMO weather descriptions that count as bad conditions.
_BAD_WEATHER_PATTERNS = (
    "thunderstorm",
    "heavy rain",
    "snow storm",
    "blizzard",
    "hail",
    "sleet",
    "heavy snow",
    "heavy drizzle",
)


def _minutes(t: str) -> int:
    """'09:30' → 570.  Returns 0 on any parse failure."""
    try:
        h, m = t.split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return 0


def _check_distance(day: DayPlan, block: TimeBlock) -> list[Conflict]:
    conflicts: list[Conflict] = []
    acts = block.activities
    for i in range(len(acts) - 1):
        a, b = acts[i], acts[i + 1]
        if None in (a.latitude, a.longitude, b.latitude, b.longitude):
            continue
        dist = haversine_km(a.latitude, a.longitude, b.latitude, b.longitude)  # type: ignore[arg-type]
        if dist > _MAX_DISTANCE_KM:
            conflicts.append(
                Conflict(
                    type="distance",
                    severity="warning",
                    day_number=day.day_number,
                    description=(
                        f"'{a.name}' → '{b.name}' are {dist:.1f} km apart in the "
                        f"{block.label} block — consider splitting across different blocks."
                    ),
                    activities=[a.name, b.name],
                )
            )
    return conflicts


def _check_timing(day: DayPlan, block: TimeBlock) -> list[Conflict]:
    block_start = _minutes(block.start_time)
    block_end = _minutes(block.end_time)
    available = max(block_end - block_start, 0)
    total = sum(a.duration_minutes for a in block.activities)
    if total > available:
        return [
            Conflict(
                type="timing",
                severity="warning",
                day_number=day.day_number,
                description=(
                    f"{block.label.capitalize()} block needs {total} min but only "
                    f"{available} min are available ({block.start_time}–{block.end_time})."
                ),
                activities=[a.name for a in block.activities],
            )
        ]
    return []


def _check_weather(day: DayPlan, block: TimeBlock) -> list[Conflict]:
    if not day.weather:
        return []

    desc = ""
    if isinstance(day.weather, dict):
        desc = str(day.weather.get("description", "")).lower()

    is_bad = any(pat in desc for pat in _BAD_WEATHER_PATTERNS)
    if not is_bad:
        return []

    conflicts: list[Conflict] = []
    for act in block.activities:
        if act.category in _OUTDOOR_CATEGORIES:
            conflicts.append(
                Conflict(
                    type="weather",
                    severity="warning",
                    day_number=day.day_number,
                    description=(
                        f"'{act.name}' is an outdoor {act.category} activity scheduled "
                        f"on a day with {desc} — consider an indoor alternative."
                    ),
                    activities=[act.name],
                )
            )
    return conflicts


def run_conflict_checks(itinerary: ItinerarySchema) -> list[Conflict]:
    """Run all deterministic checks. Returns a (possibly empty) list of Conflict objects."""
    conflicts: list[Conflict] = []
    for day in itinerary.days:
        for block in (day.morning, day.afternoon, day.evening):
            conflicts.extend(_check_distance(day, block))
            conflicts.extend(_check_timing(day, block))
            conflicts.extend(_check_weather(day, block))
    return conflicts
