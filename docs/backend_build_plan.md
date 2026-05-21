# Journey AI — Backend Build Plan (V1)

> **One-liner:** A multi-agent AI travel planner that reasons, researches real APIs, detects conflicts, and streams a strict itinerary to the client in real time.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Tech Stack — Locked Versions](#2-tech-stack--locked-versions)
3. [Folder Structure](#3-folder-structure)
4. [Database Schema (Supabase / Postgres)](#4-database-schema-supabase--postgres)
5. [Pydantic Schemas (Contracts)](#5-pydantic-schemas-contracts)
6. [API Surface](#6-api-surface)
7. [Agent Pipeline — Deep Dive](#7-agent-pipeline--deep-dive)
8. [SSE Streaming Protocol](#8-sse-streaming-protocol)
9. [External API Integration](#9-external-api-integration)
10. [The 5 Innovative Features — Backend Design](#10-the-5-innovative-features--backend-design)
11. [Error Handling & Retry Strategy](#11-error-handling--retry-strategy)
12. [Environment & Configuration](#12-environment--configuration)
13. [Testing Strategy](#13-testing-strategy)
14. [Build Order — Phase by Phase](#14-build-order--phase-by-phase)
15. [Git Strategy](#15-git-strategy)
16. [Deployment (Railway)](#16-deployment-railway)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   NEXT.JS FRONTEND                  │
│              (Vercel — built later)                  │
└──────────────────────┬──────────────────────────────┘
                       │  HTTP + SSE
                       ▼
┌─────────────────────────────────────────────────────┐
│                 FASTAPI BACKEND                     │
│                  (Railway)                           │
│                                                     │
│  ┌───────────┐  ┌───────────┐  ┌────────────────┐  │
│  │ API Layer │→ │ Services  │→ │ Agent Pipeline │  │
│  │ (routes)  │  │ (business │  │ (multi-step    │  │
│  │           │  │  logic)   │  │  reasoning)    │  │
│  └───────────┘  └───────────┘  └───────┬────────┘  │
│                                        │            │
│                            ┌───────────┼──────────┐ │
│                            ▼           ▼          ▼ │
│                      ┌──────┐   ┌────────┐  ┌─────┐│
│                      │ Groq │   │Open-   │  │Over-││
│                      │ API  │   │Meteo   │  │pass ││
│                      └──────┘   └────────┘  └─────┘│
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              SUPABASE (Postgres + Auth)              │
└─────────────────────────────────────────────────────┘
```

The backend is the brain. It accepts a natural language prompt, runs a multi-agent pipeline (Researcher → Planner → Synthesizer → Critic), streams progress via SSE, and returns a strict JSON itinerary.

No frameworks like LangChain. Raw tool calling with Groq's OpenAI-compatible API. This is more impressive to engineers and gives you full control.

---

## 2. Tech Stack — Locked Versions

| Component | Choice | Why |
|---|---|---|
| **Runtime** | Python 3.12+ | Latest stable, full async support |
| **Framework** | FastAPI (latest, 0.135+) | Native SSE via `EventSourceResponse`, async-first |
| **LLM Inference** | Groq API (OpenAI-compatible) | Free tier, ~300 tok/s, structured output support |
| **Primary Model** | `llama-3.3-70b-versatile` | Best overall quality on Groq, 128K context, tool calling support |
| **Fallback Model** | `llama-4-scout` | 512K context for large trip re-plans |
| **Database** | Supabase (Postgres) | Managed Postgres, Python SDK, Auth built-in |
| **Python SDK** | `supabase` (supabase-py, latest) | Official, async client available via `acreate_client` |
| **Weather** | Open-Meteo Forecast API | Free, no API key, JSON, up to 16-day forecast |
| **Places** | Overpass API (OpenStreetMap) | Free, no key, query by tag (tourism, amenity, historic) |
| **HTTP Client** | `httpx` | Async HTTP for all external calls |
| **Validation** | Pydantic v2 | Schema enforcement, `model_json_schema()` for Groq structured output |
| **SSE** | FastAPI native `EventSourceResponse` | Built-in since 0.135, no third-party package needed |
| **Env Management** | `pydantic-settings` | Type-safe env loading |
| **Testing** | `pytest` + `pytest-asyncio` + `httpx` | Async test support |
| **Deployment** | Railway | Docker-based, easy FastAPI deploy |

### Groq API — Key Details

Groq uses the OpenAI-compatible chat completions format. You use the standard `openai` Python package with `base_url="https://api.groq.com/openai/v1"`.

**Structured Outputs:** Use `response_format={"type": "json_schema", "json_schema": {...}}` with Pydantic's `model_json_schema()`. This gives guaranteed schema compliance via constrained decoding — no retry logic needed.

**Tool Calling:** Local tool calling — you define tools as JSON schemas, the model returns `tool_calls`, you execute locally and send results back. This is how your agents call weather/places APIs.

**Free Tier Limits:** ~30 req/min, ~6,000 tokens/min, ~14,400 req/day. Enough for development and demo.

---

## 3. Folder Structure

This follows a **feature-based layout** — each domain owns its routes, schemas, and services. No cross-domain imports at the service level. Shared logic lives in `core/` and `common/`.

```
journey-ai-backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                          # App factory, lifespan, CORS, router registration
│   │
│   ├── core/                            # App-wide config and infrastructure
│   │   ├── __init__.py
│   │   ├── config.py                    # pydantic-settings: all env vars
│   │   ├── database.py                  # Supabase client init (sync + async)
│   │   ├── dependencies.py              # FastAPI Depends: db client, auth, etc.
│   │   ├── exceptions.py                # Custom exception classes
│   │   └── exception_handlers.py        # Global exception → HTTP response mapping
│   │
│   ├── common/                          # Shared utilities (no business logic)
│   │   ├── __init__.py
│   │   ├── http_client.py               # Shared httpx.AsyncClient with retries
│   │   ├── logger.py                    # Structured logging setup
│   │   ├── constants.py                 # App-wide constants (OSM tags, weather codes, etc.)
│   │   └── types.py                     # Shared type aliases
│   │
│   ├── trips/                           # Domain: Trip CRUD
│   │   ├── __init__.py
│   │   ├── router.py                    # POST /trips, GET /trips, GET /trips/:id, DELETE
│   │   ├── schemas.py                   # TripCreate, TripResponse, TripListItem
│   │   ├── service.py                   # Trip business logic
│   │   └── repository.py               # Supabase reads/writes for trips table
│   │
│   ├── planning/                        # Domain: AI Planning Pipeline
│   │   ├── __init__.py
│   │   ├── router.py                    # POST /plan/generate (SSE endpoint)
│   │   ├── schemas.py                   # PlanRequest, itinerary schemas
│   │   ├── service.py                   # Orchestrates the agent pipeline
│   │   ├── prompt_builder.py            # Constructs the system + user prompt
│   │   │
│   │   ├── agents/                      # Multi-agent pipeline
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py            # Abstract base: call Groq, handle tools
│   │   │   ├── researcher_agent.py      # Calls weather + places tools
│   │   │   ├── planner_agent.py         # Reasons about schedule, detects persona
│   │   │   ├── synthesizer_agent.py     # Produces strict itinerary JSON
│   │   │   └── critic_agent.py          # Reviews plan, flags conflicts
│   │   │
│   │   └── tools/                       # Tool definitions for agent tool-calling
│   │       ├── __init__.py
│   │       ├── tool_registry.py         # Central registry of all tools
│   │       ├── weather_tool.py          # get_weather tool definition + executor
│   │       └── places_tool.py           # search_places tool definition + executor
│   │
│   ├── weather/                         # Domain: Weather Data
│   │   ├── __init__.py
│   │   ├── router.py                    # GET /weather (standalone endpoint)
│   │   ├── schemas.py                   # WeatherRequest, WeatherResponse, DayWeather
│   │   ├── service.py                   # Open-Meteo fetch + transform
│   │   └── client.py                    # Raw HTTP calls to Open-Meteo
│   │
│   ├── places/                          # Domain: Place Discovery
│   │   ├── __init__.py
│   │   ├── router.py                    # GET /places (standalone endpoint)
│   │   ├── schemas.py                   # PlaceQuery, PlaceResult
│   │   ├── service.py                   # Overpass query builder + result transform
│   │   └── client.py                    # Raw HTTP calls to Overpass API
│   │
│   ├── regeneration/                    # Domain: Regeneration Logic
│   │   ├── __init__.py
│   │   ├── router.py                    # POST /trips/:id/regenerate
│   │   ├── schemas.py                   # RegenerateRequest (scope: trip/day/block)
│   │   └── service.py                   # Partial regeneration orchestration
│   │
│   └── health/                          # Domain: Health Check
│       ├── __init__.py
│       └── router.py                    # GET /health
│
├── migrations/                          # SQL migration files for Supabase
│   ├── 001_create_trips.sql
│   ├── 002_create_itineraries.sql
│   └── 003_create_agent_logs.sql
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Shared fixtures: test client, mock Supabase
│   ├── unit/
│   │   ├── test_prompt_builder.py
│   │   ├── test_weather_service.py
│   │   ├── test_places_service.py
│   │   └── test_itinerary_schema.py
│   ├── integration/
│   │   ├── test_trip_endpoints.py
│   │   ├── test_planning_pipeline.py
│   │   └── test_regeneration.py
│   └── mocks/
│       ├── mock_groq_responses.py
│       └── mock_weather_data.py
│
├── scripts/
│   ├── seed_test_trip.py                # Seed a sample trip for development
│   └── test_groq_connection.py          # Verify Groq API key works
│
├── .env.example                         # Template for environment variables
├── .gitignore
├── Dockerfile
├── docker-compose.yml                   # Local dev with hot reload
├── pyproject.toml                       # Dependencies, project metadata
├── README.md
└── Makefile                             # dev, test, lint, format, docker shortcuts
```

### Why This Structure

**Feature-based, not file-type-based.** You don't hunt across 5 folders to understand "trips." Everything about trips is in `app/trips/`. This is how Google-scale codebases work — domain boundaries, not tech layer boundaries.

**`core/` is infrastructure.** Config, DB init, global error handling. Never imports from domains.

**`common/` is shared utilities.** HTTP client, logger, constants. No business logic. Any domain can import from here.

**`agents/` lives inside `planning/`.** Agents are a planning concern, not a standalone domain. If you ever add non-planning agents, you'd extract to a top-level `agents/` module.

**`tools/` lives inside `planning/`.** Tools are what agents call. Tool definitions (JSON schemas) and executors (the actual functions) live together.

---

## 4. Database Schema (Supabase / Postgres)

### `trips` table

```sql
-- migrations/001_create_trips.sql

CREATE TABLE trips (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES auth.users(id) ON DELETE CASCADE,  -- nullable for guest mode
    prompt          TEXT NOT NULL,                                      -- original user input
    destination     TEXT NOT NULL,
    budget          TEXT,                                               -- "budget", "mid-range", "luxury"
    travel_dates    JSONB,                                             -- {"start": "2026-07-01", "end": "2026-07-05"}
    total_days      INTEGER NOT NULL,
    title           TEXT NOT NULL,
    summary         TEXT,
    persona         TEXT,                                               -- detected travel persona
    status          TEXT NOT NULL DEFAULT 'pending',                    -- pending, generating, completed, failed
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for user's trip list
CREATE INDEX idx_trips_user_id ON trips(user_id);
CREATE INDEX idx_trips_status ON trips(status);
```

### `itineraries` table

```sql
-- migrations/002_create_itineraries.sql

CREATE TABLE itineraries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id         UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL DEFAULT 1,                        -- for regeneration versioning
    itinerary_data  JSONB NOT NULL,                                    -- the full strict itinerary JSON
    weather_data    JSONB,                                             -- cached weather per day
    places_data     JSONB,                                             -- cached places used
    conflicts       JSONB DEFAULT '[]'::jsonb,                         -- detected conflicts from critic
    reasoning       JSONB DEFAULT '{}'::jsonb,                         -- per-item reasoning from planner
    is_active       BOOLEAN NOT NULL DEFAULT true,                     -- only one active per trip
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Unique active itinerary per trip
CREATE UNIQUE INDEX idx_itinerary_active ON itineraries(trip_id) WHERE is_active = true;
CREATE INDEX idx_itineraries_trip_id ON itineraries(trip_id);
```

### `agent_logs` table

```sql
-- migrations/003_create_agent_logs.sql

CREATE TABLE agent_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id         UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    agent_name      TEXT NOT NULL,                                     -- researcher, planner, synthesizer, critic
    step            TEXT NOT NULL,                                     -- what the agent did
    input_data      JSONB,                                            -- what it received
    output_data     JSONB,                                            -- what it produced
    tool_calls      JSONB DEFAULT '[]'::jsonb,                        -- tools called during this step
    duration_ms     INTEGER,                                          -- execution time
    model_used      TEXT,                                             -- which Groq model
    tokens_used     JSONB,                                            -- {"prompt": N, "completion": M}
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_agent_logs_trip_id ON agent_logs(trip_id);
```

### Design Decisions

- **`itinerary_data` is JSONB, not normalized tables.** The itinerary is a document — days → blocks → activities. Normalizing this into 4 tables adds complexity with zero benefit. JSONB lets you query inside (`itinerary_data->'days'->0->'morning'`) and Supabase handles it natively.
- **Versioning via `version` + `is_active`.** When you regenerate, old itinerary becomes `is_active = false`, new one gets `version + 1`. You keep history without deleting data.
- **`reasoning` column.** This stores the "Why This?" explanation per item. The planner agent outputs this alongside the schedule.
- **`conflicts` column.** The critic agent writes detected conflicts here. The frontend reads them and renders inline warnings.
- **`agent_logs` table.** Not user-facing. This is for debugging, performance tracking, and portfolio demos ("here's the agent trace for a Tokyo trip").

---

## 5. Pydantic Schemas (Contracts)

These are the strict contracts between your backend and frontend. The AI must produce output matching `ItinerarySchema` exactly.

### Core Itinerary Schema (what Groq must produce)

```python
# app/planning/schemas.py

from pydantic import BaseModel, Field
from typing import Optional

class Activity(BaseModel):
    name: str = Field(description="Name of the activity or place")
    description: str = Field(description="1-2 sentence description")
    location: str = Field(description="Address or area name")
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    duration_minutes: int = Field(description="Estimated time in minutes")
    cost_estimate: Optional[str] = Field(default=None, description="e.g. '$10-20', 'Free'")
    category: str = Field(description="food, attraction, transport, shopping, nature, culture, nightlife")
    reasoning: str = Field(description="Why this was chosen for this traveler")

class TimeBlock(BaseModel):
    label: str = Field(description="morning, afternoon, or evening")
    start_time: str = Field(description="e.g. '09:00'")
    end_time: str = Field(description="e.g. '12:30'")
    activities: list[Activity] = Field(min_length=1, max_length=4)
    block_summary: str = Field(description="One sentence summary of this block")

class DayPlan(BaseModel):
    day_number: int
    date: Optional[str] = Field(default=None, description="ISO date if dates provided")
    title: str = Field(description="Creative title for the day, e.g. 'Temple Trails & Street Food'")
    weather: Optional[dict] = Field(default=None, description="Weather data for this day")
    morning: TimeBlock
    afternoon: TimeBlock
    evening: TimeBlock
    day_summary: str

class ItinerarySchema(BaseModel):
    title: str = Field(description="Creative trip title")
    destination: str
    total_days: int
    budget_level: str
    persona: str = Field(description="Detected travel persona")
    summary: str = Field(description="2-3 sentence trip overview")
    days: list[DayPlan]
    tips: list[str] = Field(description="3-5 general tips for this destination")
```

### Trip Schemas

```python
# app/trips/schemas.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class TripCreate(BaseModel):
    prompt: str = Field(min_length=10, max_length=2000)
    destination: Optional[str] = None      # extracted by agent if not explicit
    budget: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_days: Optional[int] = Field(default=None, ge=1, le=30)

class TripResponse(BaseModel):
    id: UUID
    prompt: str
    destination: str
    title: str
    summary: Optional[str]
    persona: Optional[str]
    status: str
    total_days: int
    created_at: datetime
    updated_at: datetime

class TripDetail(TripResponse):
    itinerary: Optional[dict] = None       # full itinerary JSON
    conflicts: list[dict] = []
    reasoning: dict = {}
    weather_data: Optional[dict] = None

class TripListItem(BaseModel):
    id: UUID
    title: str
    destination: str
    total_days: int
    status: str
    created_at: datetime
```

### Regeneration Schemas

```python
# app/regeneration/schemas.py

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class RegenerateScope(str, Enum):
    FULL_TRIP = "full_trip"
    SINGLE_DAY = "single_day"
    SINGLE_BLOCK = "single_block"

class RegenerateRequest(BaseModel):
    scope: RegenerateScope
    day_number: Optional[int] = None          # required for single_day and single_block
    block: Optional[str] = None               # "morning" | "afternoon" | "evening"
    constraint: Optional[str] = Field(        # the one-line replan instruction
        default=None,
        max_length=500,
        description="e.g. 'Make this vegetarian', 'Something more adventurous'"
    )
```

---

## 6. API Surface

### Core Endpoints

| Method | Path | Description | Response |
|---|---|---|---|
| `POST` | `/api/v1/trips` | Create trip + kick off agent pipeline | `TripResponse` (status: generating) |
| `GET` | `/api/v1/trips` | List user's saved trips | `list[TripListItem]` |
| `GET` | `/api/v1/trips/{trip_id}` | Full trip detail with itinerary | `TripDetail` |
| `DELETE` | `/api/v1/trips/{trip_id}` | Delete a trip | `204 No Content` |
| `GET` | `/api/v1/trips/{trip_id}/stream` | SSE stream of agent progress | `text/event-stream` |
| `POST` | `/api/v1/trips/{trip_id}/regenerate` | Regenerate trip/day/block | `TripResponse` (re-triggers stream) |

### Supporting Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/weather` | Standalone weather lookup (lat, lon, days) |
| `GET` | `/api/v1/places` | Standalone place search (lat, lon, category, radius) |
| `GET` | `/api/v1/health` | Health check + dependency status |

### API Versioning

All endpoints sit under `/api/v1/`. This is baked into the router prefix, not repeated in every route decorator. When V2 comes, you add a new router — zero changes to V1.

---

## 7. Agent Pipeline — Deep Dive

This is the core of the product. Four agents, running sequentially, each with a specific job.

### Pipeline Flow

```
User Prompt: "5-day Tokyo trip, budget, street food lover"
          │
          ▼
┌─────────────────────────────────┐
│  STEP 1: RESEARCHER AGENT      │  SSE: "Researching Tokyo weather..."
│                                 │  SSE: "Finding places in Shibuya..."
│  - Extracts: destination,       │
│    dates, budget, preferences   │
│  - Tool calls:                  │
│    → get_weather(Tokyo, 5 days) │
│    → search_places(Tokyo,       │
│      tourism, food, culture)    │
│  - Output: ResearchBundle       │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│  STEP 2: PLANNER AGENT         │  SSE: "Detecting travel persona..."
│                                 │  SSE: "Building day structure..."
│  - Receives: ResearchBundle     │
│  - Detects persona from prompt  │
│  - Reasons about schedule:      │
│    proximity, timing, weather   │
│  - Output: RoughPlan +          │
│    reasoning per item           │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│  STEP 3: SYNTHESIZER AGENT     │  SSE: "Generating itinerary..."
│                                 │
│  - Receives: RoughPlan +        │
│    ResearchBundle               │
│  - Produces: strict             │
│    ItinerarySchema JSON         │
│  - Uses Groq structured output  │
│    (json_schema mode)           │
│  - Output: ItinerarySchema      │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│  STEP 4: CRITIC AGENT          │  SSE: "Reviewing plan for conflicts..."
│                                 │
│  - Receives: ItinerarySchema +  │
│    weather data + places data   │
│  - Checks:                      │
│    → distance between back-to-  │
│      back locations             │
│    → weather vs outdoor plans   │
│    → timing feasibility         │
│    → closed venues on that day  │
│  - Output: list[Conflict]       │
│  - Optionally: auto-fix minor   │
│    issues                       │
└────────────┬────────────────────┘
             ▼
         SAVE TO DB
         SSE: "Trip ready!"
```

### Agent Base Class

Every agent shares the same Groq calling pattern:

```python
# app/planning/agents/base_agent.py (conceptual structure)

class BaseAgent:
    """
    - Accepts a system prompt + user message
    - Optionally has tools (JSON schema definitions)
    - Calls Groq via openai SDK (base_url swapped)
    - Handles tool call loop: model requests tool → execute → send result back
    - Emits SSE events for each step
    - Logs to agent_logs table
    """
```

### Tool Calling Loop (How Agents Use External APIs)

```
Agent sends message to Groq with tool definitions
    ↓
Groq returns: tool_calls: [{name: "get_weather", args: {lat, lon, days}}]
    ↓
Backend executes get_weather() locally (calls Open-Meteo)
    ↓
Backend sends tool result back to Groq
    ↓
Groq uses the result to continue reasoning
    ↓
Repeat until Groq returns a final text/JSON response (no more tool calls)
```

This is **raw tool calling** — no LangChain, no abstraction. You own the loop.

### Prompt Engineering

Each agent gets a carefully crafted system prompt. Key principles:

- **Researcher:** "You are a travel research assistant. Use the provided tools to gather weather and place data. Do not invent places. Only return data from tool results."
- **Planner:** "You are a travel planning strategist. Analyze the research data and the user's prompt to detect their travel persona and build a logical day-by-day structure. Explain your reasoning for each major decision."
- **Synthesizer:** "You are a JSON generator. Convert the plan into the exact schema provided. Every field must be filled. Do not add fields not in the schema."
- **Critic:** "You are a travel plan reviewer. Check for: distance conflicts, weather mismatches, timing impossibilities, closed venues. Return a list of conflicts with severity and suggested fixes."

---

## 8. SSE Streaming Protocol

FastAPI 0.135+ has native SSE support via `EventSourceResponse` and `ServerSentEvent`.

### Event Types

```
event: agent_start
data: {"agent": "researcher", "message": "Starting research for Tokyo..."}

event: tool_call
data: {"agent": "researcher", "tool": "get_weather", "args": {"location": "Tokyo"}}

event: tool_result
data: {"agent": "researcher", "tool": "get_weather", "status": "success"}

event: agent_progress
data: {"agent": "planner", "message": "Detected persona: Budget Foodie"}

event: agent_complete
data: {"agent": "synthesizer", "message": "Itinerary generated"}

event: conflict_detected
data: {"day": 3, "block": "afternoon", "message": "Rain expected, all activities outdoor"}

event: trip_complete
data: {"trip_id": "uuid", "status": "completed"}

event: error
data: {"message": "Weather API unreachable", "recoverable": true}
```

### Implementation Pattern

```python
# app/planning/router.py (conceptual)

from fastapi.sse import EventSourceResponse, ServerSentEvent

@router.get("/trips/{trip_id}/stream", response_class=EventSourceResponse)
async def stream_trip_generation(trip_id: UUID):
    async def event_generator():
        async for event in planning_service.run_pipeline(trip_id):
            yield ServerSentEvent(
                data=json.dumps(event["data"]),
                event=event["type"]
            )
    return EventSourceResponse(event_generator())
```

### Flow

1. Frontend calls `POST /api/v1/trips` → gets back `trip_id` + status `"generating"`.
2. Frontend immediately connects to `GET /api/v1/trips/{trip_id}/stream` via `EventSource`.
3. Backend runs the pipeline, yielding SSE events at each step.
4. When pipeline completes, final event sent, connection closes.
5. Frontend calls `GET /api/v1/trips/{trip_id}` to get the full saved itinerary.

---

## 9. External API Integration

### Open-Meteo (Weather)

**Endpoint:** `https://api.open-meteo.com/v1/forecast`

**No API key required.** Free for non-commercial use, up to 10,000 daily calls.

```
GET https://api.open-meteo.com/v1/forecast
  ?latitude=35.6762
  &longitude=139.6503
  &daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,windspeed_10m_max
  &timezone=auto
  &forecast_days=7
```

**What you use:**
- `temperature_2m_max` / `min` — high/low per day
- `weathercode` — WMO code → map to "Sunny", "Rainy", "Cloudy", etc.
- `precipitation_sum` — rain amount (for conflict detection)
- `windspeed_10m_max` — relevant for outdoor activities

**Geocoding:** Open-Meteo also has a geocoding endpoint to convert city names to lat/lon: `https://geocoding-api.open-meteo.com/v1/search?name=Tokyo`

### Overpass API (Places)

**Endpoint:** `https://overpass-api.de/api/interpreter`

**No API key required.** Free, rate-limited (be respectful with query frequency).

**Query pattern for travel-relevant places:**

```
[out:json][timeout:25];
area[name="Tokyo"]->.searchArea;
(
  node["tourism"~"attraction|museum|viewpoint|gallery"](area.searchArea);
  node["amenity"~"restaurant|cafe|bar"](area.searchArea);
  node["historic"](area.searchArea);
  node["leisure"~"park|garden"](area.searchArea);
);
out body 50;
```

**Key OSM tags for travel:**
- `tourism`: attraction, museum, viewpoint, hotel, gallery, information
- `amenity`: restaurant, cafe, bar, pub, fast_food, marketplace
- `historic`: monument, castle, ruins, memorial
- `leisure`: park, garden, nature_reserve, beach_resort
- `cuisine`: japanese, italian, street_food (sub-tag of amenity=restaurant)

**Important:** Overpass data quality varies by region. Tokyo, Paris, London are excellent. Smaller cities may have sparse data. Your planner agent should handle sparse results gracefully.

---

## 10. The 5 Innovative Features — Backend Design

### Feature 1: Constraint-Aware Replanning

**Backend implementation:**
- `POST /api/v1/trips/{trip_id}/regenerate` with `scope=single_block` and `constraint="it's raining and I'm tired"`
- Service loads the full current itinerary from DB
- Planner agent receives the full trip context + the constraint + current weather
- Agent replans ONLY the specified block, keeping all other blocks intact
- Synthesizer produces a replacement block matching `TimeBlock` schema
- DB update: patch `itinerary_data->'days'->N->'morning'` with the new block

**Key design:** The agent receives the full itinerary as context (not just the block). This is critical — it needs to know what came before and after to avoid conflicts.

### Feature 2: "Why This?" Transparency Layer

**Backend implementation:**
- The `Activity` schema has a `reasoning` field
- The planner agent is prompted: "For each activity, write one sentence explaining why you chose it for this specific traveler"
- The `reasoning` column on `itineraries` table stores a map: `{activity_name: reasoning_text}`
- Served as part of `GET /trips/{trip_id}` response

**No extra API call.** The reasoning is generated during the main planning pass. The prompt engineering makes this happen for free.

### Feature 3: Travel Persona Detection

**Backend implementation:**
- The planner agent's system prompt includes persona definitions:
  - Budget Backpacker, Luxury Explorer, Culture Seeker, Foodie, Adventure Junkie, Family Traveler, Digital Nomad
- From the user's prompt, the agent outputs a `persona` field
- The researcher agent uses the persona to filter Overpass queries (e.g., if "Foodie" → heavier weight on `amenity=restaurant`, `cuisine=*`)
- Persona is stored on the `trips` table and returned to the frontend

### Feature 4: Live Conflict Detector

**Backend implementation:**
- The critic agent runs after the synthesizer
- It receives: the full itinerary + weather data + places data (with lat/lon)
- It checks:
  1. **Distance conflicts:** Haversine distance between consecutive activities. If >10km and <30min gap → flag.
  2. **Weather conflicts:** If `weathercode` indicates rain and all block activities are `category=nature|outdoor` → flag.
  3. **Timing conflicts:** If total `duration_minutes` in a block exceeds the block's time window → flag.
- Output: `list[Conflict]` where each conflict has `day_number`, `block`, `severity` (warning/critical), `message`, `suggested_fix`
- Conflicts stored in `itineraries.conflicts` JSONB column

**Distance calculation runs in Python** (haversine formula), not in the LLM. The critic agent focuses on reasoning-based checks. Deterministic checks (distance, time math) run in code before the critic.

### Feature 5: One-Line Replan

**Backend implementation:**
- Same endpoint as Feature 1: `POST /api/v1/trips/{trip_id}/regenerate`
- `scope=single_block`, `constraint="Make this vegetarian"`
- The planner agent receives:
  - Full trip context (all days)
  - The specific block to replace
  - The constraint
  - The persona
- It replans just that block, respecting the constraint
- The critic agent re-runs on only the changed block (not the full trip — optimization)

---

## 11. Error Handling & Retry Strategy

### Exception Hierarchy

```python
# app/core/exceptions.py

class JourneyAIError(Exception):
    """Base exception for all app errors"""
    status_code: int = 500
    message: str = "Internal server error"

class ExternalAPIError(JourneyAIError):
    """Weather or Places API failure"""
    status_code = 502

class GroqAPIError(JourneyAIError):
    """LLM inference failure"""
    status_code = 502

class SchemaValidationError(JourneyAIError):
    """AI output didn't match expected schema"""
    status_code = 500

class TripNotFoundError(JourneyAIError):
    """Trip ID doesn't exist"""
    status_code = 404

class RateLimitError(JourneyAIError):
    """Groq free tier limit hit"""
    status_code = 429
```

### Retry Policy

| Service | Max Retries | Backoff | Fallback |
|---|---|---|---|
| Groq API | 3 | Exponential (1s, 2s, 4s) | Switch to smaller model on 3rd retry |
| Open-Meteo | 2 | Linear (1s, 2s) | Return `weather: null`, agent plans without weather |
| Overpass API | 2 | Linear (2s, 4s) | Return empty places list, agent uses LLM knowledge |
| Supabase | 2 | Linear (0.5s, 1s) | Raise hard error (no DB = no save) |

### Schema Validation After Groq

Even with structured output mode, validate the response with Pydantic:

```python
try:
    itinerary = ItinerarySchema.model_validate_json(groq_response)
except ValidationError as e:
    # Log the error, retry with a stricter prompt
    # After 2 failures, return partial result with warning
```

---

## 12. Environment & Configuration

### `.env.example`

```env
# App
APP_ENV=development
APP_PORT=8000
APP_HOST=0.0.0.0
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJ...                    # service_role key for backend
SUPABASE_ANON_KEY=eyJ...                       # anon key (if needed)

# Groq
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_FALLBACK_MODEL=llama-4-scout
GROQ_MAX_TOKENS=8192
GROQ_TEMPERATURE=0.7

# External APIs (no keys needed)
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1
OVERPASS_API_URL=https://overpass-api.de/api/interpreter
GEOCODING_API_URL=https://geocoding-api.open-meteo.com/v1/search
```

### Config Class

```python
# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "development"
    app_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    supabase_url: str
    supabase_service_key: str

    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_fallback_model: str = "llama-4-scout"
    groq_max_tokens: int = 8192
    groq_temperature: float = 0.7

    open_meteo_base_url: str = "https://api.open-meteo.com/v1"
    overpass_api_url: str = "https://overpass-api.de/api/interpreter"
    geocoding_api_url: str = "https://geocoding-api.open-meteo.com/v1/search"

    class Config:
        env_file = ".env"
```

---

## 13. Testing Strategy

### Test Pyramid

```
          ┌──────────┐
          │   E2E    │  ← Few: full pipeline with mocked Groq
          ├──────────┤
          │  Integ.  │  ← Medium: route → service → mock DB
          ├──────────┤
          │   Unit   │  ← Many: schemas, prompt builder, utils
          └──────────┘
```

### What to Test

**Unit tests (no I/O):**
- Pydantic schema validation (valid + invalid inputs)
- Prompt builder output (given a trip request, does the system prompt look right?)
- Weather code mapping (WMO code → human string)
- Haversine distance calculation
- Overpass query builder (given params, does it produce correct QL?)
- Conflict detection logic (given mock itinerary, are conflicts caught?)

**Integration tests (mock external, real FastAPI):**
- `POST /api/v1/trips` → returns 201 with correct shape
- `GET /api/v1/trips` → returns list
- `GET /api/v1/trips/{id}` → returns full detail
- `DELETE /api/v1/trips/{id}` → returns 204
- `POST /api/v1/trips/{id}/regenerate` → returns updated trip
- SSE stream → emits correct event sequence

**E2E tests (mocked Groq, real everything else):**
- Full pipeline: prompt → research → plan → synthesize → critique → save
- Verify the saved itinerary matches `ItinerarySchema`
- Verify conflicts are detected for a known-bad plan

### Mock Strategy

- **Groq:** Mock the `openai.ChatCompletion.create()` call. Return pre-built JSON that matches the schema. Store mock responses in `tests/mocks/`.
- **Supabase:** Use a test Supabase project with a separate schema, or mock the `supabase.table().select()` chain.
- **Open-Meteo:** Mock `httpx` responses with saved JSON fixtures.
- **Overpass:** Mock `httpx` responses with saved Overpass JSON.

---

## 14. Build Order — Phase by Phase

### Phase 1: Skeleton (Days 1-2)

**Goal:** Backend boots, health check works, DB connects.

```
Tasks:
├── Init repo, pyproject.toml, .gitignore
├── Set up folder structure (all __init__.py files, empty modules)
├── app/main.py — FastAPI app factory with lifespan
├── app/core/config.py — pydantic-settings
├── app/core/database.py — Supabase client init
├── app/core/exceptions.py + exception_handlers.py
├── app/common/logger.py — structured logging
├── app/common/http_client.py — shared httpx client
├── app/health/router.py — GET /health (checks DB + external APIs)
├── Dockerfile + docker-compose.yml
├── Makefile with: dev, test, lint, format
└── Verify: uvicorn boots, /health returns 200
```

**Git:** `feat: project skeleton with health check`

---

### Phase 2: Database + Trip CRUD (Days 3-4)

**Goal:** Full trip CRUD works. No AI yet.

```
Tasks:
├── Run SQL migrations in Supabase dashboard
├── app/trips/schemas.py — all Pydantic models
├── app/trips/repository.py — Supabase CRUD operations
├── app/trips/service.py — business logic (thin for now)
├── app/trips/router.py — all 4 endpoints
├── tests/unit/test_trip_schemas.py
├── tests/integration/test_trip_endpoints.py
└── Verify: can create, list, get, delete trips via curl/Postman
```

**Git:** `feat: trip CRUD with Supabase`

---

### Phase 3: Weather + Places Integration (Days 5-7)

**Goal:** Standalone weather and places endpoints work.

```
Tasks:
├── app/weather/client.py — Open-Meteo HTTP calls
├── app/weather/schemas.py — WeatherRequest, DayWeather
├── app/weather/service.py — fetch + transform + WMO code mapping
├── app/weather/router.py — GET /weather
├── app/places/client.py — Overpass HTTP calls
├── app/places/schemas.py — PlaceQuery, PlaceResult
├── app/places/service.py — Overpass QL builder + result transform
├── app/places/router.py — GET /places
├── app/common/constants.py — WMO weather codes, OSM tag mappings
├── tests/unit/test_weather_service.py (with fixtures)
├── tests/unit/test_places_service.py (with fixtures)
└── Verify: GET /weather?lat=35.67&lon=139.65&days=5 returns clean JSON
└── Verify: GET /places?lat=35.67&lon=139.65&category=food&radius=5000
```

**Git:** `feat: weather and places integration`

---

### Phase 4: Agent Base + Researcher (Days 8-11)

**Goal:** First agent works. Calls Groq with tools, executes weather/places lookups.

```
Tasks:
├── app/planning/agents/base_agent.py — Groq call + tool loop
├── app/planning/tools/tool_registry.py — tool definitions as JSON schema
├── app/planning/tools/weather_tool.py — get_weather tool definition + executor
├── app/planning/tools/places_tool.py — search_places tool definition + executor
├── app/planning/agents/researcher_agent.py — uses tools to gather data
├── app/planning/prompt_builder.py — system prompt construction
├── scripts/test_groq_connection.py — verify API key + model works
├── tests/unit/test_prompt_builder.py
├── tests/unit/test_tool_registry.py
└── Verify: researcher_agent.run(prompt) → calls weather + places → returns ResearchBundle
```

**Git:** `feat: researcher agent with tool calling`

---

### Phase 5: Planner + Synthesizer Agents (Days 12-15)

**Goal:** Full pipeline produces a valid itinerary (no streaming yet).

```
Tasks:
├── app/planning/agents/planner_agent.py — persona detection + schedule reasoning
├── app/planning/agents/synthesizer_agent.py — strict JSON output via structured output
├── app/planning/schemas.py — ItinerarySchema + all nested models
├── app/planning/service.py — orchestrates: researcher → planner → synthesizer
├── Wire into trips: POST /trips now runs the pipeline
├── Save itinerary to itineraries table
├── tests/unit/test_itinerary_schema.py
├── tests/integration/test_planning_pipeline.py (mocked Groq)
└── Verify: POST /trips with a prompt → DB has a valid itinerary JSON
```

**Git:** `feat: planner and synthesizer agents — full pipeline`

---

### Phase 6: Critic Agent + Conflict Detection (Days 16-18)

**Goal:** Plans are reviewed, conflicts detected and stored.

```
Tasks:
├── app/planning/agents/critic_agent.py — reviews itinerary
├── Add haversine distance util to app/common/
├── Add deterministic checks (distance, timing) before critic runs
├── Critic output → stored in itineraries.conflicts
├── Update TripDetail response to include conflicts
├── tests/unit/test_conflict_detection.py
└── Verify: a trip with two far-apart consecutive activities → conflict flagged
```

**Git:** `feat: critic agent with conflict detection`

---

### Phase 7: SSE Streaming (Days 19-21)

**Goal:** Frontend can watch the pipeline in real time.

```
Tasks:
├── app/planning/router.py — SSE endpoint using EventSourceResponse
├── Refactor planning/service.py to yield events at each step
├── Define SSE event types and payload schemas
├── Add keepalive pings (every 15s) for proxy compatibility
├── tests/integration/test_sse_stream.py
└── Verify: EventSource connection receives correct event sequence
```

**Git:** `feat: SSE streaming for agent pipeline`

---

### Phase 8: Regeneration (Days 22-25)

**Goal:** Users can regenerate full trip, one day, or one block with constraints.

```
Tasks:
├── app/regeneration/schemas.py — RegenerateRequest
├── app/regeneration/service.py — partial regeneration logic
├── app/regeneration/router.py — POST /trips/:id/regenerate
├── Handle itinerary versioning (old → inactive, new → active)
├── Re-run critic on changed portions only
├── Support constraint-aware replanning (one-line replan)
├── tests/integration/test_regeneration.py
└── Verify: regenerate a single evening block with "make it vegetarian"
```

**Git:** `feat: regeneration — full trip, day, and block level`

---

### Phase 9: Auth + User Scoping (Days 26-28)

**Goal:** Supabase Auth integrated. Trips are user-scoped.

```
Tasks:
├── app/core/dependencies.py — JWT verification via Supabase Auth
├── Update all trip queries to filter by user_id
├── Support guest mode (user_id = null, trips saved but not scoped)
├── Add auth middleware that extracts user from Bearer token
├── tests/integration/test_auth_flow.py
└── Verify: user A cannot see user B's trips
```

**Git:** `feat: Supabase Auth integration`

---

### Phase 10: Polish + Deploy (Days 29-32)

**Goal:** Production-ready, deployed on Railway.

```
Tasks:
├── Add request rate limiting (slowapi or custom)
├── Add structured logging with request IDs
├── Add OpenAPI docs customization (title, description, tags)
├── Final Dockerfile optimization (multi-stage build)
├── Railway deployment config (railway.toml or Procfile)
├── Environment variables set in Railway dashboard
├── CORS configured for production frontend domain
├── Smoke test all endpoints in production
├── Write README.md with setup instructions
└── Verify: deployed URL returns /health 200, full pipeline works
```

**Git:** `feat: production deployment on Railway`

---

## 15. Git Strategy

### Branch Model

```
main              ← production-ready, deployed
  └── develop     ← integration branch
       ├── feat/skeleton
       ├── feat/trip-crud
       ├── feat/weather-places
       ├── feat/researcher-agent
       ├── feat/planner-synthesizer
       ├── feat/critic-agent
       ├── feat/sse-streaming
       ├── feat/regeneration
       ├── feat/auth
       └── feat/deploy
```

### Commit Convention

```
feat: <description>       — new feature
fix: <description>        — bug fix
refactor: <description>   — restructure without behavior change
test: <description>       — add/update tests
docs: <description>       — documentation
chore: <description>      — tooling, deps, config
```

### Commit at Every Checkpoint

Every task in the build order gets its own commit. Never batch unrelated changes. A clean git log is part of the portfolio.

---

## 16. Deployment (Railway)

### Dockerfile

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app/ ./app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Railway Config

- **Build:** Docker
- **Port:** 8000
- **Health check:** `/api/v1/health`
- **Env vars:** Set all from `.env.example` in Railway dashboard
- **Region:** US East (closest to Groq servers)

### What "Done" Looks Like

When Phase 10 is complete, you have:

1. A live backend URL on Railway
2. 10+ endpoints that work
3. A multi-agent pipeline that generates real itineraries
4. SSE streaming that a frontend can consume
5. Conflict detection that catches real problems
6. Regeneration at 3 levels of granularity
7. A clean, testable, well-structured codebase
8. A git history that tells a story

---

## Appendix: Key File Responsibility Map

| File | Responsibility | Never Does |
|---|---|---|
| `router.py` | HTTP in/out, request validation, response shaping | Business logic, DB queries, external API calls |
| `service.py` | Business logic, orchestration, data transformation | HTTP concerns, direct DB queries |
| `repository.py` | Supabase reads/writes, query construction | Business logic, HTTP concerns |
| `client.py` | Raw HTTP calls to external APIs | Data transformation, business logic |
| `schemas.py` | Pydantic models, validation rules | Logic of any kind |
| `agents/*.py` | LLM interaction, tool calling, prompt execution | Direct DB access, HTTP routing |
| `tools/*.py` | Tool JSON definitions + local execution functions | LLM interaction, routing |

This separation means you can swap Supabase for raw Postgres, swap Groq for OpenAI, or swap Open-Meteo for another weather API — each change touches exactly one file.
