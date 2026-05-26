# Plan: Remove Supabase Authentication

**Goal:** Strip all Supabase auth from the project so the app works without login. The backend is already fully unauthenticated; all changes are in the frontend.

---

## Current Auth Surface (what exists today)

| Layer | File | Role |
|---|---|---|
| Frontend | `frontend/lib/supabase/client.ts` | Creates browser-side Supabase client |
| Frontend | `frontend/lib/supabase/server.ts` | Creates server-side Supabase client with cookie rotation |
| Frontend | `frontend/middleware.ts` | Redirects `/trips/*` to `/auth` if no session |
| Frontend | `frontend/app/auth/page.tsx` | Login / sign-up page |
| Frontend | `frontend/app/(protected)/layout.tsx` | Server-side guard — redirects to `/auth` if no session |
| Frontend | `frontend/hooks/useAuth.ts` | Client hook: `getSession` + `onAuthStateChange` |
| Frontend | `frontend/providers/index.tsx` | `AuthContext` provider wrapping the whole app |
| Frontend | `frontend/lib/api/client.ts` | Injects `Authorization: Bearer {token}` on every API call |
| Frontend | `frontend/components/shared/Navbar.tsx` | "Sign in" link pointing to `/auth` |
| Frontend | `frontend/.env.local` | `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` |
| Frontend | `frontend/package.json` | `@supabase/supabase-js`, `@supabase/ssr` packages |
| Backend | `app/trips/repository.py` | Unused `user_id` param — was a placeholder for future auth scoping |
| Backend | `pyproject.toml` | `supabase>=2.5.0` (still needed — used as the **database** client) |

**Note:** The backend never validated tokens. `supabase` in the backend is the **database driver**, not auth — do not remove it.

---

## Step-by-Step Removal

### Step 1 — Delete the auth page

**File to delete:** `frontend/app/auth/page.tsx`

This is the `/auth` route with sign-in and sign-up forms. It becomes unreachable after removing the redirects, so delete it entirely.

---

### Step 2 — Delete the middleware

**File to delete:** `frontend/middleware.ts`

The entire file is auth-only. It redirects unauthenticated users from `/trips/*` to `/auth`. Delete it; Next.js will simply not run any middleware.

---

### Step 3 — Remove the protected layout redirect

**File:** `frontend/app/(protected)/layout.tsx`

Remove the session check and redirect. The layout can stay (it may wrap UI chrome), but the auth guard block must go.

**Before (roughly):**
```ts
const { data: { session } } = await supabase.auth.getSession();
if (!session) redirect('/auth');
```

**After:** Delete those lines. Keep any remaining layout markup.

If the file becomes a passthrough with no meaningful content, delete it entirely and let the route group use the root layout.

---

### Step 4 — Delete the Supabase client helpers

**Files to delete:**
- `frontend/lib/supabase/client.ts`
- `frontend/lib/supabase/server.ts`

Nothing should import these after completing the other steps. Delete the `frontend/lib/supabase/` directory.

---

### Step 5 — Delete the useAuth hook

**File to delete:** `frontend/hooks/useAuth.ts`

It does nothing useful without Supabase. Delete it.

---

### Step 6 — Gut the AuthContext provider

**File:** `frontend/providers/index.tsx`

The `AuthContext` and `useAuthContext()` hook can be deleted. If the `Providers` component wraps other providers (e.g., React Query, Toaster), keep the shell but remove all auth-related code.

**Remove:**
- Import of `supabase` / `createBrowserClient`
- `AuthContext` creation and `createContext` call
- The `useAuthContext` export
- The `user`, `session`, `loading` state variables
- `useEffect` that calls `getSession` / `onAuthStateChange`

**Keep:** Any non-auth providers still in the file.

---

### Step 7 — Strip the auth header from the API client

**File:** `frontend/lib/api/client.ts`

Remove the session fetch and Bearer token injection.

**Remove these lines (approximately):**
```ts
const { data: { session } } = await supabase.auth.getSession();
headers['Authorization'] = `Bearer ${session?.access_token}`;
```

**After:** `apiFetch` becomes a plain fetch wrapper with no auth header. API calls still work because the backend doesn't validate tokens.

---

### Step 8 — Update the Navbar

**File:** `frontend/components/shared/Navbar.tsx`

Remove the "Sign in" link that points to `/auth`. Replace it with nothing, or with a neutral link, depending on the desired UI.

---

### Step 9 — Uninstall Supabase frontend packages

In `frontend/package.json`, remove:
- `@supabase/supabase-js`
- `@supabase/ssr`

Run:
```bash
cd frontend
npm uninstall @supabase/supabase-js @supabase/ssr
```

---

### Step 10 — Clean up environment variables

**File:** `frontend/.env.local`

Remove (or leave blank — they just become unused):
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

Also update `frontend/.env.local.example` to remove those two lines so future devs aren't confused.

---

### Step 11 — Clean up unused `user_id` in the backend

**File:** `app/trips/repository.py`

The `user_id` parameter in `fetch_trips()` was a placeholder for future auth scoping that was never wired up. It's safe to remove:

```python
# Before
async def fetch_trips(db: AsyncClient, user_id: str | None = None) -> list[dict]:
    query = db.table("trips").select(...)
    if user_id:
        query = query.eq("user_id", user_id)

# After
async def fetch_trips(db: AsyncClient) -> list[dict]:
    query = db.table("trips").select(...)
```

Also remove `user_id` from `app/trips/service.py` if it is passed through there.

---

### Step 12 — Delete the `(protected)` route group if empty

After step 3, check if `frontend/app/(protected)/` still holds routes beyond the layout. If `trips/` lives there, you have two options:

- **Option A (simpler):** Leave the folder structure. Next.js ignores the parenthesized group name for routing; `/trips` still resolves correctly.
- **Option B (clean):** Move `frontend/app/(protected)/trips/` to `frontend/app/trips/` and delete the now-empty `(protected)` folder.

Option A requires zero extra work; Option B is cleaner long-term.

---

## Verification Checklist

After completing all steps, confirm:

- [ ] `npm run build` in `frontend/` completes with no TypeScript errors
- [ ] Visiting `/trips` does **not** redirect to `/auth`
- [ ] Visiting `/auth` returns a 404
- [ ] Creating and listing trips works without being logged in
- [ ] No `@supabase` imports remain in the frontend (`grep -r "@supabase" frontend/`)
- [ ] No references to `supabase.auth` remain in the frontend
- [ ] The backend starts and all API routes respond normally
- [ ] `NEXT_PUBLIC_SUPABASE_URL` is no longer referenced anywhere in the frontend

---

## What Stays Unchanged

| Item | Reason |
|---|---|
| Backend `supabase` package | Still used as the database client (not for auth) |
| Backend `.env` `SUPABASE_URL` + `SUPABASE_SERVICE_KEY` | Still needed for database access |
| Supabase database tables | No schema changes needed |
| All trip API routes | Already unauthenticated |

---

## Estimated Effort

| Step | Effort |
|---|---|
| Steps 1–2 (delete files) | 2 min |
| Step 3 (protected layout) | 5 min |
| Steps 4–5 (delete lib/hooks) | 2 min |
| Step 6 (providers cleanup) | 10 min |
| Step 7 (api client) | 5 min |
| Step 8 (Navbar) | 3 min |
| Steps 9–10 (deps + env) | 3 min |
| Step 11 (backend cleanup) | 5 min |
| Step 12 (route group) | 5 min (optional) |
| **Total** | **~40 min** |
