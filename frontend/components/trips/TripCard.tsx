"use client";

import Link from "next/link";
import type { TripListItem } from "@/lib/types/trip";

interface TripCardProps {
  trip: TripListItem;
  onDelete: (id: string) => void;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function StatusDot({ status }: { status: TripListItem["status"] }) {
  const base = "inline-block w-2 h-2 rounded-full flex-shrink-0";

  if (status === "generating" || status === "pending") {
    return (
      <span
        className={`${base} bg-accent-sage animate-pulse`}
        aria-label={`Status: ${status}`}
      />
    );
  }
  if (status === "completed") {
    return (
      <span
        className={`${base} bg-accent-sage`}
        aria-label="Status: completed"
      />
    );
  }
  return (
    <span
      className={`${base} bg-rose-400`}
      aria-label="Status: failed"
    />
  );
}

export default function TripCard({ trip, onDelete }: TripCardProps) {
  return (
    <div className="group relative bg-white rounded-lg border border-border p-5 flex flex-col gap-3 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <StatusDot status={trip.status} />
          <h3 className="font-semibold text-text-primary truncate leading-tight">
            {trip.title || "Untitled Trip"}
          </h3>
        </div>
      </div>

      <div className="text-sm text-text-secondary space-y-0.5">
        <p className="truncate">{trip.destination}</p>
        {trip.total_days && (
          <p className="text-text-muted">
            {trip.total_days} {trip.total_days === 1 ? "day" : "days"}
          </p>
        )}
        <p className="text-text-muted text-xs">{formatDate(trip.created_at)}</p>
      </div>

      <div className="mt-auto pt-2 flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
        <Link
          href={`/trips/${trip.id}`}
          className="text-sm font-medium text-accent-sage hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
        >
          Open
        </Link>
        <button
          onClick={() => onDelete(trip.id)}
          className="text-sm text-text-muted hover:text-rose-500 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
