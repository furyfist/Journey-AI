import { apiFetch } from "./client";
import type { TripCreate, TripDetail, TripListItem, TripResponse } from "@/lib/types/trip";

export function createTrip(payload: TripCreate): Promise<TripResponse> {
  return apiFetch<TripResponse>("/api/v1/trips", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listTrips(): Promise<TripListItem[]> {
  return apiFetch<TripListItem[]>("/api/v1/trips");
}

export function deleteTrip(id: string): Promise<void> {
  return apiFetch<void>(`/api/v1/trips/${id}`, { method: "DELETE" });
}

export function getTrip(id: string): Promise<TripDetail> {
  return apiFetch<TripDetail>(`/api/v1/trips/${id}`);
}
