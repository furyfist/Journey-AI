-- Run AFTER 001_create_trips.sql

CREATE TABLE IF NOT EXISTS itineraries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id         UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL DEFAULT 1,                        -- increments on each regeneration
    itinerary_data  JSONB NOT NULL,                                    -- full ItinerarySchema JSON
    weather_data    JSONB,                                             -- cached weather per day
    places_data     JSONB,                                             -- cached places returned by Overpass
    conflicts       JSONB DEFAULT '[]'::jsonb,                         -- list[Conflict] from critic agent
    reasoning       JSONB DEFAULT '{}'::jsonb,                         -- {activity_name: reasoning_text}
    is_active       BOOLEAN NOT NULL DEFAULT true,                     -- only one active itinerary per trip
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enforce single active itinerary per trip
CREATE UNIQUE INDEX IF NOT EXISTS idx_itinerary_active
    ON itineraries(trip_id) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_itineraries_trip_id ON itineraries(trip_id);
