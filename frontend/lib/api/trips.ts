import { apiFetch } from "./client";
import type { TripCreate, TripResponse } from "@/lib/types/trip";

export function createTrip(payload: TripCreate): Promise<TripResponse> {
  return apiFetch<TripResponse>("/api/v1/trips", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
