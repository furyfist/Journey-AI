-- Run after duplicate historical itinerary versions have been cleaned up.
-- Prevent multiple rows from sharing the same (trip_id, version) pair.

CREATE UNIQUE INDEX IF NOT EXISTS idx_itineraries_trip_version
    ON itineraries(trip_id, version);
