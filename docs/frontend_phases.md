## Journey AI — Frontend: Phase-by-Phase Work Breakdown

Each phase has a single, shippable goal. Complete one fully before starting the next.
Sub-tasks are ordered — earlier ones unblock later ones within the same phase.


─────────────────────────────────────────────────────────────
Commit instructions — IMPORTANT
─────────────────────────────────────────────────────────────

After each phase commit using ONLY this format — no Co-Authored-By line, no
mention of Claude or AI:

  git commit -m "$(cat <<'EOF'
  <message from phase above>
  EOF
  )"

Do NOT append "Co-Authored-By: Claude" or any AI attribution. The commit should
look exactly as if it was written by the repo owner.

---

## Phase 1 — Scaffold + Design System

**Goal:** Empty repo → working Next.js app, all design tokens in place, three shared components built.

### Sub-tasks

1. `cd frontend && npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"`
2. Run `npx shadcn@latest init` — choose style: default, base colour: neutral, CSS variables: yes. This generates `components.json` and updates `tailwind.config.ts`.
3. Install initial shadcn primitives needed across all phases:
   `npx shadcn@latest add accordion button badge separator skeleton`
4. Write all CSS variables into `app/globals.css` under `:root`:
   `--background`, `--surface`, `--border`, `--accent`, `--accent-light`, `--text-primary`, `--text-secondary`, `--text-muted`, `--warning`, `--danger` — values from the design system in `fronend_plan.md`
5. Update `tailwind.config.ts` so colour utilities map to these CSS variables via `hsl()` wrappers so Tailwind classes like `bg-accent` and `text-muted` work throughout.
6. Load `Instrument Sans` in `app/layout.tsx` via `next/font/google`; apply font variable to `<html>` className.
7. Create `providers/index.tsx` — a passthrough shell for now: `export default function Providers({ children }) { return <>{children}</> }`. Auth context wired in Phase 3.
8. Import `Providers` in `app/layout.tsx` and wrap `{children}` with it.
9. Build `components/shared/PageWrapper.tsx` — a `<div>` with `max-w-screen-xl mx-auto px-4 sm:px-6`. All pages use this.
10. Build `components/shared/Navbar.tsx` — logo/wordmark left, auth link right. No interactivity yet — static links.
11. Build `components/shared/Badge.tsx` — two variants via a `variant` prop:
    - `persona` → background `var(--accent-light)`, text `var(--accent)`
    - `budget` → background neutral-100, text `var(--text-secondary)`
12. Create the route group folders and empty stubs:
    - `app/(public)/page.tsx` — `export default function Home() { return null }`
    - `app/(public)/generate/[tripId]/page.tsx` — stub
    - `app/(protected)/layout.tsx` — passthrough for now (auth guard added in Phase 3)
    - `app/(protected)/trips/page.tsx` — stub
    - `app/(protected)/trips/[tripId]/page.tsx` — stub
    - `app/auth/page.tsx` — stub
    - `app/error.tsx` — stub (full content in Phase 10)
    - `app/not-found.tsx` — stub
13. Create `.env.local.example`:
    ```
    NEXT_PUBLIC_SUPABASE_URL=
    NEXT_PUBLIC_SUPABASE_ANON_KEY=
    NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
    ```
14. Copy `.env.local.example` → `.env.local` and fill values.
15. Run `npm run dev` — verify `localhost:3000` loads, Navbar renders, no TS errors.

**Done when:** `npm run dev` is clean, Navbar shows on `/`, all CSS variables render correctly in browser DevTools, `Badge` renders both variants without errors.

---

## Phase 2 — Landing Page

**Goal:** User can type a prompt, submit it to the backend, and get redirected to `/generate/[tripId]`.

### Sub-tasks

1. Create `lib/types/trip.ts` — TypeScript interfaces mirroring the backend schemas:
   ```ts
   TripCreate        // { prompt: string; destination?: string; budget?: string; ... }
   TripResponse      // { id: string; prompt: string; destination: string; title: string; status: string; ... }
   TripDetail        // extends TripResponse — adds itinerary, conflicts, reasoning, weather_data
   TripListItem      // { id, title, destination, total_days, status, created_at }
   ```
2. Create `lib/api/client.ts` — `apiFetch<T>(path, init?)`:
   - Prepends `NEXT_PUBLIC_API_BASE_URL`
   - No auth header yet (added in Phase 3)
   - On non-2xx: throws `{ status: number, message: string }` (define an `ApiError` class)
3. Create `lib/api/trips.ts` — add `createTrip(payload: TripCreate): Promise<TripResponse>` only. Other trip functions added in their respective phases.
4. Install Zustand: `npm install zustand`
5. Create `store/generate.ts`:
   ```ts
   // { prompt: string; setPrompt: (p: string) => void }
   // Used to carry the prompt text from the landing page across the route change to /generate/[tripId].
   ```
6. Build `components/landing/PromptInput.tsx`:
   - Controlled `<textarea>` (not `<input>`) — `font-size: 16px` to prevent iOS zoom
   - Borderless inside a white `shadow-sm` card
   - Character counter (max 2000 per backend schema)
   - Submit button disabled while `loading` is true; shows spinner on loading
   - `onSubmit(prompt: string)` callback prop
7. Build `components/landing/ExampleChips.tsx`:
   - 5 hardcoded example strings covering different trip styles
   - `onSelect(example: string)` callback prop — parent uses it to set textarea value
   - Wrapping row on desktop, `overflow-x-auto` scroll on mobile
8. Build `components/landing/HowItWorks.tsx`:
   - 3 numbered items, text only, no icons, no cards
   - Content: "Describe your trip", "AI builds your itinerary", "Refine and regenerate"
9. Build `app/(public)/page.tsx`:
   - Layout: `PageWrapper`, `Navbar`, centered `max-w-2xl` column
   - Generous `py` spacing between sections: title → `PromptInput` → `ExampleChips` → `HowItWorks`
   - Submit handler:
     1. Call `createTrip({ prompt })`
     2. Call `setPrompt(prompt)` on Zustand store
     3. `router.push("/generate/" + trip.id)`
   - Handle API error: show an inline error message below the textarea

**Done when:** Submitting a prompt calls `POST /api/v1/trips`, the Zustand store has the prompt, and the browser navigates to `/generate/[id]`.

---

## Phase 3 — Auth Page + Supabase + Middleware

**Goal:** Users can log in and sign up. Protected routes redirect to `/auth`. API calls include the session token.

### Sub-tasks

1. Install Supabase: `npm install @supabase/supabase-js @supabase/ssr`
2. Create `lib/supabase/client.ts`:
   ```ts
   // createBrowserClient from @supabase/ssr
   // Export a singleton: export const supabase = createBrowserClient(url, anon)
   // Used in all client components, hooks, and lib/api/client.ts
   ```
3. Create `lib/supabase/server.ts`:
   ```ts
   // createServerClient from @supabase/ssr — requires a cookies() adapter
   // Used only in middleware.ts and server components
   // Do NOT import this in client components — it will throw
   ```
4. Build `hooks/useAuth.ts`:
   - Subscribes to `supabase.auth.onAuthStateChange`
   - Returns `{ user, session, loading }`
   - Cleans up subscription on unmount
5. Build `app/auth/page.tsx`:
   - Centered white card, `max-w-sm`, `shadow-sm`
   - `useState<"login" | "signup">` — toggle link below the form, no route change
   - Fields: email + password
   - If `searchParams.next` is set, show nudge text: *"Sign in to save your trip"*
   - On success: `router.push(next ?? "/trips")`
   - On error: show Supabase error message inline below the button
6. Write `middleware.ts`:
   - Use server Supabase client to read the session from cookies
   - If path matches `/(protected)/**` and no session: `redirect("/auth?next=" + pathname)`
   - Also refresh the session token on every request (required by `@supabase/ssr` for cookie rotation)
7. Update `app/(protected)/layout.tsx`:
   - Server-side session check as a second defence: if no session, `redirect("/auth")`
   - This covers edge cases where middleware runs before the cookie is set
8. Update `lib/api/client.ts`:
   - Import `supabase` browser client
   - Before every request: call `supabase.auth.getSession()`
   - If `session?.access_token` exists: add `Authorization: Bearer <token>` header
   - Guest calls (no session) proceed with no auth header — backend handles `user_id = null`

**Done when:** Visiting `/trips` without a session redirects to `/auth`. Logging in redirects back. API calls from a logged-in user include the Bearer header (verify in Network tab).

---

## Phase 4 — My Trips Page

**Goal:** Logged-in users see their trips in a grid, can open or delete them, and see an empty state when they have none.

### Sub-tasks

1. Add to `lib/api/trips.ts`:
   - `listTrips(): Promise<TripListItem[]>`
   - `deleteTrip(id: string): Promise<void>`
2. Build `hooks/useTrips.ts`:
   - `useState<TripListItem[]>([])`, fetches on mount via `listTrips()`
   - Exposes: `trips`, `loading`, `error`, `deleteAndRefresh(id: string)`
   - `deleteAndRefresh` calls `deleteTrip` then removes the item from local state optimistically (no full refetch)
3. Build `components/trips/EmptyState.tsx`:
   - Centered container, one heading, one short sentence, one "Plan a trip" button that routes to `/`
   - Nothing else — no illustrations, no extra text
4. Build `components/trips/TripCard.tsx`:
   - Shows: `title` (prominent), `destination`, `total_days` formatted as "X days", `created_at` formatted as a short date
   - Status dot — coloured `<span>` with `aria-label`:
     - `generating` → pulsing sage (CSS `animate-pulse`)
     - `completed` → static sage
     - `failed` → rose
   - No persona/budget badges — `TripListItem` doesn't carry those fields yet
   - On desktop hover: `hover:shadow-md transition-shadow`, reveal "Open" link + "Delete" button
   - "Open" → links to `/trips/[id]`
   - "Delete" → calls `deleteAndRefresh(id)` from parent via prop
5. Build `app/(protected)/trips/page.tsx`:
   - Fetches via `useTrips`
   - Loading: render 6 `TripCard` skeleton placeholders (shadcn `Skeleton`)
   - Error: inline error message + retry button
   - Empty: render `EmptyState`
   - Populated: responsive grid (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`), "Plan a new trip" CTA link at top right

**Done when:** Trips page shows real data from the API, status dots are correct, deleting a card removes it immediately, empty state renders for a fresh account.

---

## Phase 5 — Generation Page (Mock SSE)

**Goal:** Generation page is fully built and animated, driven by a hardcoded fixture event array. No live backend connection yet.

### Sub-tasks

1. Create `lib/types/planning.ts` — full type definitions mirroring `app/planning/schemas.py`:
   ```ts
   SSEEventType  // union of all 9 event type strings
   SSEEvent      // { event, agent?, data?, message? }
   Activity      // { name, description, location, latitude?, longitude?, duration_minutes, cost_estimate?, category, reasoning }
   TimeBlock     // { label, start_time, end_time, activities, block_summary }
   DayPlan       // { day_number, date?, title, weather?, morning, afternoon, evening, day_summary }
   ItinerarySchema // { title, destination, total_days, budget_level, persona, summary, days, tips }
   Conflict      // { type, severity, day_number, description, activities }
   ```
2. Create `lib/sse.ts`:
   ```ts
   export const SSE_EVENTS = { agent_start: "agent_start", tool_call: "tool_call", ... } // all 9
   export const AGENT_ORDER = ["researcher", "planner", "synthesizer", "conflict_checker", "critic"]
   ```
3. Build `components/generate/PromptEcho.tsx`:
   - Reads `prompt` from Zustand `generate` store
   - If store is empty (direct page load after refresh), renders nothing
   - Renders as a subtle blockquote card: left border in `--border`, muted text
4. Build `components/generate/AgentPipeline.tsx`:
   - Props: `activeAgent: string | null`, `completedAgents: string[]`
   - Renders 5 nodes in `AGENT_ORDER` sequence, connected by a thin line
   - Active node: pulsing sage dot + agent name label
   - Completed node: static checkmark + agent name
   - Inactive node: grey dot + muted agent name
   - Special case: when `activeAgent === "critic"`, also render `conflict_checker` as completed (backend emits no `agent_complete` for it)
5. Create `fixtures/sseEvents.ts` — a hardcoded `SSEEvent[]` that simulates the full real pipeline sequence in order, including at least one `conflict_detected`, one `tool_call`/`tool_result` pair, and a final `trip_complete`. Covers all 9 event types.
6. Build `components/generate/LiveLog.tsx`:
   - Props: `events: SSEEvent[]`
   - Filters out `keepalive` before rendering
   - Maps event type to prefix and display string (full table from `fronend_plan.md`)
   - Each line: `opacity-0 translate-y-1` enters to `opacity-100 translate-y-0` with 80ms CSS transition
   - Stagger via `transition-delay` based on array index, capped at 400ms total
   - Scrolls to bottom as new events arrive (`useEffect` + `scrollIntoView`)
   - `error` event: renders message in `--danger` colour + a "Retry" button stub
7. Build `app/(public)/generate/[tripId]/page.tsx`:
   - Layout: `Navbar`, `PageWrapper`, `PromptEcho` at top, `AgentPipeline` below it, `LiveLog` below that
   - Drive `AgentPipeline` and `LiveLog` from the fixture array
   - Simulate playback: use `useEffect` to push fixture events into state one at a time on an interval (e.g. 300ms), so the animation plays out visually — this is dev-only and gets removed in Phase 6

**Done when:** Visiting `/generate/anything` plays through the full mock pipeline animation. All 5 nodes cycle through their states. LiveLog lines stagger in. No real network call is made.

---

## Phase 6 — Wire Real SSE

**Goal:** Generation page connects to the live backend stream. `trip_complete` auto-redirects to the itinerary.

### Sub-tasks

1. Build `hooks/useSSEStream.ts`:
   - Opens `new EventSource(${NEXT_PUBLIC_API_BASE_URL}/api/v1/trips/${tripId}/stream)`
   - On each message: `JSON.parse(event.data)` → typed `SSEEvent`
   - Manages state:
     - `events: SSEEvent[]` — append each (except `keepalive`)
     - `activeAgent: string | null` — set on `agent_start`, clear on `agent_complete`
     - `completedAgents: string[]` — push to on `agent_complete`
     - `status: "connecting" | "streaming" | "complete" | "error"`
     - `isComplete: boolean` — true on `trip_complete`
     - `completedTripId: string | null` — from `trip_complete` data (same ID, but confirms the event arrived)
     - `error: string | null` — from `error` event message field
   - Sets `status = "streaming"` on first non-keepalive event
   - Calls `eventSource.close()` in the cleanup return of `useEffect`
   - Does not auto-reconnect — surfaces error and lets user trigger retry
2. Replace the fixture playback in `app/(public)/generate/[tripId]/page.tsx` with `useSSEStream(tripId)`. Remove the `setInterval` simulation entirely.
3. Add a `useEffect` watching `isComplete`: when true, `router.push("/trips/" + tripId)` with a 500ms delay so the user sees the `trip_complete` log line before navigating.
4. Wire the retry button in `LiveLog` (or on the page): on click, `window.location.reload()` — this closes the old `EventSource` via unmount cleanup and opens a fresh one.
5. Add a connection status indicator (small text below `AgentPipeline`): "Connecting...", "Streaming", "Complete" — driven by `status` from the hook.
6. Verify the full round-trip manually: landing → generate (stream plays live) → itinerary.

**Done when:** The complete user journey works end-to-end against the real backend without any manual steps.

---

## Phase 7 — Itinerary Page (Static First)

**Goal:** Full itinerary page built and styled with a static fixture `TripDetail`. Sticky nav and all nested components working.

### Sub-tasks

1. Add `getTrip(id: string): Promise<TripDetail>` to `lib/api/trips.ts`.
2. Build `hooks/useTrip.ts`:
   - Fetches on mount via `getTrip(tripId)`
   - Casts `trip.itinerary` (arrives as raw dict) to `ItinerarySchema` after fetch
   - Exposes: `trip`, `itinerary`, `loading`, `error`
3. Create `fixtures/tripDetail.ts` — a complete static `TripDetail` object with 2+ days, all time blocks populated, at least one `Conflict` in the `conflicts` array.
4. Build `components/itinerary/WeatherStrip.tsx`:
   - Maps condition string to a text emoji (☀️ / 🌤 / 🌧 / ❄️ etc.)
   - Renders: `{emoji} {temp}°C · {condition}` — one line, `text-muted` size
5. Build `components/itinerary/ActivityCard.tsx`:
   - Maps `activity.category` to an icon/emoji: food → 🍽, attraction → 🏛, transport → 🚌, shopping → 🛍, nature → 🌿, culture → 🎭, nightlife → 🌙
   - Shows: icon + `name` (prominent), `location` (muted), `duration_minutes` formatted as "Xh Ym", `cost_estimate`
   - `description` below the header row
   - "Why This?" — shadcn `Accordion` item containing `activity.reasoning` text; collapsed by default
6. Build `components/itinerary/TimeBlock.tsx`:
   - Header: `label` capitalised + `start_time – end_time`
   - `block_summary` in muted text
   - List of `ActivityCard` children
7. Build `components/itinerary/DaySection.tsx`:
   - Top: day number chip + `date` (if present) + `title`
   - `WeatherStrip` on the next line
   - `day_summary` below that
   - Three `TimeBlock` components (morning / afternoon / evening)
   - Accepts a `sectionRef` prop — the page passes a `ref` here for `IntersectionObserver`
8. Build `components/itinerary/DayNav.tsx`:
   - Desktop (`hidden md:block`): sticky left sidebar, `top-24`, list of day labels; active day highlighted in `--accent`
   - Mobile (`md:hidden`): horizontal scroll tab bar, `position: sticky; top: 0`
   - Active day driven by `activeDayNumber: number` prop
   - Clicking a day calls `onDaySelect(dayNumber)` → parent scrolls to that section
9. Build `components/itinerary/TripHeader.tsx`:
   - Title (large), destination (muted), total_days
   - `Badge` for persona + Badge for budget_level
   - Summary paragraph
   - Tips: shadcn `Accordion` with each tip as an item, collapsed by default, labelled "Travel Tips (X)"
10. Build `app/(protected)/trips/[tripId]/page.tsx`:
    - Hold `TripDetail` in state — start with fixture, swap to `useTrip` at end of this sub-task
    - Hold `activeDayNumber` in state, update via `IntersectionObserver` watching each `DaySection` ref
    - Layout: `TripHeader` full-width, then a two-column grid on desktop: `DayNav` (narrow left) + days (wide right)
    - Wire `useTrip` — replace fixture with real data; handle `loading` (skeleton headers) and `error` states
    - If `trip.status !== "completed"`, show a "Trip is still generating..." message instead of the itinerary

**Done when:** Itinerary page renders a real completed trip from the API. Sticky nav tracks the active day. All time blocks and activity cards render. Tips accordion works.

---

## Phase 8 — Regeneration

**Goal:** All three `RegenerateControl` placements call the backend synchronously and update the itinerary in-place.

### Sub-tasks

1. Create `lib/types/regenerate.ts`:
   ```ts
   type RegenerateScope = "full_trip" | "day" | "single_block"
   interface RegenerateRequest {
     scope: RegenerateScope
     day_number?: number
     block_label?: "morning" | "afternoon" | "evening"  // NOT "block"
     constraint?: string
   }
   ```
2. Create `lib/api/regenerate.ts` — `regenerateTrip(tripId: string, req: RegenerateRequest): Promise<TripDetail>`
3. Build `hooks/useRegenerate.ts`:
   - Accepts `tripId: string` and `onSuccess: (updated: TripDetail) => void` 
   - Exposes: `regenerate(req: RegenerateRequest)`, `loading: boolean`, `error: string | null`
   - On success: calls `onSuccess(updated)`, clears error
   - On failure: sets error message, does not throw
4. Build `components/itinerary/RegenerateControl.tsx`:
   - Props: `tripId`, `scope`, `dayNumber?`, `blockLabel?`, `onSuccess`
   - Renders a small muted "Regenerate this [block/day/trip]" text button
   - On click: expands to show a constraint `<input>` (placeholder: *"Any changes? e.g. 'avoid museums'"*) + a "Go" button + a "Cancel" link
   - While loading: show a translucent overlay on the parent section; disable the button
   - On success: overlay disappears, parent state updates via `onSuccess`
   - On error: show inline error below the constraint input
5. Place `RegenerateControl` in the component tree:
   - Bottom of each `TimeBlock` — `scope="single_block"`, `dayNumber={day.day_number}`, `blockLabel={block.label}`
   - Bottom of each `DaySection` — `scope="day"`, `dayNumber={day.day_number}`
   - Bottom of the page (after last `DaySection`) — `scope="full_trip"`
6. In `app/(protected)/trips/[tripId]/page.tsx`:
   - Hold the full `TripDetail` in `useState`
   - Pass `onSuccess={(updated) => setTrip(updated)}` to every `RegenerateControl`
   - The whole page re-renders from the fresh `TripDetail` on success

**Done when:** Clicking any regenerate button calls `POST /api/v1/trips/{id}/regenerate`, shows a loading overlay on the affected section, and the itinerary updates without a page reload. All three scopes (`single_block`, `day`, `full_trip`) work correctly.

---

## Phase 9 — Conflict Banners

**Goal:** Conflicts from `TripDetail.conflicts` render as inline banners at the correct location in the itinerary.

### Sub-tasks

1. Build `components/itinerary/ConflictBanner.tsx`:
   - Props: `conflict: Conflict`
   - `severity === "warning"` → amber tint background, amber left border, `⚠` icon
   - `severity === "error"` → rose tint background, rose left border, `✕` icon
   - Shows: conflict `type` as a small uppercase label chip + `description` as body text
   - Add `role="alert"` for screen readers
2. Add conflict filtering logic in `DaySection.tsx`:
   - Accept `conflicts: Conflict[]` as a prop (passed from the page, already filtered to this day)
   - Render `ConflictBanner` for each conflict above the time blocks
3. In `app/(protected)/trips/[tripId]/page.tsx`:
   - For each day, filter `trip.conflicts` where `conflict.day_number === day.day_number`
   - Pass the filtered array to `DaySection`
4. Create a dev fixture override: temporarily inject 2-3 mock conflicts into the fixture `TripDetail` (one `warning`, one `error`, different days) to verify rendering. Remove the override after verification.
5. Verify the zero-conflict case: with no matching conflicts for a day, no banners render and no empty space appears.

**Done when:** Real conflicts from the API render in the correct day with the correct severity styling. No conflicts = no banners, no layout shift.

---

## Phase 10 — Polish

**Goal:** App is production-ready — responsive, accessible, all loading/error/empty states handled, build is clean.

### Sub-tasks

**Loading states**
1. Add skeleton loading to `app/(protected)/trips/page.tsx` — 6 `TripCard`-shaped `Skeleton` blocks while `useTrips` is loading.
2. Add skeleton loading to `app/(protected)/trips/[tripId]/page.tsx` — `TripHeader` skeleton (two lines + badge placeholders) and 3 `ActivityCard` skeletons per time block while `useTrip` is loading.
3. Verify `RegenerateControl` loading overlay covers only the affected section, not the full page.

**Error states**
4. `useTrip` error: show "Failed to load itinerary" message + "Try again" button that calls `refetch()`. Not just a console.error.
5. `useTrips` error: same pattern on the trips list page.
6. `createTrip` error on landing page: show message below the textarea, clear it on next submit attempt.

**Error boundary + 404**
7. Implement `app/error.tsx` — Next.js error boundary: "Something went wrong" heading, short message, "Back to home" link. Log `error.digest` to console.
8. Implement `app/not-found.tsx` — one sentence, "Go home" link, no decoration.

**Mobile QA checklist**
9. `PromptInput` textarea — confirm `font-size: 16px` on mobile (prevents iOS zoom on focus).
10. `ExampleChips` — confirm horizontal scroll works on narrow screens with no overflow leak.
11. `DayNav` — confirm it collapses to horizontal scroll tabs on mobile with no text truncation issues.
12. `ActivityCard` "Why This?" accordion — confirm it opens correctly on touch devices.
13. `RegenerateControl` constraint input — confirm it is usable on a small screen without layout break.
14. Navbar — confirm no overflow on narrow screens.

**Accessibility pass**
15. All buttons and links have visible focus rings (Tailwind `focus-visible:ring-2` utility).
16. Status dots on `TripCard` have `aria-label` (e.g. `aria-label="Status: generating"`).
17. `ConflictBanner` has `role="alert"` (already done in Phase 9 — verify it's present).
18. "Why This?" accordions are keyboard-navigable (shadcn Accordion handles this — verify with Tab + Enter).
19. Image-free build — no `alt` attributes missing (there are no images, but verify no `<img>` tags slipped in).

**Final checks**
20. Audit all files for hardcoded `localhost:8000` or `localhost:3000` — replace with env variable references.
21. Verify all keys in `.env.local.example` match what the code actually reads.
22. Run `npm run build` — zero TypeScript errors, zero ESLint errors.
23. Run `npm run build` output size check — confirm no unexpectedly large bundles (Zustand and shadcn should be minimal).

**Done when:** `npm run build` passes clean. All 5 pages work on a 375px mobile screen. No runtime console errors. Loading and error states are visible and functional for every data-fetching hook.
