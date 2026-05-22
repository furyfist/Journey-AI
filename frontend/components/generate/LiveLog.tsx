"use client";

import { useEffect, useRef } from "react";
import type { SSEEvent } from "@/lib/types/planning";

interface LiveLogProps {
  events: SSEEvent[];
  onRetry?: () => void;
}

function formatEvent(e: SSEEvent): { prefix: string; text: string; isError: boolean } {
  switch (e.event) {
    case "agent_start":
      return { prefix: "▶", text: e.message ?? `${e.agent} started`, isError: false };
    case "agent_complete":
      return { prefix: "✓", text: e.message ?? `${e.agent} complete`, isError: false };
    case "tool_call":
      return { prefix: "⚙", text: e.message ?? `Calling tool`, isError: false };
    case "tool_result":
      return { prefix: "↩", text: e.message ?? `Tool result received`, isError: false };
    case "thinking":
      return { prefix: "…", text: e.message ?? `Thinking`, isError: false };
    case "conflict_detected":
      return { prefix: "⚠", text: e.message ?? `Conflict detected`, isError: false };
    case "trip_complete":
      return { prefix: "★", text: e.message ?? `Trip generation complete`, isError: false };
    case "error":
      return { prefix: "✕", text: e.message ?? `An error occurred`, isError: true };
    default:
      return { prefix: "·", text: e.message ?? e.event, isError: false };
  }
}

export default function LiveLog({ events, onRetry }: LiveLogProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  const visible = events.filter((e) => e.event !== "keepalive");

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [visible.length]);

  return (
    <div className="bg-[#fafafa] border border-[var(--border)] rounded-lg p-4 font-mono text-xs overflow-y-auto max-h-72 space-y-1">
      {visible.map((e, idx) => {
        const { prefix, text, isError } = formatEvent(e);
        const delay = Math.min(idx * 40, 400);

        return (
          <div
            key={idx}
            className="flex gap-2 items-start opacity-0 translate-y-1 animate-log-in"
            style={{
              animationDelay: `${delay}ms`,
              animationFillMode: "forwards",
            }}
          >
            <span
              className={`flex-shrink-0 w-4 text-center ${
                isError
                  ? "text-[var(--danger)]"
                  : e.event === "trip_complete"
                  ? "text-[var(--accent)]"
                  : e.event === "conflict_detected"
                  ? "text-amber-500"
                  : "text-[var(--text-muted)]"
              }`}
            >
              {prefix}
            </span>
            <span
              className={
                isError
                  ? "text-[var(--danger)]"
                  : e.event === "trip_complete"
                  ? "text-[var(--accent)] font-medium"
                  : "text-[var(--text-secondary)]"
              }
            >
              {text}
            </span>
          </div>
        );
      })}

      {visible.some((e) => e.event === "error") && onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 text-xs text-[var(--accent)] hover:underline focus-visible:ring-2"
        >
          Retry
        </button>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
