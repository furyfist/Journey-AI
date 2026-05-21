-- Run AFTER 001_create_trips.sql

CREATE TABLE IF NOT EXISTS agent_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id         UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    agent_name      TEXT NOT NULL,                                     -- researcher | planner | synthesizer | critic
    step            TEXT NOT NULL,                                     -- short label for what this entry records
    input_data      JSONB,
    output_data     JSONB,
    tool_calls      JSONB DEFAULT '[]'::jsonb,
    duration_ms     INTEGER,
    model_used      TEXT,
    tokens_used     JSONB,                                             -- {"prompt": N, "completion": M}
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_logs_trip_id ON agent_logs(trip_id);
