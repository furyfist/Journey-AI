-- Run this in the Supabase SQL editor (Dashboard → SQL Editor → New query)

CREATE TABLE IF NOT EXISTS trips (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES auth.users(id) ON DELETE CASCADE,  -- nullable for guest mode
    prompt          TEXT NOT NULL,
    destination     TEXT NOT NULL,
    budget          TEXT,                                               -- "budget" | "mid-range" | "luxury"
    travel_dates    JSONB,                                             -- {"start": "2026-07-01", "end": "2026-07-05"}
    total_days      INTEGER NOT NULL,
    title           TEXT NOT NULL,
    summary         TEXT,
    persona         TEXT,                                               -- detected travel persona (Session 3)
    status          TEXT NOT NULL DEFAULT 'pending',                    -- pending | generating | completed | failed
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_trips_user_id ON trips(user_id);
CREATE INDEX IF NOT EXISTS idx_trips_status  ON trips(status);

-- Auto-update updated_at on any row change
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trips_updated_at
    BEFORE UPDATE ON trips
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
