import type { Activity, TimeBlock, DayPlan, ItinerarySchema, Conflict } from "./trip";

export type { Activity, TimeBlock, DayPlan, ItinerarySchema, Conflict };

export type SSEEventType =
  | "agent_start"
  | "agent_complete"
  | "tool_call"
  | "tool_result"
  | "thinking"
  | "conflict_detected"
  | "trip_complete"
  | "error"
  | "keepalive";

export interface SSEEvent {
  event: SSEEventType;
  agent?: string;
  data?: Record<string, unknown>;
  message?: string;
}
