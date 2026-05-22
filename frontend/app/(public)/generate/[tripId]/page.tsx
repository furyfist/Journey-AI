"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/shared/Navbar";
import PageWrapper from "@/components/shared/PageWrapper";
import PromptEcho from "@/components/generate/PromptEcho";
import AgentPipeline from "@/components/generate/AgentPipeline";
import LiveLog from "@/components/generate/LiveLog";
import { sseFixtureEvents } from "@/fixtures/sseEvents";
import type { SSEEvent } from "@/lib/types/planning";

export default function GeneratePage() {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [completedAgents, setCompletedAgents] = useState<string[]>([]);

  useEffect(() => {
    let idx = 0;

    const interval = setInterval(() => {
      if (idx >= sseFixtureEvents.length) {
        clearInterval(interval);
        return;
      }

      const e = sseFixtureEvents[idx];
      idx++;

      setEvents((prev) => [...prev, e]);

      if (e.event === "agent_start" && e.agent) {
        setActiveAgent(e.agent);
      }
      if (e.event === "agent_complete" && e.agent) {
        setCompletedAgents((prev) => [...prev, e.agent!]);
        setActiveAgent(null);
      }
    }, 300);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <Navbar />
      <PageWrapper>
        <div className="max-w-2xl mx-auto py-10 flex flex-col gap-8">
          <PromptEcho />

          <div>
            <p className="text-xs text-text-muted uppercase tracking-wide mb-4 font-medium">
              Planning your trip
            </p>
            <AgentPipeline activeAgent={activeAgent} completedAgents={completedAgents} />
          </div>

          <LiveLog events={events} onRetry={() => window.location.reload()} />
        </div>
      </PageWrapper>
    </>
  );
}
