"use client";

import { useCallback, useEffect, useState } from "react";
import { listTrips, deleteTrip } from "@/lib/api/trips";
import type { TripListItem } from "@/lib/types/trip";

interface UseTripsResult {
  trips: TripListItem[];
  loading: boolean;
  error: string | null;
  deleteAndRefresh: (id: string) => Promise<void>;
}

export function useTrips(): UseTripsResult {
  const [trips, setTrips] = useState<TripListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    listTrips()
      .then((data) => {
        if (!cancelled) setTrips(data);
      })
      .catch((err: unknown) => {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Failed to load trips");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const deleteAndRefresh = useCallback(async (id: string) => {
    await deleteTrip(id);
    setTrips((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return { trips, loading, error, deleteAndRefresh };
}
