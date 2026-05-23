import type { SSEEventType } from "./types/planning";

export const SSE_EVENTS: Record<SSEEventType, SSEEventType> = {
  agent_start: "agent_start",
  agent_complete: "agent_complete",
  tool_call: "tool_call",
  tool_result: "tool_result",
  thinking: "thinking",
  conflict_detected: "conflict_detected",
  trip_complete: "trip_complete",
  error: "error",
  keepalive: "keepalive",
};

export const AGENT_ORDER = [
  "researcher",
  "synthesizer",
  "conflict_checker",
  "critic",
] as const;

export type AgentName = (typeof AGENT_ORDER)[number];
