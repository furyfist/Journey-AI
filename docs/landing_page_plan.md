# Journey AI — Landing Page Build Plan

> Reference design: `frontend/public/designs/landing_page.png`
> Key decision: the prompt input IS the hero (right column of hero section), not a below-fold element.
> Images are placeholders throughout — swap in real assets later without touching layout.

---

## Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Hero right column | `PromptInput` card, not a live trip card | Removes API dependency; immediate product value for resume reviewers |
| Nav buttons (Sign In / Get Started) | Scroll to `#prompt` | Auth was removed; no dead links |
| Watch Demo button | Opens `VideoModal` placeholder | Keeps the button, defers real content |
| Testimonials + destinations | Fully hardcoded | Marketing copy, no data dependency |
| Blue accent in design vs. existing sage green | Add `--color-brand-blue` token | Landing-only token; existing app palette untouched |
| Images | `bg-muted rounded-xl` placeholder divs | Exact aspect ratios preserved for easy swap |

---

## Step 1 — Design Token Alignment (`globals.css`)

**Files:** `frontend/app/globals.css`

- Add `--color-brand-blue: #3B82F6` and `--color-brand-blue-dark: #2563EB` to `:root`
- Add `--color-brand-blue` mapping under `@theme inline`
- Add a `bg-gradient-brand` custom class for the CTA banner (blue → slightly darker blue, left-to-right)
- Existing tokens untouched — this is purely additive

---

## Step 2 — Navbar Update

**Files:** `frontend/components/shared/Navbar.tsx`

- Add three anchor nav links: **Features** (`#features`), **How It Works** (`#how-it-works`), **Explore** (`#explore`) — centered in the nav bar
- Add **Sign In** button (ghost/outline style, scrolls to `#prompt`)
- Add **Get Started** button (filled, brand-blue background, scrolls to `#prompt`)
- Keep existing border + surface background; extend the flex row
- On mobile: collapse nav links, keep both buttons

---

## Step 3 — Hero Section (Core Change)

**Files:** `frontend/components/landing/HeroSection.tsx` *(new)*

Two-column layout, `min-h-[85vh]`, vertically centered:

**Left column:**
- Eyebrow pill: "Powered by AI" — small badge, brand-blue border + text, rounded-full
- H1: "Your AI Travel **Companion**" — last word wrapped in `<span className="text-brand-blue">`
- Subtitle paragraph in `text-text-secondary`
- Two CTA buttons side by side:
  - **Start Planning** → filled brand-blue, scrolls to `#prompt`
  - **Watch Demo** → ghost outline, opens `VideoModal`
- Star rating row: 3 avatar placeholder circles (overlapping, initials) + "★★★★★ Trusted by travelers"

**Right column:**
- Floating card: `bg-surface shadow-xl rounded-2xl p-6 border border-border`
- Card label at top: "Where do you want to go?" in `text-text-muted text-sm`
- Existing `PromptInput` component rendered inside
- Existing `ExampleChips` component rendered below input
- Card gets `id="prompt"` — this is the scroll target for all CTAs
- Subtle light-blue tinted background behind card (`bg-blue-50/30`) to give depth

On mobile: single column, left content stacks above card.

---

## Step 4 — How Journey AI Works (Redesign)

**Files:** `frontend/components/landing/HowItWorks.tsx` *(rewrite)*

Change from vertical numbered list → **3-column icon grid**:

| Step | Icon (lucide) | Title | Description |
|---|---|---|---|
| 1 | `MapPin` | Tell your destination | Where you want to go, how long, what matters |
| 2 | `Sparkles` | AI builds your itinerary | Multiple agents research, plan days, check conflicts |
| 3 | `PlaneTakeoff` | Travel stress-free | Refine any day or block, regenerate just that part |

- Section has `id="how-it-works"`
- Centered eyebrow label + H2 "How Journey AI Works" above the grid
- Each tile: icon in a rounded-square `bg-accent-light` container, bold title, description below
- `grid-cols-1 md:grid-cols-3 gap-8`
- Section background: `bg-muted/40` to visually separate from hero

---

## Step 5 — Built Around You

**Files:** `frontend/components/landing/FeaturesGrid.tsx` *(new)*

6-tile grid, `id="features"`:

| Icon (lucide) | Title | Description |
|---|---|---|
| `Globe` | International Wanderer | Multi-country routes, visa tips, timezone handling |
| `Wallet` | Budget Planner | Set a budget, AI picks stays and activities that fit |
| `Users` | Family Trips | Age-appropriate activities, stroller-friendly routes |
| `User` | Solo Explorer | Safe neighborhoods, solo-friendly experiences |
| `UtensilsCrossed` | Foodie Traveler | Restaurants, markets, and food tours woven into your days |
| `Landmark` | Cultural Explorer | Museums, heritage sites, and local festivals |

- `grid-cols-2 md:grid-cols-3 gap-4`
- Each card: `bg-surface border border-border rounded-xl p-5`, icon + title + description
- Hover: `hover:shadow-md hover:border-brand-blue/30 transition-all`
- Section: centered H2 "Built Around You" + subtitle, then grid

---

## Step 6 — Destinations Showcase

**Files:** `frontend/components/landing/DestinationsShowcase.tsx` *(new)*

`id="explore"`, section heading: "See What a Real Trip Looks Like"

**Two city panels side by side** (`grid-cols-1 md:grid-cols-2 gap-6`), hardcoded:

**Panel — Tokyo, Japan:**
- City + weather header: "Tokyo, Japan" + ☀️ 22°C
- 3 activity rows: time badge (`9:00 AM`) + activity name + category tag
  - 9:00 AM · Tsukiji Outer Market · Food
  - 11:30 AM · teamLab Borderless · Art
  - 2:00 PM · Senso-ji Temple · Culture

**Panel — Shibuya & Harajuku:**
- City + weather header: "Shibuya & Harajuku" + 🌤 20°C
- 3 activity rows:
  - 10:00 AM · Shibuya Crossing · Landmark
  - 12:30 PM · Takeshita Street · Shopping
  - 3:00 PM · Yoyogi Park · Outdoors

**Below panels — Map placeholder:**
- Full-width `rounded-2xl bg-muted aspect-[16/5]` div
- Centered content: lucide `Map` icon + "Interactive map — coming soon" in `text-text-muted`
- This div is exactly where a real map image drops in

---

## Step 7 — Testimonials

**Files:** `frontend/components/landing/Testimonials.tsx` *(new)*

- Centered heading: "Loved by Travelers Worldwide"
- Aggregate star row: ★★★★★ with "4.9/5 from 200+ trips planned"
- `grid-cols-1 md:grid-cols-3 gap-6`

Hardcoded cards:

| Avatar | Name | Location | Quote |
|---|---|---|---|
| S (indigo) | Sarah M. | New York, USA | "Planned my entire Japan trip in 3 minutes. The day-by-day breakdown was better than anything I'd have made myself." |
| J (emerald) | James K. | London, UK | "The budget planner mode is insane. It found ryokans I never would have discovered on my own." |
| P (amber) | Priya R. | Sydney, AU | "Used it for a 10-day Southeast Asia trip. Zero conflicts, perfect pacing. I was genuinely impressed." |

Each card: `bg-surface border border-border rounded-xl p-6`, avatar (initials circle, colored bg), name + location, 5 stars, quote in `text-text-secondary italic`.

---

## Step 8 — CTA Banner

**Files:** `frontend/components/landing/CTABanner.tsx` *(new)*

- `rounded-3xl mx-4 sm:mx-6` so it floats slightly from the page edges
- `bg-gradient-brand` (blue gradient left → right)
- Two-column layout:
  - Left: H2 "Start your next journey with AI" (white), subtitle (white/80), button "Plan My Trip →" (white bg, brand-blue text) → scrolls to `#prompt`
  - Right: lucide `PlaneTakeoff` at `size={120}` in white/20 opacity, rotated slightly — placeholder for the plane illustration
- Section `py-24` spacing

---

## Step 9 — Footer

**Files:** `frontend/components/shared/Footer.tsx` *(new)*

Structure:
```
[Logo + tagline]    [Product]    [Company]    [Resources]    [Legal]

────────────────────────────────────────────────────────────────────
© 2025 Journey AI. All rights reserved.         [𝕏] [IG] [GH]
```

- Logo: same `<Link href="/">Journey AI</Link>` as Navbar
- Tagline: "AI-powered travel, built for curious minds"
- Link columns (all `href="#"` placeholders):
  - **Product**: Features, How It Works, Pricing, Changelog
  - **Company**: About, Blog, Careers, Press
  - **Resources**: Docs, API, Status, Community
  - **Legal**: Privacy, Terms, Cookies
- Social icons: lucide `Twitter`, `Instagram`, `Github` — 24px, `text-text-muted hover:text-text-primary`
- `border-t border-border` separator above copyright row

---

## Step 10 — Page Assembly + Polish

**Files:** `frontend/app/(public)/page.tsx`, `frontend/components/shared/VideoModal.tsx` *(new)*

**`page.tsx` section order:**
```tsx
<Navbar />
<HeroSection />           {/* contains PromptInput, id="prompt" */}
<HowItWorks />            {/* id="how-it-works" */}
<FeaturesGrid />          {/* id="features" */}
<DestinationsShowcase />  {/* id="explore" */}
<Testimonials />
<CTABanner />
<Footer />
```

**`VideoModal.tsx`:**
- Triggered by "Watch Demo" in hero via `useState` lifted to `HeroSection`
- Overlay: `fixed inset-0 bg-black/50 z-50 flex items-center justify-center`
- Modal card: `bg-surface rounded-2xl p-8 max-w-lg w-full text-center`
- Content: lucide `PlayCircle` icon at 48px, "Demo coming soon", "Check back after launch", close button
- Close on backdrop click or Escape key

**Polish checklist:**
- `scroll-smooth` on `<html>` in `layout.tsx`
- All sections use `py-20 sm:py-24` consistently
- All sections use `PageWrapper` for max-width
- Mobile: hero single-column, grids stack, CTA banner text wraps cleanly
- Verify `PromptInput` submit still routes to `/generate/[tripId]` correctly from within the hero card

---

## Files Summary

| File | Status |
|---|---|
| `frontend/app/globals.css` | Update — add blue token + gradient |
| `frontend/app/(public)/page.tsx` | Rewrite — compose all sections |
| `frontend/app/layout.tsx` | Update — add `scroll-smooth` |
| `frontend/components/shared/Navbar.tsx` | Update — nav links + CTA buttons |
| `frontend/components/shared/Footer.tsx` | New |
| `frontend/components/shared/VideoModal.tsx` | New |
| `frontend/components/landing/HeroSection.tsx` | New |
| `frontend/components/landing/HowItWorks.tsx` | Rewrite |
| `frontend/components/landing/FeaturesGrid.tsx` | New |
| `frontend/components/landing/DestinationsShowcase.tsx` | New |
| `frontend/components/landing/Testimonials.tsx` | New |
| `frontend/components/landing/CTABanner.tsx` | New |

## Placeholder → Real Asset Map

| Placeholder | Location | Real asset |
|---|---|---|
| `bg-muted aspect-[16/5]` div | Destinations map | Map screenshot or Mapbox embed |
| `bg-muted aspect-video` divs | Destination thumbnails (if added) | City photos |
| Initials circles | Testimonial avatars | Profile photos |
| lucide `PlaneTakeoff` 120px | CTA banner right | Plane illustration SVG |
| `href="#"` links | Nav + Footer | Real routes |
