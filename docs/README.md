# Docs Guide

This folder is organized so it is easier to tell what is current, what was implemented, and what is only historical planning.

## Start Here

- Current source of truth: [overview/PROJECT_OVERVIEW.md](overview/PROJECT_OVERVIEW.md)
- Active planning work: [plans/active](plans/active)
- Implemented change notes: [implementation](implementation)
- Historical or superseded plans: [plans/archive](plans/archive)

## Folder Layout

### `overview/`

High-signal reference docs that describe the current project state.

- `PROJECT_OVERVIEW.md`: best single-file project snapshot

### `plans/active/`

Plans that still represent work we may want to execute next.

- `remove_auth_plan.md`: current active plan for auth removal

### `implementation/`

Docs that describe a focused implementation that has already been carried out or mostly completed.

- `implemented_structured_input_pipeline.md`: structured input and pipeline optimization plan that now matches the shipped implementation
- `landing_page_plan.md`: landing page build plan tied closely to implemented frontend work

### `plans/archive/`

Older roadmap or planning docs kept for history and context, but no longer treated as the current plan.

- `backend_build_plan.md`
- `session_plan.md`
- `frontend_master_plan.md`
- `frontend_phase_breakdown.md`

## Status Labels

When adding new docs, try to place them using this rule:

- `overview`: current truth
- `plans/active`: next work
- `implementation`: implemented or nearly implemented change records
- `plans/archive`: superseded planning history

## Suggested Workflow

1. Update `overview/PROJECT_OVERVIEW.md` whenever the real project state changes materially.
2. Keep only a small number of files in `plans/active`.
3. Move completed plans into `implementation` if they document what shipped.
4. Move superseded planning docs into `plans/archive` instead of deleting them.
