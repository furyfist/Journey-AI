# Journey AI — 5-Session Chat Build Plan

> Each session ends at a clean, tested, committable checkpoint. At the end of every session,
> save memory notes so the next session picks up with full context.

---

## Overview

| Session | Phases Covered | Key Deliverable |
|---|---|---|
| 1 | Phase 1–2 | Repo scaffold + Trip CRUD |
| 2 | Phase 3 | Weather + Places API integration |
| 3 | Phase 4–5 | Full AI pipeline → DB (no streaming yet) |
| 4 | Phase 6–7 | Critic agent + SSE streaming |
| 5 | Phase 8–10 | Regeneration + Auth + Railway deploy |

---

## Session 1 — Foundation

**Covers:** Phase 1 (Skeleton) + Phase 2 (Trip CRUD)

**Goal:** Repo boots, DB connects, Trip CRUD works end-to-end.

### Tasks
- Full project scaffold — all folders, `__init__.py`, `pyproject.toml`, `Makefile`
- `app/core/` — `config.py`, `database.py`, `exceptions.py`, `exception_handlers.py`
- `app/common/` — `logger.py`, `http_client.py`
- `app/health/router.py` — `GET /health` (checks DB + external API reachability)
- `app/trips/` — `schemas.py`, `repository.py`, `service.py`, `router.py`
- SQL migrations 001, 002, 003 run in Supabase dashboard
- `Dockerfile` + `docker-compose.yml`
- `.env.example`, `.gitignore`

### Done When
- `POST /api/v1/trips`, `GET /api/v1/trips`, `GET /api/v1/trips/{id}`, `DELETE /api/v1/trips/{id}` all return correct responses via curl
- `GET /api/v1/health` returns 200

### Git Commit
```
feat: project skeleton with health check
feat: trip CRUD with Supabase
```

---

## Session 2 — External APIs

**Covers:** Phase 3 (Weather + Places Integration)

**Goal:** Weather and places data flowing cleanly through standalone endpoints.

### Tasks
- `app/weather/` — `client.py`, `schemas.py`, `service.py` (WMO code mapping), `router.py`
- `app/places/` — `client.py`, `schemas.py`, `service.py` (Overpass QL builder + transform), `router.py`
- `app/common/constants.py` — WMO weather codes, OSM tag mappings
- `tests/unit/test_weather_service.py` — with JSON fixtures
- `tests/unit/test_places_service.py` — with JSON fixtures
- `tests/mocks/mock_weather_data.py`

### Done When
- `GET /api/v1/weather?lat=35.67&lon=139.65&days=5` returns clean validated JSON with human-readable weather descriptions
- `GET /api/v1/places?lat=35.67&lon=139.65&category=food&radius=5000` returns a list of places with name, lat, lon, category
- Unit tests pass

### Git Commit
```
feat: weather and places integration
```

---

## Session 3 — Agent Pipeline (Heaviest Session)

**Covers:** Phase 4 (Researcher Agent) + Phase 5 (Planner + Synthesizer)

**Goal:** Full Researcher → Planner → Synthesizer pipeline produces a valid `ItinerarySchema` JSON and saves to DB. No streaming yet — pipeline runs synchronously.

### Tasks
- `app/planning/schemas.py` — `ItinerarySchema`, `DayPlan`, `TimeBlock`, `Activity` (all nested models)
- `app/planning/agents/base_agent.py` — Groq call + tool-call loop
- `app/planning/tools/tool_registry.py` — central tool definitions as JSON schema
- `app/planning/tools/weather_tool.py` — tool definition + executor
- `app/planning/tools/places_tool.py` — tool definition + executor
- `app/planning/agents/researcher_agent.py` — calls weather + places tools, returns `ResearchBundle`
- `app/planning/prompt_builder.py` — system prompt construction per agent
- `app/planning/agents/planner_agent.py` — persona detection + schedule reasoning
- `app/planning/agents/synthesizer_agent.py` — strict JSON output via Groq structured output mode
- `app/planning/service.py` — orchestrates researcher → planner → synthesizer
- Wire `POST /api/v1/trips` to trigger pipeline and save to `itineraries` table
- `scripts/test_groq_connection.py` — verify API key + model availability
- `tests/unit/test_prompt_builder.py`
- `tests/integration/test_planning_pipeline.py` — mocked Groq responses

### Natural Cut Point (if session runs long)
End after Researcher agent working (`researcher_agent.run(prompt)` calls weather + places and returns a `ResearchBundle`). Continue from Planner in the next session before moving to Session 4.

### Done When
- `POST /api/v1/trips` with a natural language prompt completes synchronously and saves a validated `ItinerarySchema` to Supabase
- `GET /api/v1/trips/{id}` returns the full itinerary JSON

### Git Commits
```
feat: researcher agent with tool calling
feat: planner and synthesizer agents — full pipeline
```

---

## Session 4 — Critic + SSE Streaming

**Covers:** Phase 6 (Critic Agent) + Phase 7 (SSE Streaming)

**Goal:** Plans are reviewed for conflicts, and the entire pipeline streams events to the client in real time.

### Tasks
- `app/common/` — haversine distance util
- Deterministic conflict checks (distance, timing math) — run in Python before critic
- `app/planning/agents/critic_agent.py` — weather mismatches, distance conflicts, timing feasibility
- Conflicts stored in `itineraries.conflicts`, returned in `TripDetail` response
- Refactor `planning/service.py` to `async yield` SSE events at each step
- `app/planning/router.py` — `GET /api/v1/trips/{trip_id}/stream` with `EventSourceResponse`
- Full SSE event type definitions (`agent_start`, `tool_call`, `tool_result`, `agent_progress`, `agent_complete`, `conflict_detected`, `trip_complete`, `error`)
- 15-second keepalive pings for proxy compatibility
- `tests/integration/test_sse_stream.py`
- `tests/unit/test_conflict_detection.py`

### Done When
- Connecting to `GET /api/v1/trips/{trip_id}/stream` shows a live sequence of typed SSE events
- A trip with two far-apart consecutive activities has a conflict flagged and stored in DB

### Git Commits
```
feat: critic agent with conflict detection
feat: SSE streaming for agent pipeline
```

---

## Session 5 — Regeneration + Auth + Deploy

**Covers:** Phase 8 (Regeneration) + Phase 9 (Auth) + Phase 10 (Polish + Deploy)

**Goal:** Users can replan at any granularity, trips are user-scoped, and the backend is live on Railway.

### Tasks

**Regeneration**
- `app/regeneration/schemas.py` — `RegenerateRequest`, `RegenerateScope` enum
- `app/regeneration/service.py` — partial regeneration, itinerary patching
- `app/regeneration/router.py` — `POST /api/v1/trips/{id}/regenerate`
- Itinerary versioning — old version flips to `is_active = false`, new gets `version + 1`
- Critic re-runs only on changed block (not full trip)
- One-line replan with `constraint` field
- `tests/integration/test_regeneration.py`

**Auth**
- `app/core/dependencies.py` — JWT verification via Supabase Auth
- Auth middleware to extract user from Bearer token
- Update all trip repository queries to filter by `user_id`
- Guest mode — `user_id = null`, trips saved but not scoped
- `tests/integration/test_auth_flow.py`

**Deploy**
- Rate limiting (slowapi or custom middleware)
- Structured logging with request IDs
- OpenAPI docs customization (title, tags, descriptions)
- Multi-stage Dockerfile optimization
- `railway.toml` config
- CORS updated for production frontend domain
- Smoke test all endpoints on Railway
- `README.md` with setup instructions

### Done When
- Live Railway URL returns `GET /health` 200
- Full pipeline works end-to-end in production
- User A cannot access User B's trips
- `POST /api/v1/trips/{id}/regenerate` with `scope=single_block` + `constraint="make it vegetarian"` returns an updated itinerary

### Git Commits
```
feat: regeneration — full trip, day, and block level
feat: Supabase Auth integration
feat: production deployment on Railway
```

---

## Session Handoff Checklist

At the end of each session, confirm before closing:

- [ ] All planned endpoints tested via curl or Postman
- [ ] Relevant unit/integration tests passing
- [ ] Changes committed with correct commit message convention
- [ ] `.env.example` updated if new env vars were added
- [ ] No secrets committed (check `.gitignore`)
- [ ] Note any decisions made that deviate from `backend_build_plan.md`
