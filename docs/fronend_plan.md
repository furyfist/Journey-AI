## Journey AI — Frontend Build Plan

### Stack

| Concern | Choice |
|---|---|
| Framework | Next.js 15 (App Router) |
| Styling | Tailwind CSS v4 + shadcn/ui |
| Auth | Supabase JS v2 (`@supabase/ssr`) |
| State (cross-route) | Zustand (prompt echo only) |
| Server state | Custom hooks with native fetch |
| Fonts | `next/font/google` (Instrument Sans) |

---

### Placement in Repo

The frontend lives at `frontend/` inside the existing `journey_ai` monorepo.

```
journey_ai/
├── app/          # FastAPI backend (existing)
├── frontend/     # Next.js app (this plan)
└── docs/
```

---

### Design System

**CSS variables in `globals.css`**

```
--background:     #FAF9F6    warm off-white
--surface:        #FFFFFF    card white
--border:         #EBEBEB    subtle card border
--accent:         #7C9A7E    sage green (primary)
--accent-light:   #EEF3EE    sage tint (badges, hovers)
--text-primary:   #1A1A1A    near black
--text-secondary: #6B6B6B    medium grey
--text-muted:     #A8A8A8    metadata grey
--warning:        #F5A623    amber (soft conflicts)
--danger:         #E07070    rose (critical conflicts)
```

**Typography** — `Instrument Sans` via `next/font/google`. Weight hierarchy through size + spacing only, never bold.

**Shadow system** — one token: `shadow-sm` (`0 1px 4px rgba(0,0,0,0.06)`). Never `shadow-lg`.

**Badge component** — two variants: `persona` (sage tint bg) and `budget` (neutral grey bg). Shared across all pages.

---

### Folder Structure

```
frontend/
├── app/
│   ├── (public)/                         # route group — no auth required
│   │   ├── page.tsx                      # Landing (/)
│   │   └── generate/
│   │       └── [tripId]/
│   │           └── page.tsx              # Live generation screen
│   ├── (protected)/                      # route group — auth required
│   │   ├── layout.tsx                    # auth guard layout — redirects to /auth if no session
│   │   └── trips/
│   │       ├── page.tsx                  # My Trips library
│   │       └── [tripId]/
│   │           └── page.tsx              # Itinerary page
│   ├── auth/
│   │   └── page.tsx                      # Login / Sign up
│   ├── error.tsx                         # Next.js top-level error boundary
│   ├── not-found.tsx                     # 404 page
│   ├── layout.tsx                        # Root layout — font, providers, global styles
│   └── globals.css
│
├── components/
│   ├── ui/                               # shadcn primitives (auto-generated, do not edit)
│   ├── shared/
│   │   ├── Badge.tsx                     # persona + budget variants
│   │   ├── Navbar.tsx                    # minimal top nav
│   │   └── PageWrapper.tsx               # consistent padding + max-width
│   ├── landing/
│   │   ├── PromptInput.tsx
│   │   ├── ExampleChips.tsx
│   │   └── HowItWorks.tsx
│   ├── generate/
│   │   ├── AgentPipeline.tsx             # 5-node pipeline (see agent names below)
│   │   ├── LiveLog.tsx                   # renders all 9 SSE event types
│   │   └── PromptEcho.tsx                # reads prompt from Zustand generate store
│   ├── itinerary/
│   │   ├── TripHeader.tsx                # title, badges, summary, tips accordion
│   │   ├── DayNav.tsx                    # sticky sidebar (desktop) / tabs (mobile)
│   │   ├── DaySection.tsx                # day wrapper
│   │   ├── TimeBlock.tsx                 # morning / afternoon / evening wrapper
│   │   ├── ActivityCard.tsx              # card with "Why This?" collapsible
│   │   ├── WeatherStrip.tsx              # inline weather one-liner
│   │   ├── ConflictBanner.tsx            # amber (warning) / rose (error) inline alert
│   │   └── RegenerateControl.tsx         # scope-aware regen trigger + constraint input
│   └── trips/
│       ├── TripCard.tsx
│       └── EmptyState.tsx
│
├── lib/
│   ├── api/
│   │   ├── client.ts                     # base fetch — injects auth header, throws typed ApiError
│   │   ├── trips.ts                      # createTrip, getTrip, listTrips, deleteTrip
│   │   └── regenerate.ts                 # regenerateTrip
│   ├── supabase/
│   │   ├── client.ts                     # createBrowserClient() — use in components + hooks
│   │   └── server.ts                     # createServerClient() — use in middleware + server components
│   ├── sse.ts                            # SSEEvent union type + 9 event type constants
│   └── types/
│       ├── trip.ts                       # TripCreate, TripResponse, TripDetail, TripListItem
│       ├── planning.ts                   # ItinerarySchema, DayPlan, TimeBlock, Activity, Conflict, SSEEvent
│       └── regenerate.ts                 # RegenerateRequest, RegenerateScope
│
├── hooks/
│   ├── useSSEStream.ts                   # EventSource lifecycle, all 9 events
│   ├── useTrip.ts                        # GET /trips/:id → TripDetail
│   ├── useTrips.ts                       # GET /trips → TripListItem[]
│   ├── useRegenerate.ts                  # POST /trips/:id/regenerate → TripDetail + loading state
│   └── useAuth.ts                        # Supabase session + user
│
├── store/
│   └── generate.ts                       # Zustand: { prompt, setPrompt } — bridges landing → generate page
│
├── providers/
│   └── index.tsx                         # composes providers used in root layout (auth, etc.)
│
├── middleware.ts                         # guards /(protected) routes via Supabase session check
├── components.json                       # shadcn config
├── tailwind.config.ts
├── next.config.ts
└── .env.local.example
```

---

### Page-by-Page Breakdown

**Page 1 — Landing (`/`)**

- Centered layout, `max-w-2xl`, generous vertical whitespace
- `PromptInput` — large `<textarea>`, borderless inside a white card, placeholder: *"Describe your trip in plain English..."*
- On submit:
  1. `POST /api/v1/trips` with `{ prompt }` → receives `TripResponse` including `id`
  2. Write `prompt` to Zustand `generate` store (for `PromptEcho` on the next page)
  3. Redirect to `/generate/[id]`
- `ExampleChips` — wrapping row on desktop, horizontal scroll on mobile. Click pre-fills textarea
- `HowItWorks` — 3 numbered items, text only, no icons, no cards

---

**Page 2 — Live Generation (`/generate/[tripId]`)**

- `PromptEcho` — reads prompt from Zustand store, renders it in a subtle blockquote card at top
- `AgentPipeline` — **5 nodes** driven entirely by SSE events:

  ```
  researcher → planner → synthesizer → conflict_checker → critic
  ```

  These are the exact agent name strings emitted by the backend in the `agent` field.

  | SSE event | Pipeline effect |
  |---|---|
  | `agent_start` (agent=X) | activate node X — pulsing sage dot |
  | `agent_complete` (agent=X) | mark node X done — checkmark |
  | `agent_start` (agent=critic) | also marks `conflict_checker` complete — backend emits no `agent_complete` for it |

- SSE connection via `useSSEStream` hook → `GET /api/v1/trips/{tripId}/stream`

- `LiveLog` — one line per event, 80ms staggered CSS transition:

  | Event type | Prefix | What to show |
  |---|---|---|
  | `agent_start` | ◆ | `agent` name + `message` |
  | `tool_call` | 🔍 | tool name from `data` |
  | `tool_result` | · | result summary from `data` |
  | `agent_progress` | · | `message` |
  | `agent_complete` | ✓ | `agent` + `message` |
  | `conflict_detected` | ⚠ | `data.description` |
  | `trip_complete` | ✓ | destination + total_conflicts from `data` |
  | `error` | ✕ | `message` in danger colour + retry button |
  | `keepalive` | — | silently discarded, never rendered |

- On `trip_complete`: auto-redirect to `/trips/[tripId]`
- On `error`: show inline error with retry button. Retry re-navigates to the same URL, which re-opens the SSE stream from scratch

---

**Page 3 — Itinerary (`/trips/[tripId]`)**

Data source: `GET /api/v1/trips/{tripId}` → `TripDetail`. `TripDetail.itinerary` arrives as a raw `dict` from the backend — cast it to the local `ItinerarySchema` type after fetch; do not assume it arrives typed.

```
TripHeader
  ├── title, destination, total_days
  ├── Budget badge (itinerary.budget_level) + Persona badge (trip.persona)
  ├── summary (2-3 sentences)
  └── Tips accordion (3-5 items, collapsed by default)

DayNav (sticky)
  ├── Desktop: left sidebar, highlights active day via IntersectionObserver
  └── Mobile: horizontal scroll tabs, sticky top

[For each day in itinerary.days:]
DaySection
  ├── Day number + date + creative title
  ├── WeatherStrip (icon + temp + condition — from day.weather)
  ├── day_summary (one sentence, muted)
  └── [morning | afternoon | evening] TimeBlock
        ├── label + start_time – end_time
        ├── block_summary
        ├── [For each activity:]
        │     ActivityCard
        │       ├── category icon + name + location
        │       ├── duration_minutes + cost_estimate
        │       ├── description
        │       └── "Why This?" collapsible → activity.reasoning
        └── ConflictBanner
              Shown if any item in TripDetail.conflicts matches
              this day_number. Match block via conflict.description
              (conflicts don't carry a block field — match on day only).
              severity="warning" → amber, severity="error" → rose

  RegenerateControl (scope: single_block) — bottom of each TimeBlock
  RegenerateControl (scope: day)          — bottom of each DaySection

RegenerateControl (scope: full_trip)      — page bottom
```

**RegenerateControl** — sends `POST /api/v1/trips/{tripId}/regenerate`. Request body must use the backend field names exactly:

```ts
{
  scope: "full_trip" | "day" | "single_block",
  day_number?: number,                              // required for day + single_block
  block_label?: "morning" | "afternoon" | "evening", // required for single_block — NOT "block"
  constraint?: string                               // optional natural language override
}
```

This endpoint is **synchronous** — it returns `TripDetail` directly. Do NOT redirect to `/generate/[tripId]`. Instead:
1. Show a loading overlay on the affected section
2. On success, update the itinerary state in-place from the response
3. On error, show an inline error message

---

**Page 4 — My Trips (`/trips`)**

- Fetches `GET /api/v1/trips` via `useTrips`
- Grid: 1 col mobile, 2 col tablet, 3 col desktop
- `TripCard` fields available in `TripListItem`: `id`, `title`, `destination`, `total_days`, `status`, `created_at`

  > **Backend note:** `persona` and `budget_level` are not in `TripListItem` today. To show persona/budget badges on TripCard, add those two fields to `TripListItem` in `app/trips/schemas.py`. Until that is done, the TripCard shows destination, date range, day count, and status dot only — no fake data.

- Status dot: `generating` → pulsing sage, `completed` → static sage, `failed` → rose
- Hover on desktop: `hover:shadow-md transition-shadow`, reveals Open + Delete quick actions
- "Plan a new trip" CTA at top
- `EmptyState`: centered text + single button — nothing else

---

**Page 5 — Auth (`/auth`)**

- Single centered white card, `max-w-sm`
- Toggle Login / Sign Up via local state — no route change
- Fields: email + password only
- If coming from a guest trip, show nudge: *"Sign up to save your trip"*. Use `?next=/trips/[id]` query param for redirect after login
- On success: Supabase sets session cookie → redirect to `next` param or `/trips`
- `middleware.ts` guards `/(protected)` group — redirects unauthenticated users to `/auth`
- Generation page is in `(public)` group — guest mode works, backend handles `user_id = null`

---

### API Layer

**`lib/api/client.ts`**

```ts
// Reads Supabase browser session, injects Authorization: Bearer <token> header.
// Guest calls (no session) send no auth header — backend handles user_id = null.
// Throws ApiError (with status + message) on non-2xx responses.
async function apiFetch<T>(path: string, init?: RequestInit): Promise<T>
```

**`lib/api/trips.ts`**

```ts
createTrip(payload: TripCreate): Promise<TripResponse>
getTrip(tripId: string): Promise<TripDetail>
listTrips(): Promise<TripListItem[]>
deleteTrip(tripId: string): Promise<void>
```

**`lib/api/regenerate.ts`**

```ts
regenerateTrip(tripId: string, req: RegenerateRequest): Promise<TripDetail>
```

---

### Types (`lib/types/`)

Mirror the backend Pydantic schemas exactly.

**`planning.ts`** — from `app/planning/schemas.py`

```ts
type SSEEventType =
  | "agent_start" | "tool_call" | "tool_result" | "agent_progress"
  | "agent_complete" | "conflict_detected" | "trip_complete"
  | "error" | "keepalive"

interface SSEEvent {
  event: SSEEventType
  agent?: string
  data?: unknown
  message?: string
}

// Conflict.severity: "warning" | "error"
// Conflict.type: "distance" | "timing" | "weather" | "budget" | "persona"
// Activity.category: "food" | "attraction" | "transport" | "shopping" | "nature" | "culture" | "nightlife"
// DayPlan has morning, afternoon, evening as TimeBlock (not an array)
```

**`regenerate.ts`** — from `app/regeneration/schemas.py`

```ts
type RegenerateScope = "full_trip" | "day" | "single_block"

interface RegenerateRequest {
  scope: RegenerateScope
  day_number?: number
  block_label?: "morning" | "afternoon" | "evening"  // field is block_label, not block
  constraint?: string
}
```

---

### SSE Hook (`hooks/useSSEStream.ts`)

```ts
// Opens EventSource to GET /api/v1/trips/{tripId}/stream
//
// Returns:
//   events:           SSEEvent[]     — full log, consumed by LiveLog
//   activeAgent:      string | null  — set on agent_start, cleared on agent_complete
//   completedAgents:  string[]       — accumulates agent names as agent_complete fires
//   status:           "connecting" | "streaming" | "complete" | "error"
//   isComplete:       boolean        — true once trip_complete fires
//   error:            string | null  — populated from error event message
//
// keepalive events are silently discarded.
// No auto-reconnect — surface error state and let user retry via button.
// Closes EventSource on component unmount.
```

Both `AgentPipeline` and `LiveLog` consume this hook. Pass the return value via props or a local React context — no prop drilling through intermediary components.

---

### Build Order

| Phase | Work |
|---|---|
| 1 | `frontend/` scaffold: Next.js 15, Tailwind v4, shadcn init, `globals.css` tokens, shared components (Badge, Navbar, PageWrapper) |
| 2 | Landing page — PromptInput, ExampleChips, HowItWorks, Zustand generate store |
| 3 | Auth page + Supabase browser/server clients + middleware |
| 4 | My Trips page + TripCard (no badges until backend extended) + EmptyState |
| 5 | Generation page — AgentPipeline (5 nodes) + LiveLog with mock SSE data |
| 6 | `useSSEStream` wired to real backend stream, all 9 event types handled |
| 7 | Itinerary page — full structure with static fixture data |
| 8 | RegenerateControl wired to real endpoint — in-place update, no redirect |
| 9 | ConflictBanner — match against `TripDetail.conflicts` by `day_number` |
| 10 | Polish — mobile QA, loading states, error boundaries, empty states |
