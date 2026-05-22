"use client";

import React, { useEffect, useState } from "react";
import { getTrip } from "@/lib/api/trips";
import type { TripDetail, ItinerarySchema } from "@/lib/types/trip";

interface UseTripResult {
  trip: TripDetail | null;
  setTrip: React.Dispatch<React.SetStateAction<TripDetail | null>>;
  itinerary: ItinerarySchema | null;
  loading: boolean;
  error: string | null;
}

export function useTrip(tripId: string): UseTripResult {
  const [trip, setTrip] = useState<TripDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    getTrip(tripId)
      .then((data) => {
        if (!cancelled) setTrip(data);
      })
      .catch((err: unknown) => {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Failed to load trip");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [tripId]);

  const itinerary = trip?.itinerary ? (trip.itinerary as ItinerarySchema) : null;

  return { trip, setTrip, itinerary, loading, error };
}
