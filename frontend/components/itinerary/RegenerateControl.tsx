"use client";

import { useCallback, useState } from "react";
import { useRegenerate } from "@/hooks/useRegenerate";
import type { TripDetail } from "@/lib/types/trip";
import type { RegenerateScope } from "@/lib/types/regenerate";

interface Props {
  tripId: string;
  scope: RegenerateScope;
  dayNumber?: number;
  blockLabel?: "morning" | "afternoon" | "evening";
  onSuccess: (updated: TripDetail) => void;
}

const SCOPE_LABEL: Record<RegenerateScope, string> = {
  single_block: "block",
  day: "day",
  full_trip: "trip",
};

export default function RegenerateControl({
  tripId,
  scope,
  dayNumber,
  blockLabel,
  onSuccess,
}: Props) {
  const [open, setOpen] = useState(false);
  const [constraint, setConstraint] = useState("");

  const handleSuccess = useCallback(
    (updated: TripDetail) => {
      onSuccess(updated);
      setOpen(false);
      setConstraint("");
    },
    [onSuccess],
  );

  const { regenerate, loading, error } = useRegenerate(tripId, handleSuccess);

  const handleGo = useCallback(() => {
    regenerate({
      scope,
      day_number: dayNumber,
      block_label: blockLabel,
      constraint: constraint.trim() || undefined,
    });
  }, [regenerate, scope, dayNumber, blockLabel, constraint]);

  return (
    <>
      {loading && (
        <div className="absolute inset-0 bg-white/60 backdrop-blur-[1px] z-10 rounded-lg" />
      )}

      {!open ? (
        <button
          onClick={() => setOpen(true)}
          className="mt-2 self-start text-xs text-text-muted hover:text-text-secondary transition-colors"
        >
          Regenerate this {SCOPE_LABEL[scope]}
        </button>
      ) : (
        <div className="mt-3 flex flex-col gap-1.5">
          <div className="flex flex-wrap items-center gap-2">
            <input
              type="text"
              value={constraint}
              onChange={(e) => setConstraint(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && handleGo()}
              placeholder="Any changes? e.g. 'avoid museums'"
              disabled={loading}
              className="min-w-0 flex-1 rounded border border-border bg-white px-3 py-1.5 text-sm placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent-sage disabled:opacity-50"
            />
            <button
              onClick={handleGo}
              disabled={loading}
              className="rounded bg-accent-sage px-3 py-1.5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {loading ? "…" : "Go"}
            </button>
            <button
              onClick={() => {
                setOpen(false);
                setConstraint("");
              }}
              disabled={loading}
              className="text-xs text-text-muted transition-colors hover:text-text-secondary disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
          {error && <p className="text-xs text-danger">{error}</p>}
        </div>
      )}
    </>
  );
}
