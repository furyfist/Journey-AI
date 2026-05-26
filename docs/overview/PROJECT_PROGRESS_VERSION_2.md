# Journey AI — Project Progress Version 2

> Snapshot date: May 27, 2026
>
> Purpose: a practical, current-state project progress document that tells us what is built, what has been verified, what changed recently, and what still remains.

---

## 1. Current Status

Journey AI is now a working guest-mode AI travel planner with:

- trip creation
- SSE-based itinerary generation
- structured trip input
- direct HTTP research fetching
- synthesizer-only planning flow
- deterministic + LLM conflict detection
- partial regeneration at 3 scopes
- frontend regeneration controls wired into the itinerary UI

The regeneration system has now been:

- aligned with the current optimized pipeline
- validated against bad targets
- hardened around version selection
- covered by expanded automated tests
- live-verified against a real trip in Supabase

Authentication is not part of the active product direction.

---

## 2. What Is Fully Built

### Backend core

Implemented:

- FastAPI app setup and dependency wiring
- health endpoint
- trip CRUD endpoints
- planning pipeline services
- regeneration endpoint
- weather and places standalone endpoints
- Supabase persistence

Key backend areas:

- `app/trips/`
- `app/planning/`
- `app/regeneration/`
- `app/weather/`
- `app/places/`

### Main planning pipeline

Implemented:

- structured payload support in trip creation
- async `fetch_research()` with Open-Meteo + Overpass
- synthesizer-only itinerary generation
- deterministic conflict checks before critic
- SSE streaming with `trip_complete` before critic
- post-itinerary critic review with persisted conflict updates

This means the older planner-heavy primary flow is no longer the main generation path.

### Regeneration system

Implemented and verified:

- `scope=full_trip`
- `scope=day`
- `scope=single_block`

Current regeneration behavior:

- full trip uses the current synthesizer-first regeneration flow
- day regeneration preserves `day_number`, `date`, and `weather`
- block regeneration preserves `label`, `start_time`, and `end_time`
- invalid targets fail early with `400`
- latest active itinerary is chosen by `version desc`
- regeneration returns a full updated `TripDetail`

### Frontend

Implemented:

- landing page
- 2-step trip creation flow
- generation page SSE behavior
- itinerary page
- full-trip/day/block regeneration controls
- error/loading handling in regeneration controls

Key frontend regeneration files:

- `frontend/components/itinerary/RegenerateControl.tsx`
- `frontend/components/itinerary/DaySection.tsx`
- `frontend/components/itinerary/TimeBlock.tsx`
- `frontend/hooks/useRegenerate.ts`
- `frontend/app/(protected)/trips/[tripId]/page.tsx`

---

## 3. What Was Verified Recently

### Automated verification

Regeneration hardening work was verified on May 27, 2026 with:

- `tests/integration/test_regeneration.py`
- `tests/integration/test_trip_endpoints.py`

Covered behaviors include:

- full-trip regeneration uses the current synthesizer-only path
- structured context restoration during regeneration
- invalid day/block targets return `400`
- invalid targets fail before any regeneration agent call
- version increment behavior
- deactivation of active rows before inserting the next version
- constraint forwarding for day and block scopes
- merged deterministic + critic conflict persistence
- route response shape

Frontend verification completed on May 27, 2026 with:

- `npm run lint` in `frontend/`

Frontend build status:

- `npm run build` was blocked by Google Fonts fetch for `Instrument Sans`
- this was an environment/network issue, not a regeneration code issue

### Live verification

Live verification was run against the local backend and real Supabase data on May 27, 2026.

Verified on real trip:

- `full_trip` regeneration succeeded
- `day` regeneration succeeded
- `single_block` regeneration succeeded after one temporary Groq rate-limit response

Observed outcomes:

- updated `TripDetail` payload returned in each successful case
- itinerary content changed according to scope
- conflict lists were recomputed
- version history advanced correctly
- only one itinerary row remained active after repeated regenerations

### Historical duplicate cleanup

One duplicate historical itinerary version group was found in Supabase:

- trip `87ba3db4-da3b-489f-b85f-a1336b003c36`
- duplicate `version = 3`

Cleanup completed:

- removed the older duplicate row
- kept the later, more relevant historical row
- re-verified that the trip now has versions `1, 2, 3, 4`
- confirmed only version `4` is active

Preventative follow-up added:

- `migrations/005_enforce_unique_itinerary_trip_version.sql`

This migration adds a unique index on:

- `(trip_id, version)`

---

## 4. Important Current Architecture Notes

### No-auth direction

Current product direction:

- guest-mode usage
- no active auth roadmap

Important nuance:

- the database schema still contains a nullable legacy `user_id` column for compatibility
- the active app flow does not depend on auth

### Versioning rules

Current intended invariants:

- exactly one active itinerary per trip
- itinerary versions increase over time
- no two rows should share the same `(trip_id, version)`

The active-row invariant is already functioning in live data.

The version uniqueness invariant is now backed by migration `005`, which should be applied to Supabase.

### Rate limits

Groq rate limits are still a real runtime behavior.

Observed live behavior:

- a single-block regeneration request returned a rate-limit error once
- retry later succeeded without code changes

This is not a correctness bug in regeneration, but it is still a real operational constraint for demos and testing.

---

## 5. Files Changed During Regeneration Hardening Work

### Backend logic

- `app/regeneration/service.py`
- `app/regeneration/repository.py`
- `app/core/exceptions.py`
- `app/trips/repository.py`

### Backend tests

- `tests/integration/test_regeneration.py`
- `tests/integration/test_trip_endpoints.py`

### Frontend

- `frontend/lib/types/trip.ts`
- `frontend/app/(protected)/trips/[tripId]/page.tsx`
- `frontend/components/landing/TripDetailsForm.tsx`

### Documentation and migration

- `docs/overview/PROJECT_OVERVIEW.md`
- `docs/overview/PROJECT_PROGRESS_VERSION_2.md`
- `migrations/005_enforce_unique_itinerary_trip_version.sql`

---

## 6. What Still Remains

The regeneration plan itself is complete.

What remains at the project level is mostly polish and deployment work:

- apply migration `005` in Supabase if it has not yet been run manually
- deployment setup and production polish
- final production environment review
- optional cleanup of any old docs that are now superseded by version 2 progress tracking

Potential nice-to-have follow-ups:

- friendlier UI treatment for backend rate-limit errors
- explicit frontend test coverage for regeneration controls
- database-level cleanup scripts for future maintenance tasks

---

## 7. Recommended Source Of Truth Usage

Use these docs like this:

- `docs/overview/PROJECT_OVERVIEW.md`
  - full architectural reference
- `docs/overview/PROJECT_PROGRESS_VERSION_2.md`
  - current delivery/progress status and verified state

If future work changes the shipped behavior materially, update both:

- the architecture reference
- this progress/status document

---

## 8. Practical Resume Point

If resuming work from here, the clean next step is:

1. apply migration `005` in Supabase
2. focus on deployment / production polish
3. optionally add frontend tests around regeneration interactions

If resuming debugging instead, start with:

- `app/regeneration/service.py`
- `tests/integration/test_regeneration.py`
- `frontend/app/(protected)/trips/[tripId]/page.tsx`

These three areas now define most of the real regeneration behavior.
