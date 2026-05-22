"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Navbar from "@/components/shared/Navbar";
import PageWrapper from "@/components/shared/PageWrapper";
import PromptEcho from "@/components/generate/PromptEcho";
import AgentPipeline from "@/components/generate/AgentPipeline";
import LiveLog from "@/components/generate/LiveLog";
import { useSSEStream } from "@/hooks/useSSEStream";

const STATUS_LABELS: Record<string, string> = {
  connecting: "Connecting...",
  streaming: "Streaming",
  complete: "Complete",
  error: "Connection error",
};

export default function GeneratePage() {
  const params = useParams<{ tripId: string }>();
  const tripId = params?.tripId ?? "";
  const router = useRouter();

  const { events, activeAgent, completedAgents, status, isComplete } =
    useSSEStream(tripId);

  useEffect(() => {
    if (!isComplete) return;
    const t = setTimeout(() => router.push(`/trips/${tripId}`), 500);
    return () => clearTimeout(t);
  }, [isComplete, tripId, router]);

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
            <p className="text-xs text-[var(--text-muted)] mt-2">
              {STATUS_LABELS[status] ?? status}
            </p>
          </div>

          <LiveLog events={events} onRetry={() => window.location.reload()} />
        </div>
      </PageWrapper>
    </>
  );
}
