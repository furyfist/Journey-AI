-- Add structured input fields to trips table
ALTER TABLE trips
  ADD COLUMN IF NOT EXISTS persona_hint  TEXT,
  ADD COLUMN IF NOT EXISTS interests     TEXT[]  NOT NULL DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS constraints   TEXT[]  NOT NULL DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS travel_party  TEXT;
