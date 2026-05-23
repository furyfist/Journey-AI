# Structured Input + Pipeline Optimisation Plan

**Goal:** Replace the single raw-prompt flow with a two-step structured input, and cut LLM call count from up to 10 down to 2 per generation — with no quality loss.

---

## Problem Statement

### Current pipeline (per generation)

```
POST /api/v1/trips  { prompt: "5 day Tokyo trip" }
        ↓
ResearcherAgent      ← 1 Groq call + 4–6 tool round trips (each = 1 Groq call)
PlannerAgent         ← 1 Groq call
SynthesizerAgent     ← 1 Groq call
ConflictChecker      ← deterministic (free)
CriticAgent          ← 1 Groq call
Persist → trip_complete

Total: up to 10 Groq API calls. Latency: 20–35s. User waits for everything.
```

### Root causes

1. ResearcherAgent uses an LLM to orchestrate HTTP calls that are fully deterministic — the LLM adds no value here
2. PlannerAgent produces an intermediate rough dict that the SynthesizerAgent immediately converts — two calls doing one job
3. Critic blocks `trip_complete` — user waits for quality review before seeing their itinerary
4. Raw prompt gives the LLM nothing structured — it guesses destination, budget, persona, and interests from free text
5. Full raw API responses (weather JSON, Overpass nodes) are dumped into every downstream prompt — wasted tokens

---

## Solution Overview

```
POST /api/v1/trips  { prompt, destination, total_days, budget, persona_hint, interests, constraints, travel_party }
        ↓
fetch_research()          ← pure async Python, 0 Groq calls, parallel HTTP
SynthesizerAgent          ← 1 Groq call (absorbs planner responsibility)
ConflictChecker           ← deterministic (free)
Persist → trip_complete   ← user sees itinerary NOW
CriticAgent               ← 1 Groq call, runs AFTER trip_complete in same SSE stream
Critic persists conflicts → stream closes

Total: 2 Groq API calls. Latency: 8–14s. Itinerary visible at ~8s.
```

---

## Part 1 — Structured Input (Frontend + Backend Schema)

### Why

A generic prompt is underspecified. The itinerary schema requires `destination`, `total_days`, `budget_level`, `persona`, `interests`. Currently the LLM guesses all of these from free text. Structured fields give it ground truth instead of inference.

### UX Flow

```
Step 1: User types raw prompt in existing textarea → clicks "Plan my trip"
        (no API call yet)
        ↓
Step 2: Compact 6-field form slides in below the prompt
        User fills or confirms fields (pre-fill from prompt where detectable)
        → clicks "Generate Itinerary"
        ↓
Step 3: One merged payload POSTed to backend → redirect to /generate/:id
```

### 6 Fields (chosen to fill schema gaps, not add friction)

| Field | UI | Backend field | Maps to schema |
|---|---|---|---|
| Destination | Text input | `destination` | `ItinerarySchema.destination` |
| Trip length | Number stepper (1–30) | `total_days` | `ItinerarySchema.total_days` |
| Budget | 3-chip selector | `budget` | `ItinerarySchema.budget_level` |
| Travel style | 7-chip selector | `persona_hint` | `ItinerarySchema.persona` (strong prior) |
| Interests | Multi-select chips | `interests: list[str]` | Researcher categories + Planner context |
| Constraints | Multi-select chips | `constraints: list[str]` | Synthesizer + Critic context |

**Budget chips:** Budget / Mid-range / Luxury

**Travel style chips:** Backpacker, Foodie, Culture Seeker, Adventure Junkie, Family Traveler, Digital Nomad, Luxury Explorer

**Interest chips:** Food, Culture, Nature, Nightlife, Shopping, Art, History, Beaches, Architecture

**Constraint chips:** Vegetarian, Less walking, Indoor mostly, Family friendly, Accessibility needs, Halal food

---

## Part 2 — Replace ResearcherAgent with Direct HTTP

### Why

The ResearcherAgent is an LLM that decides to call `get_weather` then `search_places` in a loop. But the logic is always identical and fully deterministic:
- Always call weather for the destination
- Always search places for categories matching the user's interests
- Always return a `ResearchBundle`

With structured `interests` from the form, we know the categories upfront. The LLM orchestration layer is pure overhead.

### Before

```
ResearcherAgent._tool_loop():
  → Groq call: "call get_weather for Tokyo"
  → tool exec: HTTP to Open-Meteo
  → Groq call: "call search_places for attractions"
  → tool exec: HTTP to Overpass
  → Groq call: "call search_places for food"
  → tool exec: HTTP to Overpass
  → Groq call: "call search_places for culture"
  → tool exec: HTTP to Overpass
  → Groq call: "summarise findings"
  → return ResearchBundle

= 5–9 Groq API calls
```

### After

```python
# app/planning/research_fetcher.py  (new file)

INTEREST_TO_CATEGORY = {
    "food":        ["food", "cafe"],
    "culture":     ["culture", "museum"],
    "nature":      ["nature", "park"],
    "nightlife":   ["nightlife", "bar"],
    "shopping":    ["shopping"],
    "art":         ["museum", "culture"],
    "history":     ["attraction", "culture"],
    "beaches":     ["nature", "park"],
    "architecture":["attraction"],
}

DEFAULT_CATEGORIES = ["attractions", "food", "culture", "nature"]

async def fetch_research(
    http: httpx.AsyncClient,
    destination: str,
    total_days: int,
    start_date: str | None,
    budget: str | None,
    interests: list[str] | None,
    prompt: str,
) -> ResearchBundle:
    # 1. Fetch weather (also returns lat/lon)
    weather_data = await fetch_weather_direct(http, destination, start_date, total_days)
    lat = weather_data.get("latitude")
    lon = weather_data.get("longitude")

    # 2. Determine categories from interests
    categories = _resolve_categories(interests)

    # 3. Parallel place searches — no sequential waiting
    place_results = await asyncio.gather(
        *[search_places_direct(http, lat, lon, cat) for cat in categories],
        return_exceptions=True,
    )

    places: dict[str, list[dict]] = {}
    for cat, result in zip(categories, place_results):
        if isinstance(result, Exception):
            logger.warning("places fetch failed for %s: %s", cat, result)
            places[cat] = []
        else:
            places[cat] = _compress_places(result)  # trim to top 15, strip raw tags

    return ResearchBundle(
        destination=destination,
        prompt=prompt,
        total_days=total_days,
        weather=weather_data,
        places=places,
        budget=budget,
        start_date=start_date,
    )
```

= **0 Groq API calls** for research. Parallel HTTP replaces sequential LLM tool loop.

### Research data compression

Before passing places data to the LLM, strip raw Overpass tags and limit results:

```python
def _compress_places(raw: list[dict]) -> list[dict]:
    """Keep only what the LLM needs. Drop raw OSM noise."""
    return [
        {
            "name": p.get("name", "Unnamed"),
            "category": p.get("category"),
            "lat": p.get("lat"),
            "lon": p.get("lon"),
            "address": p.get("address", ""),
        }
        for p in raw
        if p.get("name")
    ][:15]  # top 15 per category is enough
```

This cuts synthesizer prompt token count by ~50%.

---

## Part 3 — Collapse Planner into Synthesizer

### Why

PlannerAgent → `{"persona": ..., "days": [...rough structure...]}` → SynthesizerAgent → `ItinerarySchema`

The planner exists because the synthesizer previously had no signal to determine persona or day structure. With `persona_hint`, `interests`, `constraints`, and `travel_party` now in the payload, persona detection is already done. The rough plan intermediate step is waste.

### Risk

Collapsing increases synthesizer prompt complexity. Mitigation: explicit two-section system prompt with clear responsibilities. Monitor `SchemaValidationError` rate — if it rises, the system prompt needs tightening, not reverting to two agents.

### New SynthesizerAgent system prompt structure

```
SECTION 1 — PERSONA & DAY STRUCTURE GUIDANCE
You are a travel planning expert. Use the traveler context below to determine:
- The correct persona label (choose exactly one: Budget Backpacker, Luxury Explorer, Culture Seeker, 
  Foodie, Adventure Junkie, Family Traveler, Digital Nomad)
- The appropriate pace and day structure for that persona and stated interests
- Which places from the research data best fit morning/afternoon/evening blocks

Traveler context will include: persona_hint, interests, constraints, travel_party, budget.

SECTION 2 — STRICT JSON OUTPUT RULES
Convert your planning decisions into the following exact JSON schema. 
All fields required. No markdown. No explanation.

[ItinerarySchema JSON schema here — as already implemented]

Rules:
- tips: exactly 3–5 items
- Each TimeBlock: 1–4 activities
- reasoning field per activity: explain why this fits THIS traveler's persona/interests
- budget_level must match the stated budget exactly
- Use persona_hint as the persona unless research data strongly suggests otherwise
```

### SynthesizerAgent user message (new)

```python
def synthesizer_user_message(
    prompt: str,
    research: ResearchBundle,
    persona_hint: str | None,
    interests: list[str] | None,
    constraints: list[str] | None,
    travel_party: str | None,
) -> str:
    ctx_parts = [f"Original request: {prompt}"]
    if persona_hint:
        ctx_parts.append(f"Travel style: {persona_hint}")
    if interests:
        ctx_parts.append(f"Interests: {', '.join(interests)}")
    if constraints:
        ctx_parts.append(f"Constraints: {', '.join(constraints)}")
    if travel_party:
        ctx_parts.append(f"Traveling: {travel_party}")

    return (
        f"Plan a {research.total_days}-day trip to {research.destination}.\n\n"
        + "\n".join(ctx_parts) + "\n\n"
        f"Budget: {research.budget or 'mid-range'}\n\n"
        f"Weather data:\n{json.dumps(research.weather, default=str)}\n\n"
        f"Available places by category:\n{json.dumps(research.places, default=str)}\n\n"
        "Build the full itinerary JSON now."
    )
```

---

## Part 4 — Stream Itinerary Before Critic

### Why

Critic takes 3–6 seconds. The user has a complete, valid itinerary after the synthesizer. Making them wait for quality review before seeing anything is pure UX debt.

### New SSE event order

```
researcher_start → researcher_complete   (progress only, no Groq)
synthesizer_start → synthesizer_complete
conflict_checker_start → conflict_detected* (deterministic, instant)
persist (with pre_conflicts only)
trip_complete  ← USER SEES ITINERARY HERE
critic_start   ← still in same SSE stream, user is already reading
critic_complete → conflict_detected* (LLM conflicts pushed as incremental updates)
persist update (add llm_conflicts to itinerary record)
[stream closes]
```

### Implementation in stream_service.py

```python
# After synthesizer completes and pre-conflicts run:

await _persist_initial(db, trip_id, itinerary, research, pre_conflicts)

yield SSEEvent(
    event="trip_complete",
    data={"trip_id": trip_id, "total_conflicts": len(pre_conflicts), ...}
)

# Critic runs AFTER trip_complete — user is already reading their itinerary
yield SSEEvent(event="agent_start", agent="critic", message="Running quality review")
critic = CriticAgent(http, on_event=on_event)
llm_conflicts = await critic.run_critique(itinerary, pre_conflicts, research)
for c in llm_conflicts:
    yield SSEEvent(event="conflict_detected", agent="critic", data=c.model_dump())
yield SSEEvent(event="agent_complete", agent="critic", message=f"{len(llm_conflicts)} issue(s) found")

await _persist_conflicts(db, trip_id, llm_conflicts)
# stream generator returns — SSE connection closes naturally
```

### Frontend behaviour (no breaking change)

- `trip_complete` already triggers itinerary render in the frontend
- `conflict_detected` events already append to the conflicts list
- SSE connection staying open after `trip_complete` is already handled — frontend listens until stream closes
- No new event types needed

---

## Part 5 — Pass Structured Fields Through the Full Pipeline

### Backend schema changes

**`app/trips/schemas.py`** — extend `TripCreate`:
```python
class TripCreate(BaseModel):
    prompt: str = Field(min_length=10, max_length=2000)
    destination: Optional[str] = None
    budget: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_days: Optional[int] = Field(default=None, ge=1, le=30)
    # NEW
    persona_hint: Optional[str] = None
    interests: Optional[list[str]] = None
    constraints: Optional[list[str]] = None
    travel_party: Optional[str] = None
```

**`app/planning/schemas.py`** — extend `ResearchBundle`:
```python
class ResearchBundle(BaseModel):
    destination: str
    prompt: str
    total_days: int
    weather: Optional[dict] = None
    places: dict[str, list[dict]] = {}
    budget: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    # NEW
    persona_hint: Optional[str] = None
    interests: Optional[list[str]] = None
    constraints: Optional[list[str]] = None
    travel_party: Optional[str] = None
```

**`app/planning/service.py`** and **`app/planning/stream_service.py`** — add new params to `run_planning_pipeline()` and `stream_planning_pipeline()` signatures, thread through to `fetch_research()` and the synthesizer call.

**`app/trips/service.py`** — store new fields in the trip DB row:
```python
data = {
    ...existing fields...
    "persona_hint": payload.persona_hint,
    "interests": payload.interests or [],
    "constraints": payload.constraints or [],
    "travel_party": payload.travel_party,
}
```

---

## Implementation Order

Work in this sequence — each step is independently testable:

### Phase 1 — Backend plumbing (no logic change yet)
1. Extend `TripCreate` with 4 new optional fields
2. Extend `ResearchBundle` with the same 4 fields
3. Update `stream_planning_pipeline()` and `run_planning_pipeline()` signatures
4. Update `trips/service.py` to store new fields
5. Verify: POST with new fields → trip created, fields stored in DB

### Phase 2 — Research fetcher (replace ResearcherAgent)
6. Create `app/planning/research_fetcher.py` with `fetch_research()` async function
7. Expose `fetch_weather_direct()` from `app/planning/tools/weather_tool.py`
8. Expose `search_places_direct()` from `app/planning/tools/places_tool.py`
9. Add `_compress_places()` helper
10. Wire `stream_service.py` to call `fetch_research()` instead of `ResearcherAgent`
11. Keep `ResearcherAgent` file intact — it is still used by `RegenerationAgent`
12. Verify: pipeline runs, `ResearchBundle` populated, no Groq calls for research step

### Phase 3 — Collapse Planner into Synthesizer
13. Update `synthesizer_system_prompt()` to include persona/day-structure guidance (new Section 1)
14. Update `synthesizer_user_message()` to accept and include structured context fields
15. Update `SynthesizerAgent.run_synthesis()` signature to accept new context
16. Remove `PlannerAgent` calls from `stream_service.py` and `service.py`
17. Remove planner SSE events from stream
18. Verify: itinerary generated correctly, `persona` field populated, `ItinerarySchema` validates
19. Monitor: watch for `SchemaValidationError` — tighten system prompt if rate > 5%

### Phase 4 — Stream itinerary before critic
20. Split `_persist()` into `_persist_initial()` (without llm_conflicts) and `_persist_conflicts()`
21. Move `trip_complete` event emission to after `_persist_initial()`
22. Move critic call and `_persist_conflicts()` to after `trip_complete`
23. Verify: SSE stream delivers `trip_complete` before critic events, frontend renders itinerary immediately

### Phase 5 — Frontend structured input form
24. Add new fields to `frontend/lib/types/trip.ts`
25. Create `frontend/components/landing/TripDetailsForm.tsx`
    - 6-field layout using chip selectors for budget, style, interests, constraints
    - Props: `prompt`, `onBack`, `onSubmit(payload: TripCreate)`, `loading`, `error`
26. Update `frontend/components/landing/HeroSection.tsx`
    - Add `step: 'prompt' | 'details'` state
    - On `PromptInput.onSubmit` → transition to `'details'` (no API call)
    - On `TripDetailsForm.onSubmit` → call `createTrip(mergedPayload)` → navigate
27. Verify: full flow works end-to-end, all 6 fields reach the backend

---

## Files Changed Summary

### New files
- `app/planning/research_fetcher.py` — replaces ResearcherAgent for primary pipeline

### Modified files
| File | Change |
|---|---|
| `app/trips/schemas.py` | +4 fields to `TripCreate` |
| `app/planning/schemas.py` | +4 fields to `ResearchBundle` |
| `app/trips/service.py` | Store new fields in DB row |
| `app/planning/service.py` | Thread new params, call `fetch_research()` |
| `app/planning/stream_service.py` | Call `fetch_research()`, remove planner, reorder critic after `trip_complete` |
| `app/planning/prompt_builder.py` | Enhance synthesizer prompts, remove planner prompts |
| `app/planning/agents/synthesizer_agent.py` | Accept structured context, merged planner responsibility |
| `app/planning/tools/weather_tool.py` | Expose `fetch_weather_direct()` |
| `app/planning/tools/places_tool.py` | Expose `search_places_direct()` |
| `frontend/lib/types/trip.ts` | +4 fields to `TripCreate` type |
| `frontend/components/landing/HeroSection.tsx` | Add step state, wire `TripDetailsForm` |

### Preserved (no changes)
| File | Reason |
|---|---|
| `app/planning/agents/researcher_agent.py` | Still used by RegenerationAgent |
| `app/planning/agents/planner_agent.py` | Keep for reference, not called in primary pipeline |
| `app/planning/agents/critic_agent.py` | Unchanged, just reordered in stream |
| `app/planning/conflict_checker.py` | Unchanged |
| All regeneration files | Out of scope |

### New frontend files
- `frontend/components/landing/TripDetailsForm.tsx`

---

## Expected Outcome

| Metric | Before | After |
|---|---|---|
| Groq API calls per generation | 8–10 | 2 |
| Time to itinerary visible | 20–35s | 8–14s |
| Time to page (trip_complete) | 20–35s | 8–12s |
| Prompt token count (synthesizer) | ~6,000 | ~3,200 |
| LLM prompt quality | Guesses from free text | Ground truth from structured fields |
| Schema validation failure risk | Baseline | Watch after Phase 3 — tighten if needed |
