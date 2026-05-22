Let me read the backend build plan you uploaded before I finalize the frontend plan.I have everything I need. Here's the full picture — stack, API contract, SSE event types, schema, all 5 pages. Let me now give you the complete frontend plan.

---

## Journey AI — Frontend Build Plan

### Design System First

**Palette (Tailwind CSS variables in `globals.css`)**
```
--background: #FAF9F6       warm off-white
--surface: #FFFFFF          card white
--border: #EBEBEB           subtle card border
--accent: #7C9A7E           sage green (primary)
--accent-light: #EEF3EE     sage tint (badges, hovers)
--text-primary: #1A1A1A     near black
--text-secondary: #6B6B6B   medium grey
--text-muted: #A8A8A8       metadata grey
--warning: #F5A623          amber (soft conflicts)
--danger: #E07070           rose (critical conflicts)
```

**Typography** — Use `Instrument Sans` or `DM Sans` from Google Fonts. Size scale via Tailwind's default — no custom scale needed. Weight hierarchy only through size + spacing, not bold.

**Shadow system** — one shadow token: `shadow-sm` for cards (`0 1px 4px rgba(0,0,0,0.06)`). Never `shadow-lg` or `drop-shadow`.

**Badge component** — reused across all pages. Two variants: `persona` (sage tint bg) and `budget` (neutral grey bg). This is your internal design language.

---

### Folder Structure

```
journey-ai-frontend/
├── app/
│   ├── layout.tsx                  # Root layout, font, global styles
│   ├── page.tsx                    # Landing (/)
│   ├── generate/
│   │   └── [tripId]/
│   │       └── page.tsx            # Live generation screen
│   ├── trips/
│   │   ├── page.tsx                # My Trips library
│   │   └── [tripId]/
│   │       └── page.tsx            # Itinerary page
│   ├── auth/
│   │   └── page.tsx                # Login / Sign up
│   └── globals.css
│
├── components/
│   ├── ui/                         # shadcn primitives (auto-generated)
│   ├── shared/
│   │   ├── Badge.tsx               # persona + budget badge
│   │   ├── Navbar.tsx              # minimal top nav
│   │   └── PageWrapper.tsx         # consistent padding/max-width
│   ├── landing/
│   │   ├── PromptInput.tsx
│   │   ├── ExampleChips.tsx
│   │   └── HowItWorks.tsx
│   ├── generate/
│   │   ├── AgentPipeline.tsx       # 4-step progress indicator
│   │   ├── LiveLog.tsx             # SSE event renderer
│   │   └── PromptEcho.tsx          # carries prompt from landing
│   ├── itinerary/
│   │   ├── TripHeader.tsx          # title, badges, summary, tips
│   │   ├── DayNav.tsx              # sticky day navigation
│   │   ├── DaySection.tsx          # day wrapper (weather strip + blocks)
│   │   ├── TimeBlock.tsx           # morning/afternoon/evening card
│   │   ├── ActivityCard.tsx        # activity with "Why This?" collapsible
│   │   ├── WeatherStrip.tsx        # subtle inline weather
│   │   ├── ConflictBanner.tsx      # amber/rose inline warning
│   │   └── RegenerateControl.tsx   # regen trigger with constraint input
│   └── trips/
│       ├── TripCard.tsx
│       └── EmptyState.tsx
│
├── lib/
│   ├── api.ts                      # typed fetch wrappers for all endpoints
│   ├── sse.ts                      # SSE connection manager (EventSource)
│   ├── supabase.ts                 # Supabase client (browser)
│   └── types.ts                    # mirrors backend Pydantic schemas exactly
│
├── hooks/
│   ├── useSSEStream.ts             # manages EventSource lifecycle
│   ├── useTrip.ts                  # fetches GET /trips/:id
│   └── useAuth.ts                  # Supabase session wrapper
│
└── middleware.ts                   # route protection (Supabase session check)
```

---

### Page-by-Page Breakdown

**Page 1 — Landing (`/`)**
- Centered layout, max-w-2xl, huge vertical whitespace
- `PromptInput` — large textarea (not `<input>`), borderless inside a white card, placeholder: *"Describe your trip in plain English..."*
- On submit: `POST /api/v1/trips` → get `trip_id` → redirect to `/generate/[tripId]`
- `ExampleChips` — horizontal scroll on mobile, wrapping row on desktop. Each chip pre-fills the textarea on click
- `HowItWorks` — 3 items, text only, numbered, understated. No icons, no cards

**Page 2 — Live Generation (`/generate/[tripId]`)**
- `PromptEcho` — carries prompt in a subtle blockquote-style card at top
- `AgentPipeline` — 4 nodes: Researcher → Planner → Synthesizer → Critic. Active one gets sage accent dot. Completed ones get a checkmark. Inactive ones are muted grey
- SSE connection via `useSSEStream` hook hitting `GET /api/v1/trips/{tripId}/stream`
- `LiveLog` — renders each SSE event as a new line, staggered with 80ms CSS transition. Event type maps to log prefix: `tool_call` → 🔍, `agent_progress` → ◆, `conflict_detected` → ⚠, `trip_complete` → ✓
- On `trip_complete` event: auto-redirect to `/trips/[tripId]`
- On `error` event: show inline error with retry button if `recoverable: true`

**Page 3 — Itinerary (`/trips/[tripId]`)**

This is the most complex page. Structure:

```
TripHeader
  └── title, destination, dates, total_days
  └── Budget badge + Persona badge
  └── summary (2-3 sentences)
  └── Tips (collapsed accordion, 3-5 items)

DayNav (sticky)
  └── Desktop: left sidebar, scrolls with page, highlights active day
  └── Mobile: horizontal tabs, sticky top

[For each day:]
DaySection
  └── Day number + date + creative title
  └── WeatherStrip (icon + temp + condition, one line)
  └── day_summary (one sentence, muted)
  └── [Morning | Afternoon | Evening] TimeBlock
        └── Label + time range
        └── block_summary
        └── [For each activity:]
              ActivityCard
                └── category icon + name + location + duration + cost
                └── description
                └── "Why This?" collapsible (reasoning field from schema)
                └── ConflictBanner (if this block has conflicts)
        └── RegenerateControl (scope: block, pre-filled day + block)

[Bottom of each day:]
  └── RegenerateControl (scope: day)

[Page bottom:]
  └── RegenerateControl (scope: full_trip)
```

RegenerateControl posts to `POST /api/v1/trips/{tripId}/regenerate` with `{scope, day_number, block, constraint}` then redirects back to `/generate/[tripId]` to re-stream.

**Page 4 — My Trips (`/trips`)**
- Fetches `GET /api/v1/trips`
- Grid: 1 col mobile, 2 col tablet, 3 col desktop
- `TripCard`: destination + title (prominent), date range, persona badge, budget badge, status dot (generating = pulsing sage, completed = static, failed = rose)
- Hover on desktop: card lifts slightly (`hover:shadow-md transition-shadow`), reveals Open + Delete quick actions
- Top: "Plan a new trip" CTA button (sage, restrained size)
- `EmptyState`: centered, one line of text, one button — nothing more

**Page 5 — Auth (`/auth`)**
- Single centered white card, max-w-sm
- Toggle between Login / Sign Up via state (no page change)
- Fields: email + password, submit button
- If coming from guest trip: nudge text "Sign up to save your [destination] trip"
- On success: Supabase sets session → redirect to `/trips`
- `middleware.ts` guards `/trips` and `/trips/[tripId]` — redirects to `/auth` if no session. Generation page stays unguarded (guest mode supported per backend)

---

### API Layer (`lib/api.ts`)

Mirror every backend endpoint with a typed function:

```ts
// Key ones:
createTrip(prompt: string): Promise<TripResponse>
getTrip(tripId: string): Promise<TripDetail>
listTrips(): Promise<TripListItem[]>
deleteTrip(tripId: string): Promise<void>
regenerateTrip(tripId: string, req: RegenerateRequest): Promise<TripResponse>
```

Auth header injected from Supabase session on every call. Guest calls go without auth header — backend handles `user_id = null`.

---

### SSE Hook (`hooks/useSSEStream.ts`)

```ts
// Manages EventSource lifecycle
// Returns: { events, status, activeAgent, isComplete, error }
// Handles: reconnect on drop, cleanup on unmount, parsing all 8 event types
```

`LiveLog` and `AgentPipeline` both consume this hook. No prop drilling — use context if needed.

---

### Build Order (phase-matched to backend)

| Phase | Frontend work |
|---|---|
| 1 | Design system setup, globals.css, shared components, Navbar |
| 2 | Landing page — PromptInput, chips, HowItWorks |
| 3 | Auth page + Supabase client + middleware |
| 4 | My Trips page + TripCard + EmptyState |
| 5 | Generation page — AgentPipeline + LiveLog (mock SSE data first) |
| 6 | SSE hook wired to real backend stream |
| 7 | Itinerary page — full structure, static data first |
| 8 | RegenerateControl wired to real endpoint |
| 9 | Conflict rendering (ConflictBanner + styling) |
| 10 | Polish — transitions, mobile QA, empty/error states |

---

That's the complete plan. When you're ready to start building, say which phase or which component you want to tackle first and I'll generate the full code.