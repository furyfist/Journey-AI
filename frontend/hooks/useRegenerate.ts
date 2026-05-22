"use client";

import { useCallback, useState } from "react";
import { regenerateTrip } from "@/lib/api/regenerate";
import type { TripDetail } from "@/lib/types/trip";
import type { RegenerateRequest } from "@/lib/types/regenerate";

export function useRegenerate(
  tripId: string,
  onSuccess: (updated: TripDetail) => void,
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const regenerate = useCallback(
    async (req: RegenerateRequest) => {
      setLoading(true);
      setError(null);
      try {
        const updated = await regenerateTrip(tripId, req);
        onSuccess(updated);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Regeneration failed");
      } finally {
        setLoading(false);
      }
    },
    [tripId, onSuccess],
  );

  return { regenerate, loading, error };
}
