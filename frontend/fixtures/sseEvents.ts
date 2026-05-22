import type { SSEEvent } from "@/lib/types/planning";

export const sseFixtureEvents: SSEEvent[] = [
  {
    event: "keepalive",
    message: "connected",
  },
  {
    event: "agent_start",
    agent: "researcher",
    message: "Researcher agent starting — gathering destination intelligence",
  },
  {
    event: "tool_call",
    agent: "researcher",
    data: { tool: "search_web", query: "Tokyo travel tips best areas to stay" },
    message: "Calling search_web: Tokyo travel tips best areas to stay",
  },
  {
    event: "tool_result",
    agent: "researcher",
    data: { tool: "search_web", result_count: 12 },
    message: "search_web returned 12 results",
  },
  {
    event: "tool_call",
    agent: "researcher",
    data: { tool: "get_weather", destination: "Tokyo", dates: "2024-04-10 to 2024-04-15" },
    message: "Calling get_weather: Tokyo, April 2024",
  },
  {
    event: "tool_result",
    agent: "researcher",
    data: { tool: "get_weather", avg_temp: "16°C", condition: "partly cloudy" },
    message: "get_weather returned forecast data",
  },
  {
    event: "thinking",
    agent: "researcher",
    message: "Analysing cherry blossom season overlap and crowd patterns",
  },
  {
    event: "agent_complete",
    agent: "researcher",
    message: "Researcher complete — destination profile ready",
  },
  {
    event: "agent_start",
    agent: "planner",
    message: "Planner agent starting — drafting day-by-day schedule",
  },
  {
    event: "thinking",
    agent: "planner",
    message: "Balancing temple visits with neighbourhood exploration and meal windows",
  },
  {
    event: "tool_call",
    agent: "planner",
    data: { tool: "estimate_travel_time", from: "Shinjuku", to: "Asakusa", mode: "subway" },
    message: "Calling estimate_travel_time: Shinjuku → Asakusa",
  },
  {
    event: "tool_result",
    agent: "planner",
    data: { tool: "estimate_travel_time", minutes: 35 },
    message: "estimate_travel_time returned 35 min",
  },
  {
    event: "agent_complete",
    agent: "planner",
    message: "Planner complete — 5-day structure locked in",
  },
  {
    event: "agent_start",
    agent: "synthesizer",
    message: "Synthesizer agent starting — assembling final itinerary",
  },
  {
    event: "thinking",
    agent: "synthesizer",
    message: "Enriching activity descriptions and writing day summaries",
  },
  {
    event: "agent_complete",
    agent: "synthesizer",
    message: "Synthesizer complete — itinerary fully written",
  },
  {
    event: "agent_start",
    agent: "conflict_checker",
    message: "Conflict Checker scanning for timing and logistics issues",
  },
  {
    event: "conflict_detected",
    agent: "conflict_checker",
    data: {
      type: "timing_overlap",
      severity: "warning",
      day_number: 2,
      description: "Tsukiji Outer Market closes at 14:00 — afternoon slot may arrive too late",
      activities: ["Tsukiji Outer Market", "teamLab Borderless"],
    },
    message: "Conflict detected: timing overlap on day 2",
  },
  {
    event: "conflict_detected",
    agent: "conflict_checker",
    data: {
      type: "distance",
      severity: "warning",
      day_number: 4,
      description: "Nikko is 2h from central Tokyo — full-day trip recommended, not a half-day add-on",
      activities: ["Toshogu Shrine", "Kegon Falls"],
    },
    message: "Conflict detected: travel distance on day 4",
  },
  {
    event: "agent_start",
    agent: "critic",
    message: "Critic agent starting — reviewing quality and coherence",
  },
  {
    event: "thinking",
    agent: "critic",
    message: "Checking pacing, budget fit, and persona alignment across all days",
  },
  {
    event: "agent_complete",
    agent: "critic",
    message: "Critic complete — itinerary approved with minor notes",
  },
  {
    event: "trip_complete",
    data: { trip_id: "fixture-trip-id" },
    message: "Trip generation complete",
  },
];
