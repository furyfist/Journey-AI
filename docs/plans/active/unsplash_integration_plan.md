# Plan: Unsplash Photo Integration

**Goal:** Use the Unsplash API to fetch destination photos for the app without exposing credentials in the frontend, starting with the landing page and leaving room to expand into trip detail surfaces later.

---

## Why Backend-First

Unsplash credentials should stay server-side. The frontend currently has no image API flow, and the landing page component `frontend/components/landing/DestinationsShowcase.tsx` still renders placeholder image blocks, which makes it the safest and highest-value first integration point.

**Recommended architecture:**
- Backend stores and uses the Unsplash keys
- Backend fetches and normalizes photo responses
- Frontend consumes a small internal API
- Server-side caching reduces repeat calls and protects rate limits

---

## Phase 1 - Configuration and Backend Contract

**Objective:** Prepare the project to talk to Unsplash in a safe, maintainable way.

### Tasks

1. Add backend settings in `app/core/config.py`
   - `unsplash_access_key: str = ""`
   - `unsplash_secret_key: str = ""`
   - `unsplash_base_url: str = "https://api.unsplash.com"`

2. Add env documentation
   - Keep `UNSPLASH_ACCESS_KEY` and `UNSPLASH_SECRET_KEY` in `.env`
   - Keep placeholders in `.env.example`

3. Define response shape for frontend consumption
   - `query`
   - `image_url`
   - `thumb_url`
   - `alt_text`
   - `photographer_name`
   - `photographer_url`
   - `unsplash_page_url`
   - `source`

4. Decide lookup mode
   - Default to `search/photos`
   - Start with `per_page=1`
   - Use curated search terms for better landing page results

### Deliverables

- Config fields added
- Clear internal photo response schema
- Env files aligned

### Exit Criteria

- Backend can read the Unsplash env vars
- We have a stable internal contract before UI wiring begins

---

## Phase 2 - Unsplash Client and Service Layer

**Objective:** Build a small backend integration that isolates Unsplash-specific logic.

### Tasks

1. Add a client module
   - Suggested file: `app/photos/client.py`
   - Handle auth header using `Client-ID {access_key}`
   - Call Unsplash search endpoint

2. Add a service module
   - Suggested file: `app/photos/service.py`
   - Normalize raw Unsplash responses into the app's internal schema
   - Apply query cleanup like `"Tokyo, Japan" -> "Tokyo skyline"`
   - Return a fallback object when no result is found

3. Add simple error handling
   - Handle timeouts
   - Handle rate-limit responses
   - Handle invalid credentials
   - Log failures without breaking page render

4. Add attribution mapping
   - Preserve photographer and source links required for display

### Deliverables

- Reusable Unsplash client
- Reusable photo service
- Normalized backend data model

### Exit Criteria

- A backend function can return one normalized image object for a destination query

---

## Phase 3 - Internal API Endpoint

**Objective:** Expose a frontend-safe API for fetching destination photos.

### Tasks

1. Add router files
   - Suggested files:
   - `app/photos/router.py`
   - `app/photos/schemas.py`

2. Add endpoints
   - `GET /photos/search?query=Tokyo`
   - Optional batch endpoint later: `POST /photos/batch`

3. Register the router in `app/main.py`

4. Add response rules
   - Return `200` with normalized photo object when found
   - Return `200` with `image_url: null` fallback when not found
   - Return `503` only for truly blocking backend failures if needed

### Deliverables

- One backend endpoint for photo search
- Clear API contract for frontend integration

### Exit Criteria

- Frontend can request a destination photo without touching Unsplash directly

---

## Phase 4 - Landing Page Integration

**Objective:** Replace the current placeholder blocks in the landing page showcase with real destination photos.

### Tasks

1. Update `frontend/components/landing/DestinationsShowcase.tsx`
   - Replace the empty `aspect-video` placeholder with a real image surface
   - Show loading and fallback states

2. Add frontend API helper
   - Suggested file: `frontend/lib/api/photos.ts`

3. Decide data-loading strategy
   - Preferred first pass: fetch on the server if the page/component structure supports it cleanly
   - Acceptable fallback: client fetch with loading skeletons

4. Add attribution UI
   - Photographer name
   - Link to photographer profile
   - Optional small "on Unsplash" label

5. Preserve layout quality
   - Ensure aspect ratio remains stable
   - Ensure mobile layout stays intact
   - Keep placeholders when the API is unavailable

### Deliverables

- Landing page using real destination images
- Attribution visible in the UI
- Fallback UX that does not break layout

### Exit Criteria

- `DestinationsShowcase` no longer shows empty image boxes during normal operation

---

## Phase 5 - Caching and Query Quality

**Objective:** Improve reliability, speed, and API usage efficiency.

### Tasks

1. Add caching
   - In-memory cache is fine for first pass
   - Cache by normalized destination query
   - Add a TTL such as 6 to 24 hours

2. Add curated queries
   - Example:
   - `"Tokyo, Japan" -> "Tokyo city skyline"`
   - `"Shibuya & Harajuku" -> "Shibuya street Tokyo"`

3. Add fallback image behavior
   - If Unsplash returns nothing, keep the styled placeholder

4. Add request guards
   - Limit repeated calls per page render
   - Avoid fetching duplicate queries in one request cycle

### Deliverables

- Lower API usage
- More relevant image results
- Better resilience

### Exit Criteria

- Repeated landing page visits do not generate unnecessary upstream API calls

---

## Phase 6 - Testing and Verification

**Objective:** Lock in behavior so the integration is safe to iterate on.

### Tasks

1. Backend unit tests
   - Settings load correctly
   - Unsplash response normalization works
   - Fallback behavior works

2. Backend integration tests
   - Endpoint returns normalized objects
   - Endpoint handles upstream failures safely

3. Frontend tests
   - Loading state renders
   - Success state renders image and attribution
   - Fallback state renders placeholder

4. Manual verification
   - Home page loads cleanly
   - Photos appear in the showcase
   - Attribution is visible
   - Layout works on mobile and desktop

### Deliverables

- Test coverage around the new integration
- Manual QA checklist

### Exit Criteria

- The feature behaves predictably under success, empty, and failure cases

---

## Phase 7 - Optional Expansion

**Objective:** Reuse the photo system beyond the landing page once the first integration is stable.

### Good next targets

1. Trip cards in `frontend/components/trips/TripCard.tsx`
2. Trip header in `frontend/components/itinerary/TripHeader.tsx`
3. Destination hero surfaces for generated itineraries
4. Pre-fetching one representative city image during trip creation

### Guardrails

- Keep all Unsplash access server-side
- Reuse the same normalization and caching logic
- Avoid adding multiple duplicate photo fetches for the same destination on a single page

---

## Suggested Order of Work

1. Phase 1 - Config and schema
2. Phase 2 - Client and service
3. Phase 3 - Backend endpoint
4. Phase 4 - Landing page UI integration
5. Phase 5 - Caching and query refinement
6. Phase 6 - Tests and manual QA
7. Phase 7 - Optional expansion

---

## Estimated Effort

| Phase | Effort |
|---|---|
| Phase 1 | 15-20 min |
| Phase 2 | 45-60 min |
| Phase 3 | 20-30 min |
| Phase 4 | 45-75 min |
| Phase 5 | 20-30 min |
| Phase 6 | 45-60 min |
| **Total initial integration** | **~3 to 4.5 hours** |

---

## Recommendation

Start with the landing page only. It gives us visible value quickly, keeps the scope small, and lets us validate the API, attribution, and caching strategy before we spread photo fetching across the rest of the product.
