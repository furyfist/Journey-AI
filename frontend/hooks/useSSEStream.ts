"use client";

import { useEffect, useRef, useState } from "react";
import type { SSEEvent, SSEEventType } from "@/lib/types/planning";

export type StreamStatus = "connecting" | "streaming" | "complete" | "error";

export interface UseSSEStreamResult {
  events: SSEEvent[];
  activeAgent: string | null;
  completedAgents: string[];
  status: StreamStatus;
  isComplete: boolean;
  completedTripId: string | null;
  error: string | null;
}

const ALL_EVENT_TYPES: SSEEventType[] = [
  "agent_start",
  "agent_complete",
  "tool_call",
  "tool_result",
  "thinking",
  "conflict_detected",
  "trip_complete",
  "error",
  "keepalive",
];

export function useSSEStream(tripId: string): UseSSEStreamResult {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [completedAgents, setCompletedAgents] = useState<string[]>([]);
  const [status, setStatus] = useState<StreamStatus>("connecting");
  const [isComplete, setIsComplete] = useState(false);
  const [completedTripId, setCompletedTripId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Ref to avoid stale closure in onerror — tracks whether trip_complete was received.
  const tripCompleteReceived = useRef(false);

  useEffect(() => {
    if (!tripId) return;

    tripCompleteReceived.current = false;

    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
    const url = `${apiBase}/api/v1/trips/${tripId}/stream`;
    const es = new EventSource(url);

    function handleEvent(ev: MessageEvent) {
      let parsed: SSEEvent;
      try {
        parsed = JSON.parse(ev.data) as SSEEvent;
      } catch {
        return;
      }

      if (parsed.event === "keepalive") return;

      setStatus("streaming");
      setEvents((prev) => [...prev, parsed]);

      switch (parsed.event) {
        case "agent_start":
          if (parsed.agent) setActiveAgent(parsed.agent);
          break;
        case "agent_complete":
          if (parsed.agent) {
            setCompletedAgents((prev) => [...prev, parsed.agent!]);
          }
          setActiveAgent(null);
          break;
        case "trip_complete":
          tripCompleteReceived.current = true;
          setIsComplete(true);
          setStatus("complete");
          setCompletedTripId((parsed.data?.trip_id as string) ?? tripId);
          // Do NOT close — critic still runs after trip_complete in the same stream.
          break;
        case "error":
          setError(parsed.message ?? "An error occurred");
          setStatus("error");
          es.close();
          break;
      }
    }

    ALL_EVENT_TYPES.forEach((type) => es.addEventListener(type, handleEvent));

    es.onerror = () => {
      es.close();
      // If trip_complete was already received, onerror = server closed the stream naturally.
      // Don't clobber the complete state with an error.
      if (!tripCompleteReceived.current) {
        setError("Connection lost");
        setStatus("error");
      }
    };

    return () => {
      ALL_EVENT_TYPES.forEach((type) => es.removeEventListener(type, handleEvent));
      es.close();
    };
  }, [tripId]);

  return { events, activeAgent, completedAgents, status, isComplete, completedTripId, error };
}
