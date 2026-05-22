"use client";

import { AGENT_ORDER } from "@/lib/sse";

interface AgentPipelineProps {
  activeAgent: string | null;
  completedAgents: string[];
}

const AGENT_LABELS: Record<string, string> = {
  researcher: "Researcher",
  planner: "Planner",
  synthesizer: "Synthesizer",
  conflict_checker: "Conflict Checker",
  critic: "Critic",
};

export default function AgentPipeline({ activeAgent, completedAgents }: AgentPipelineProps) {
  const effectiveCompleted =
    activeAgent === "critic"
      ? [...new Set([...completedAgents, "conflict_checker"])]
      : completedAgents;

  return (
    <div className="flex items-center gap-0">
      {AGENT_ORDER.map((agent, idx) => {
        const isActive = activeAgent === agent;
        const isDone = effectiveCompleted.includes(agent);
        const isLast = idx === AGENT_ORDER.length - 1;

        return (
          <div key={agent} className="flex items-center">
            <div className="flex flex-col items-center gap-1.5">
              {isActive && (
                <span className="w-3 h-3 rounded-full bg-[var(--accent)] animate-pulse" />
              )}
              {isDone && !isActive && (
                <span className="w-3 h-3 rounded-full bg-[var(--accent)] flex items-center justify-center">
                  <svg
                    className="w-2 h-2 text-white"
                    fill="none"
                    viewBox="0 0 8 8"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path d="M1 4l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </span>
              )}
              {!isActive && !isDone && (
                <span className="w-3 h-3 rounded-full bg-[var(--border)]" />
              )}
              <span
                className={`text-xs font-medium whitespace-nowrap ${
                  isActive
                    ? "text-[var(--accent)]"
                    : isDone
                    ? "text-[var(--text-secondary)]"
                    : "text-[var(--text-muted)]"
                }`}
              >
                {AGENT_LABELS[agent]}
              </span>
            </div>
            {!isLast && (
              <div className="w-8 sm:w-12 h-px bg-[var(--border)] mb-5 mx-1" />
            )}
          </div>
        );
      })}
    </div>
  );
}
