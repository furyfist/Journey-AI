# Journey AI — Complete Project Reference

> **One-liner:** A multi-agent AI travel planner that researches real APIs, detects conflicts, and streams a strict JSON itinerary to the client in real time.

---

## Table of Contents

1. [Project Purpose](#1-project-purpose)
2. [Tech Stack](#2-tech-stack)
3. [Architecture Overview](#3-architecture-overview)
4. [Folder Structure](#4-folder-structure)
5. [Database Schema](#5-database-schema)
6. [Pydantic Schemas](#6-pydantic-schemas)
7. [API Surface](#7-api-surface)
8. [Agent Pipeline](#8-agent-pipeline)
9. [SSE Streaming Protocol](#9-sse-streaming-protocol)
10. [External API Integrations](#10-external-api-integrations)
11. [Conflict Detection](#11-conflict-detection)
12. [Regeneration System](#12-regeneration-system)
13. [Error Handling & Retry Strategy](#13-error-handling--retry-strategy)
14. [Configuration & Environment](#14-configuration--environment)
15. [Testing Strategy](#15-testing-strategy)
16. [Build History & Status](#16-build-history--status)
17. [Frontend Integration Notes](#17-frontend-integration-notes)

---

## 1. Project Purpose

Journey AI is a **portfolio backend** demonstrating production-level multi-agent reasoning, streaming, and partial replanning. It accepts a natural language trip prompt and runs a 4-stage AI pipeline:

```
Natural language prompt → Research → Plan → Critique → Stream to client
```

**What makes it interesting to engineers:**
- No LangChain / LlamaIndex — raw OpenAI-format tool calling via Groq
- SSE streaming so the frontend watches each agent step in real time
- Deterministic conflict detection (Python haversine + timing math) _before_ the LLM critic runs
- Partial regeneration at 3 levels of granularity (full trip / single day / single block)
- Itinerary versioning: old versions preserved, only one `is_active` per trip
- `0` Groq calls for the research phase — weather + places fetched with direct async HTTP

---

## 2. Tech Stack

| Layer | Choice | Detail |
|---|---|---|
| Language | Python 3.12 | Full async, latest stable |
| Framework | FastAPI (0.135+) | Native `EventSourceResponse` SSE, async-first |
| LLM Inference | Groq API | OpenAI-compatible, ~300 tok/s, free tier |
| Primary model | `llama-3.3-70b-versatile` | Best quality on Groq, 128K ctx, tool calling |
| Fallback model | `llama-4-scout` | Activated on 2nd retry when primary fails |
| LLM SDK | `openai` (v1+) | `base_url="https://api.groq.com/openai/v1"` |
| Database | Supabase (Postgres) | Managed Postgres, Python async SDK |
| HTTP client | `httpx` | Async HTTP for all external calls |
| Validation | Pydantic v2 | Schema enforcement + `model_json_schema()` |
| SSE | `sse-starlette` | `EventSourceResponse` wrapper |
| Config | `pydantic-settings` | Type-safe `.env` loading |
| Weather API | Open-Meteo | Free, no key, geocode + forecast |
| Places API | Overpass (OpenStreetMap) | Free, no key, Overpass QL queries |
| Testing | pytest + pytest-asyncio + httpx | Async test support |
| Deployment target | Railway | Docker-based FastAPI deploy |

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│               NEXT.JS FRONTEND (future)             │
│              (Vercel — planned Session 6+)           │
└──────────────────────┬──────────────────────────────┘
                       │  HTTP + SSE
                       ▼
┌─────────────────────────────────────────────────────┐
│                 FASTAPI BACKEND                     │
│                                                     │
│  ┌───────────┐  ┌───────────┐  ┌────────────────┐  │
│  │  Routers  │→ │ Services  │→ │ Agent Pipeline │  │
│  │ (HTTP I/O)│  │ (business │  │ (multi-step    │  │
│  │           │  │  logic)   │  │  reasoning)    │  │
│  └───────────┘  └───────────┘  └───────┬────────┘  │
│                                        │            │
│                         ┌──────────────┤            │
│                         ▼              ▼            │
│                    ┌──────┐    ┌────────────┐       │
│                    │ Groq │    │ Open-Meteo │       │
│                    │ LLM  │    │ + Overpass │       │
│                    └──────┘    └────────────┘       │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              SUPABASE (Postgres)                    │
│   trips / itineraries / agent_logs tables           │
└─────────────────────────────────────────────────────┘
```

**Key architectural decisions:**

| Decision | Why |
|---|---|
| Research via direct HTTP (not LLM tool calls) | Eliminates ~2 Groq round-trips per request. Weather + places fetched in parallel with `asyncio.gather`. |
| SynthesizerAgent absorbs PlannerAgent | Reduces LLM calls from 2 to 1 for the core reasoning step. Synthesizer both plans and formats. |
| Deterministic checks before LLM critic | Distance, timing, and weather conflicts are caught by pure Python before burning a Groq call. The critic only handles reasoning-level issues. |
| `trip_complete` SSE before critic runs | Frontend gets the itinerary immediately. Critic conflicts stream in afterwards as they're found. |
| Versioned itineraries | Old `is_active=false` rows kept. Regeneration bumps `version` and activates the new row atomically. |

---

## 4. Folder Structure

```
journey_ai/
│
├── app/
│   ├── main.py                          # App factory, lifespan, CORS, router registration
│   │
│   ├── core/                            # App-wide infrastructure
│   │   ├── config.py                    # pydantic-settings: all env vars + cors_origins_list property
│   │   ├── database.py                  # Supabase async client init
│   │   ├── dependencies.py              # FastAPI Depends: DBDep, HttpDep
│   │   ├── exceptions.py                # Custom exception hierarchy
│   │   └── exception_handlers.py        # Global exception → HTTP response mapping
│   │
│   ├── common/                          # Shared utilities (no business logic)
│   │   ├── http_client.py               # Shared httpx.AsyncClient with retries
│   │   ├── logger.py                    # Structured logging setup
│   │   ├── constants.py                 # WMO_WEATHER_CODES + OSM_TAG_GROUPS
│   │   ├── types.py                     # Shared type aliases
│   │   └── haversine.py                 # haversine_km(lat1, lon1, lat2, lon2) → float
│   │
│   ├── trips/                           # Domain: Trip CRUD
│   │   ├── router.py                    # POST /trips, GET /trips, GET/DELETE /{id}, GET /{id}/stream
│   │   ├── schemas.py                   # TripCreate, TripResponse, TripDetail, TripListItem
│   │   ├── service.py                   # create_trip, list_trips, get_trip, delete_trip
│   │   └── repository.py               # Supabase reads/writes for trips table
│   │
│   ├── planning/                        # Domain: AI Planning Pipeline
│   │   ├── schemas.py                   # SSEEvent, Conflict, Activity, TimeBlock, DayPlan,
│   │   │                                #   ItinerarySchema, ResearchBundle
│   │   ├── service.py                   # run_planning_pipeline (sync path, no SSE)
│   │   ├── stream_service.py            # stream_planning_pipeline (async generator → SSEEvent)
│   │   ├── research_fetcher.py          # fetch_research: parallel weather+places, 0 Groq calls
│   │   ├── prompt_builder.py            # System + user prompts for all agents + regen variants
│   │   ├── conflict_checker.py          # run_conflict_checks: distance, timing, weather
│   │   │
│   │   ├── agents/
│   │   │   ├── base_agent.py            # Groq tool-call loop (8 iterations, 3 retries, fallback model)
│   │   │   ├── researcher_agent.py      # (legacy) LLM-based research — kept for compatibility
│   │   │   ├── planner_agent.py         # Persona detection + rough day-by-day plan (used in regen)
│   │   │   ├── synthesizer_agent.py     # Full ItinerarySchema JSON via json_object mode + Pydantic
│   │   │   ├── critic_agent.py          # LLM quality review, never raises, returns [] on failure
│   │   │   └── regeneration_agent.py    # DayRegenerationAgent + BlockRegenerationAgent
│   │   │
│   │   └── tools/
│   │       ├── tool_registry.py         # Central registry of all tool definitions
│   │       ├── weather_tool.py          # get_weather tool schema + fetch_weather_direct executor
│   │       └── places_tool.py           # search_places tool schema + search_places_direct executor
│   │
│   ├── weather/                         # Domain: Standalone weather endpoint
│   │   ├── router.py                    # GET /api/v1/weather
│   │   ├── schemas.py                   # WeatherRequest, DayWeather, WeatherResponse
│   │   ├── service.py                   # Fetch + transform + WMO code mapping
│   │   └── client.py                    # Raw HTTP calls to Open-Meteo + geocoding
│   │
│   ├── places/                          # Domain: Standalone places endpoint
│   │   ├── router.py                    # GET /api/v1/places
│   │   ├── schemas.py                   # PlaceQuery, PlaceResult
│   │   ├── service.py                   # Overpass QL builder + result transform
│   │   └── client.py                    # Raw HTTP calls to Overpass API
│   │
│   ├── regeneration/                    # Domain: Partial replanning
│   │   ├── router.py                    # POST /api/v1/trips/{id}/regenerate
│   │   ├── schemas.py                   # RegenerateScope enum + RegenerateRequest
│   │   ├── service.py                   # _regen_full / _regen_day / _regen_block + version swap
│   │   └── repository.py               # fetch_active_itinerary, deactivate_itinerary, insert_new_version
│   │
│   └── health/
│       └── router.py                    # GET /api/v1/health
│
├── migrations/
│   ├── 001_create_trips.sql
│   ├── 002_create_itineraries.sql
│   ├── 003_create_agent_logs.sql
│   └── 004_add_structured_input_fields.sql   # persona_hint, interests[], constraints[], travel_party
│
├── tests/
│   ├── conftest.py                      # Shared fixtures: AsyncClient, mock Supabase
│   ├── unit/
│   │   ├── test_trip_schemas.py
│   │   ├── test_weather_service.py
│   │   ├── test_places_service.py
│   │   ├── test_itinerary_schema.py
│   │   ├── test_prompt_builder.py
│   │   └── test_conflict_detection.py
│   ├── integration/
│   │   ├── test_trip_endpoints.py
│   │   ├── test_planning_pipeline.py
│   │   ├── test_sse_stream.py
│   │   └── test_regeneration.py
│   └── mocks/
│       ├── mock_groq_responses.py
│       ├── mock_weather_data.py
│       └── mock_places_data.py
│
└── docs/
    ├── backend_build_plan.md            # Original session-by-session build plan
    └── PROJECT_OVERVIEW.md             # This document
```

---

## 5. Database Schema

### `trips` table

```sql
CREATE TABLE trips (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    prompt          TEXT NOT NULL,
    destination     TEXT NOT NULL,
    budget          TEXT,                         -- "budget" | "mid-range" | "luxury"
    travel_dates    JSONB,                        -- {"start": "2026-07-01", "end": "2026-07-05"}
    total_days      INTEGER NOT NULL,
    title           TEXT NOT NULL,
    summary         TEXT,
    persona         TEXT,                         -- detected: "Budget Backpacker", "Foodie", etc.
    status          TEXT NOT NULL DEFAULT 'pending',
    -- Added in migration 004:
    persona_hint    TEXT,
    interests       TEXT[] NOT NULL DEFAULT '{}',
    constraints     TEXT[] NOT NULL DEFAULT '{}',
    travel_party    TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- status lifecycle: pending → generating → completed | failed
```

### `itineraries` table

```sql
CREATE TABLE itineraries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id         UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL DEFAULT 1,
    itinerary_data  JSONB NOT NULL,               -- full ItinerarySchema as JSON
    weather_data    JSONB,                        -- cached per-day weather
    places_data     JSONB,                        -- cached places by category
    conflicts       JSONB DEFAULT '[]'::jsonb,    -- list[Conflict] — pre-conflicts + critic conflicts
    reasoning       JSONB DEFAULT '{}'::jsonb,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Only one is_active=true row per trip_id at a time.
-- Regeneration: old row → is_active=false, new row → version+1, is_active=true
CREATE UNIQUE INDEX idx_itinerary_active ON itineraries(trip_id) WHERE is_active = true;
```

### `agent_logs` table

```sql
CREATE TABLE agent_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id         UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    agent_name      TEXT NOT NULL,
    step            TEXT NOT NULL,
    input_data      JSONB,
    output_data     JSONB,
    tool_calls      JSONB DEFAULT '[]'::jsonb,
    duration_ms     INTEGER,
    model_used      TEXT,
    tokens_used     JSONB,                        -- {"prompt": N, "completion": M}
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 6. Pydantic Schemas

### Planning schemas (`app/planning/schemas.py`)

```python
class Activity(BaseModel):
    name: str
    description: str
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    duration_minutes: int
    cost_estimate: Optional[str]       # e.g. "$10-20", "Free"
    category: str                      # food | attraction | transport | shopping | nature | culture | nightlife
    reasoning: str                     # "Why this was chosen for this traveler"

class TimeBlock(BaseModel):
    label: str                         # morning | afternoon | evening
    start_time: str                    # "09:00"
    end_time: str                      # "12:30"
    activities: list[Activity]         # min 1, max 4
    block_summary: str

class DayPlan(BaseModel):
    day_number: int
    date: Optional[str]               # ISO date if travel_dates provided
    title: str                        # creative day title
    weather: Optional[dict]           # weather snapshot for this day
    morning: TimeBlock
    afternoon: TimeBlock
    evening: TimeBlock
    day_summary: str

class ItinerarySchema(BaseModel):
    title: str
    destination: str
    total_days: int
    budget_level: str
    persona: str
    summary: str
    days: list[DayPlan]
    tips: list[str]                   # 3-5 items

class ResearchBundle(BaseModel):
    """Internal pipeline transfer object — not stored directly."""
    destination: str
    prompt: str
    total_days: int
    weather: Optional[dict]
    places: dict[str, list[dict]]     # {category: [compressed place dicts]}
    budget: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    persona_hint: Optional[str]
    interests: Optional[list[str]]
    constraints: Optional[list[str]]
    travel_party: Optional[str]

class Conflict(BaseModel):
    type: Literal["distance", "timing", "weather", "budget", "persona"]
    severity: Literal["warning", "error"]
    day_number: int
    description: str
    activities: list[str]

class SSEEvent(BaseModel):
    event: Literal["agent_start", "tool_call", "tool_result", "agent_progress",
                   "agent_complete", "conflict_detected", "trip_complete", "error", "keepalive"]
    agent: Optional[str]
    data: Optional[Any]
    message: Optional[str]
```

### Trip schemas (`app/trips/schemas.py`)

```python
class TripCreate(BaseModel):
    prompt: str                       # 10-2000 chars
    destination: Optional[str]
    budget: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    total_days: Optional[int]         # 1-30
    persona_hint: Optional[str]
    interests: Optional[list[str]]
    constraints: Optional[list[str]]
    travel_party: Optional[str]

class TripResponse(BaseModel):
    id, prompt, destination, title, summary, persona, status, total_days, created_at, updated_at

class TripDetail(TripResponse):
    itinerary: Optional[dict]         # full ItinerarySchema
    conflicts: list[dict]
    reasoning: dict
    weather_data: Optional[dict]

class TripListItem(BaseModel):
    id, title, destination, total_days, status, created_at
```

### Regeneration schemas (`app/regeneration/schemas.py`)

```python
class RegenerateScope(str, Enum):
    full_trip = "full_trip"
    day = "day"
    single_block = "single_block"

class RegenerateRequest(BaseModel):
    scope: RegenerateScope
    day_number: Optional[int]         # required for day / single_block
    block_label: Optional[Literal["morning", "afternoon", "evening"]]  # required for single_block
    constraint: Optional[str]         # max 500 chars, e.g. "make it vegetarian"
    # @model_validator enforces required fields per scope
```

---

## 7. API Surface

### Core endpoints

| Method | Path | Description | Response |
|---|---|---|---|
| `POST` | `/api/v1/trips` | Create pending trip row (no pipeline yet) | `TripResponse` (status: pending) |
| `GET` | `/api/v1/trips` | List all trips | `list[TripListItem]` |
| `GET` | `/api/v1/trips/{trip_id}` | Full trip detail with active itinerary | `TripDetail` |
| `DELETE` | `/api/v1/trips/{trip_id}` | Delete trip + cascade | `204 No Content` |
| `GET` | `/api/v1/trips/{trip_id}/stream` | **SSE endpoint** — runs full pipeline | `text/event-stream` |
| `POST` | `/api/v1/trips/{trip_id}/regenerate` | Partial or full replan | `TripDetail` |

### Supporting endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/weather` | Standalone weather lookup (lat, lon, days) |
| `GET` | `/api/v1/places` | Standalone place search (lat, lon, category, radius) |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc UI |

### Frontend flow

```
1. POST /api/v1/trips            → get trip_id (status: pending)
2. GET  /api/v1/trips/{id}/stream → open EventSource, receive events
3. Handle trip_complete event    → call GET /api/v1/trips/{id} for full itinerary
4. Handle conflict_detected      → show inline warnings
5. POST /api/v1/trips/{id}/regenerate → replan, receive TripDetail immediately
```

---

## 8. Agent Pipeline

### Pipeline stages

```
User prompt → TripCreate
                ↓
         POST /api/v1/trips
                ↓
          status: "pending"
                ↓
    GET /api/v1/trips/{id}/stream
                ↓
   ┌─────────────────────────────────┐
   │  STAGE 1: RESEARCH FETCHER     │  No Groq calls — pure HTTP
   │                                 │
   │  fetch_weather_direct()         │  → Open-Meteo geocode + forecast
   │  search_places_direct() ×N      │  → Overpass QL (parallel gather)
   │  Output: ResearchBundle         │
   └──────────────────┬──────────────┘
                      ↓
   ┌─────────────────────────────────┐
   │  STAGE 2: SYNTHESIZER AGENT    │  1 Groq call
   │                                 │
   │  Input: prompt + ResearchBundle │
   │  response_format: json_object   │
   │  Output: ItinerarySchema        │  Pydantic-validated
   └──────────────────┬──────────────┘
                      ↓
   ┌─────────────────────────────────┐
   │  STAGE 3: CONFLICT CHECKER     │  0 Groq calls — pure Python
   │                                 │
   │  _check_distance()              │  haversine ≥15km back-to-back
   │  _check_timing()                │  sum(duration_minutes) > block window
   │  _check_weather()               │  outdoor activity on bad-weather day
   └──────────────────┬──────────────┘
                      ↓
              PERSIST TO DB
              SSE: trip_complete
                      ↓
   ┌─────────────────────────────────┐
   │  STAGE 4: CRITIC AGENT         │  1 Groq call — after client sees itinerary
   │                                 │
   │  Input: itinerary + conflicts   │
   │  + research bundle              │
   │  Checks: quality, feasibility,  │
   │  persona alignment              │
   │  Output: list[Conflict] | []   │  Never raises
   └─────────────────────────────────┘
                      ↓
              PERSIST CRITIC CONFLICTS
```

### BaseAgent (`app/planning/agents/base_agent.py`)

The shared Groq interaction layer:

- Uses `openai.AsyncOpenAI(base_url="https://api.groq.com/openai/v1")`
- `run()` method: builds messages, calls `_tool_loop()`
- `_tool_loop()`: up to 8 iterations. Each iteration: call Groq → if `tool_calls` present → execute each → append results → repeat
- Retries: 3 attempts with exponential backoff (1s, 2s). On attempt 2, switches to fallback model
- `_emit()`: broadcasts SSE events via optional `on_event: EventCallback`
- Tool results appended as `{"role": "tool", "tool_call_id": ..., "content": ...}`

```
Attempt 1 → groq_model (llama-3.3-70b-versatile)
Attempt 2 → groq_model with 1s delay
Attempt 3 → groq_fallback_model (llama-4-scout) with 2s delay
```

### Prompt architecture

| Agent | System prompt intent | Output format |
|---|---|---|
| Researcher (legacy) | Research assistant, gather data via tools, don't invent places | Free text summary |
| Planner | Strategist, detect persona, reason about schedule | `{"persona": "...", "days": [...]}` |
| Synthesizer | JSON generator, convert plan → strict schema, fill every field | Full `ItinerarySchema` JSON |
| Critic | Reviewer, return conflicts list only | `{"conflicts": [...]}` |
| DayRegenerationAgent | Regenerate one day matching DayPlan schema | `DayPlan` JSON |
| BlockRegenerationAgent | Regenerate one time block matching TimeBlock schema | `TimeBlock` JSON |

---

## 9. SSE Streaming Protocol

The `stream_planning_pipeline` function in `app/planning/stream_service.py` is an async generator that yields `SSEEvent` objects. An `asyncio.Queue` bridges the `on_event` callbacks from agents back to the generator.

### Event types and timing

```
event: agent_start       — stage begins (agent, message)
event: tool_call         — agent calling a tool (tool, args) — from BaseAgent
event: tool_result       — tool returned (tool, ok, error?) — from BaseAgent
event: agent_complete    — stage finished (agent, message)
event: conflict_detected — one conflict found (Conflict dict)
event: trip_complete     — itinerary persisted, safe to fetch GET /{id}
event: error             — unrecoverable failure (message)
event: keepalive         — sent every 15s to keep proxies from closing the connection
```

### Sequence

```
agent_start (researcher)
agent_complete (researcher)
agent_start (synthesizer)
  [tool_call / tool_result]* (if synthesizer uses tools — currently none)
agent_complete (synthesizer)
agent_start (conflict_checker)
[conflict_detected]*         (0 or more deterministic conflicts)
trip_complete                ← client should fetch GET /{id} at this point
agent_start (critic)
agent_complete (critic)
[conflict_detected]*         (0 or more LLM critic conflicts)
```

### Keepalive implementation

```python
async def keepalive_loop(stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=15)
        except asyncio.TimeoutError:
            await queue.put(SSEEvent(event="keepalive"))
```

The keepalive task is cancelled in the `finally` block after the generator completes.

---

## 10. External API Integrations

### Open-Meteo (weather + geocoding)

**Geocode:** `GET https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1`
Returns: `latitude`, `longitude`, `timezone`

**Forecast:** `GET https://api.open-meteo.com/v1/forecast`
Parameters: `latitude`, `longitude`, `daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max`, `timezone=auto`, `forecast_days={n}`

**What's used:**
- `temperature_2m_max/min` — daily high/low
- `weathercode` — WMO code mapped to human description via `WMO_WEATHER_CODES` constant
- `precipitation_sum` — rain amount for conflict detection
- `windspeed_10m_max` — outdoor activity relevance

**Error handling:** Returns `{"weather": null}` on failure. Synthesizer plans without weather data.

### Overpass API (OpenStreetMap places)

**Endpoint:** `POST https://overpass-api.de/api/interpreter`

**Query pattern:**
```
[out:json][timeout:25];
area[name="{city}"]->.searchArea;
(
  node["{tag_key}"~"{tag_values}"](area.searchArea);
);
out body {limit};
```

**Category → OSM tag mapping** (from `common/constants.py` `OSM_TAG_GROUPS`):
- `attractions` → `tourism~"attraction|museum|viewpoint|gallery"`
- `food` → `amenity~"restaurant|cafe|fast_food"`
- `culture` → `tourism~"museum|gallery"` + `historic`
- `nature` → `leisure~"park|garden|nature_reserve"`
- `nightlife` → `amenity~"bar|pub|nightclub"`
- `shopping` → `shop~"mall|market|clothes"`

**Compression:** `_compress_places()` keeps only `{name, category, lat, lon}` and caps at 15 per category to reduce LLM token usage.

---

## 11. Conflict Detection

Two-pass system: deterministic checks first, LLM critic second.

### Pass 1: Deterministic (`app/planning/conflict_checker.py`)

Runs in pure Python, 0 Groq calls.

| Check | Condition | Severity |
|---|---|---|
| Distance | `haversine_km(a, b) > 15.0` for consecutive activities in same block | warning |
| Timing | `sum(activity.duration_minutes) > block_end - block_start` in minutes | warning |
| Weather | Outdoor category activity (`attraction`, `nature`, `shopping`) on a day with bad weather pattern in description | warning |

Bad weather patterns: `thunderstorm`, `heavy rain`, `snow storm`, `blizzard`, `hail`, `sleet`, `heavy snow`, `heavy drizzle`

### Pass 2: LLM Critic (`app/planning/agents/critic_agent.py`)

- Receives: `ItinerarySchema` + pre-conflicts list + `ResearchBundle`
- `response_format={"type": "json_object"}` → returns `{"conflicts": [...]}`
- Uses `TypeAdapter(list[Conflict]).validate_python(...)` for validation
- Never raises — returns `[]` on any LLM or parsing failure
- Runs **after** `trip_complete` is emitted so the client isn't blocked

### Conflict model

```python
class Conflict(BaseModel):
    type: Literal["distance", "timing", "weather", "budget", "persona"]
    severity: Literal["warning", "error"]
    day_number: int
    description: str              # human-readable explanation
    activities: list[str]         # activity names involved
```

---

## 12. Regeneration System

**Endpoint:** `POST /api/v1/trips/{trip_id}/regenerate`

The regeneration service (`app/regeneration/service.py`) restores `ResearchBundle` from cached `weather_data` + `places_data` on the existing itinerary row — **no new API calls**.

### Three scopes

#### `full_trip`
Runs `PlannerAgent.run_planning()` → `SynthesizerAgent.run_synthesis()` with optional `constraint` appended to the prompt. Uses cached research.

#### `day`
Runs `DayRegenerationAgent.regenerate_day()` for the specified `day_number`. Patches the day in a deep copy of the itinerary, preserving `day_number`, `date`, and `weather` from the original.

#### `single_block`
Runs `BlockRegenerationAgent.regenerate_block()` for the specified `day_number` + `block_label`. Patches the block, preserving `label`, `start_time`, `end_time` from the original.

### Version swap (atomic)
```
1. Fetch current active itinerary row
2. Generate new itinerary
3. Run full conflict checks (deterministic + critic)
4. deactivate_itinerary(old_row_id)      → is_active = false
5. insert_new_version(version + 1, ...)  → is_active = true
6. Return updated TripDetail
```

### Constraint injection
For `full_trip` and `day`/`single_block`, an optional `constraint` string (max 500 chars) is injected into the agent prompt: `"Additional constraint: {constraint}"`. This is the "one-line replan" feature.

---

## 13. Error Handling & Retry Strategy

### Exception hierarchy (`app/core/exceptions.py`)

```
JourneyAIError (base, 500)
├── ExternalAPIError (502)    — weather or places API failure
├── GroqAPIError (502)        — LLM inference failure
├── SchemaValidationError (500) — AI output failed Pydantic validation
├── TripNotFoundError (404)
└── RateLimitError (429)      — Groq free tier limit
```

### BaseAgent retry policy

| Attempt | Model | Delay |
|---|---|---|
| 1st | `groq_model` | none |
| 2nd | `groq_model` | 1s |
| 3rd | `groq_fallback_model` | 2s |

`RateLimitError` is raised immediately (no retry). After 3 failures, `GroqAPIError` is raised.

### External API fallback

| API | Behavior on failure |
|---|---|
| Open-Meteo geocode | `lat/lon = None` — places skipped, weather = null |
| Open-Meteo forecast | `weather = None` — synthesizer plans without weather |
| Overpass | `places[category] = []` — category silently skipped |

### Pipeline failure handling

In `stream_service.py`, any unhandled exception:
1. Sets `trip.status = "failed"` in DB
2. Yields `SSEEvent(event="error", message=str(exc))`
3. Generator completes; keepalive task cancelled

The **critic agent** never raises — it returns `[]` on any failure so the pipeline always reaches `trip_complete`.

---

## 14. Configuration & Environment

### `app/core/config.py`

```python
class Settings(BaseSettings):
    app_env: str = "development"
    app_port: int = 8000
    app_host: str = "0.0.0.0"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"    # comma-separated or JSON array

    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_anon_key: str = ""

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_fallback_model: str = "llama-4-scout"
    groq_max_tokens: int = 8192
    groq_temperature: float = 0.7

    open_meteo_base_url: str = "https://api.open-meteo.com/v1"
    overpass_api_url: str = "https://overpass-api.de/api/interpreter"
    geocoding_api_url: str = "https://geocoding-api.open-meteo.com/v1/search"

    @property
    def cors_origins_list(self) -> list[str]: ...  # parses comma or JSON list
```

### `.env` required variables

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
GROQ_API_KEY=gsk_...
```

All other variables have defaults. `cors_origins` must include the frontend URL in production.

---

## 15. Testing Strategy

**Test command:** `venv/Scripts/python -m pytest tests/ -v`

**Total: 94 tests passing**

### Test layout

| Suite | Files | What's tested |
|---|---|---|
| Unit | `test_trip_schemas.py` | TripCreate / TripResponse validation |
| Unit | `test_weather_service.py` | WMO code mapping, transform |
| Unit | `test_places_service.py` | Overpass QL builder, result transform |
| Unit | `test_itinerary_schema.py` | ItinerarySchema valid + invalid inputs |
| Unit | `test_prompt_builder.py` | System + user prompt construction |
| Unit | `test_conflict_detection.py` | 14 tests: distance, timing, weather conflicts |
| Integration | `test_trip_endpoints.py` | POST/GET/DELETE trip endpoints |
| Integration | `test_planning_pipeline.py` | Full pipeline with mocked Groq |
| Integration | `test_sse_stream.py` | 7 tests: SSE event sequence |
| Integration | `test_regeneration.py` | All 3 regeneration scopes |

### Mock strategy

- **Groq:** Mock the `openai.AsyncOpenAI.chat.completions.create()` call. Pre-built JSON in `tests/mocks/mock_groq_responses.py`
- **Supabase:** Mock `supabase.table().select/insert/update/delete` chains
- **Open-Meteo / Overpass:** Mock `httpx.AsyncClient` with saved JSON fixtures in `tests/mocks/`

---

## 16. Build History & Status

### Sessions completed

| Session | Focus | Key commits |
|---|---|---|
| 1 | Skeleton: health check, FastAPI app factory | `feat: project skeleton with health check` |
| 2 | Trip CRUD with Supabase | `feat: trip CRUD with Supabase` |
| 3 | Weather + places integration | `feat: weather and places integration` |
| 3 | Researcher agent (LLM tool calling) | `feat: researcher agent with tool calling` |
| 3 | Planner + synthesizer agents | `feat: planner and synthesizer agents — full pipeline` |
| 4 | Haversine + conflict checker | `feat: critic agent with conflict detection` (phase 1) |
| 4 | Critic agent + SSE streaming | `feat: critic agent with conflict detection` (phase 2) |
| 4 | SSE stream service | `feat: SSE streaming for agent pipeline` |
| 5 | TripDetailsForm 2-step UI prep, chip selectors, prompt pre-fill | `feat: add TripDetailsForm 2-step flow...` |
| 5 | Collapse PlannerAgent into SynthesizerAgent | `feat: collapse PlannerAgent into SynthesizerAgent` |
| 5 | Research fetcher (0 Groq calls) | `feat: replace ResearcherAgent with direct async fetch_research` |
| 5 | SSE fix: keep connection open after trip_complete | `fix: keep SSE connection open after trip_complete so critic events are received` |

### Current branch: `frontend/pages`

### Planned (Session 5+ remaining)
- Regeneration endpoint (in code, tests pending)
- Supabase Auth integration (user-scoped trips)
- Railway deployment

---

## 17. Frontend Integration Notes

### Creating and streaming a trip

```javascript
// Step 1: Create the trip
const res = await fetch('/api/v1/trips', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "5-day Tokyo trip, I love street food",
    destination: "Tokyo",
    total_days: 5,
    budget: "budget",
    interests: ["food", "culture"],
    travel_party: "solo"
  })
});
const { id: tripId } = await res.json();  // status: "pending"

// Step 2: Stream the pipeline
const es = new EventSource(`/api/v1/trips/${tripId}/stream`);

es.addEventListener('agent_start', e => { /* show agent name */ });
es.addEventListener('conflict_detected', e => { /* show warning */ });
es.addEventListener('trip_complete', async e => {
  // Safe to fetch the full itinerary now
  const trip = await fetch(`/api/v1/trips/${tripId}`).then(r => r.json());
  renderItinerary(trip.itinerary);
});
es.addEventListener('error', e => { /* show error state */ });
```

### Regenerating a block

```javascript
const res = await fetch(`/api/v1/trips/${tripId}/regenerate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    scope: 'single_block',
    day_number: 2,
    block_label: 'evening',
    constraint: 'make it vegetarian'
  })
});
const updatedTrip = await res.json();  // TripDetail — immediate response
```

### Conflict display

Conflicts are available on `TripDetail.conflicts`. Each has:
- `type`: `distance | timing | weather | budget | persona`
- `severity`: `warning | error`
- `day_number`: which day
- `description`: human-readable string
- `activities`: list of activity names involved

Display inline next to the relevant day/block in the itinerary view.
