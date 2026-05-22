import { apiFetch } from "./client";
import type { TripDetail } from "@/lib/types/trip";
import type { RegenerateRequest } from "@/lib/types/regenerate";

export function regenerateTrip(
  tripId: string,
  req: RegenerateRequest,
): Promise<TripDetail> {
  return apiFetch<TripDetail>(`/api/v1/trips/${tripId}/regenerate`, {
    method: "POST",
    body: JSON.stringify(req),
  });
}
