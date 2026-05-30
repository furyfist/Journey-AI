"use client";

import Image from "next/image";
import Link from "next/link";
import { Camera } from "lucide-react";
import type { TripListItem } from "@/lib/types/trip";
import { useDestinationPhoto } from "@/hooks/useDestinationPhoto";

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

// ---------------------------------------------------------------------------
// Photo banner — top section of the card
// ---------------------------------------------------------------------------

function CardPhotoBanner({ destination }: { destination: string }) {
  const { photo, status } = useDestinationPhoto(destination);

  // Loading shimmer
  if (status === "loading") {
    return (
      <div className="relative w-full aspect-video bg-muted overflow-hidden rounded-t-lg">
        <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.4s_infinite] bg-gradient-to-r from-transparent via-white/30 to-transparent" />
      </div>
    );
  }

  // No photo — styled placeholder keeps the card height consistent
  if (status === "error" || !photo || photo.source === "fallback" || !photo.image_url) {
    return (
      <div className="relative w-full aspect-video bg-muted rounded-t-lg flex items-center justify-center">
        <Camera size={20} strokeWidth={1.5} className="text-text-muted" />
      </div>
    );
  }

  return (
    <div className="relative w-full aspect-video overflow-hidden rounded-t-lg group-hover:brightness-95 transition-[filter] duration-300">
      <Image
        src={photo.image_url}
        alt={photo.alt_text ?? destination}
        fill
        sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
        className="object-cover transition-transform duration-500 group-hover:scale-105"
      />
      {/* Attribution — bottom-right micro label */}
      {photo.photographer_name && (
        <a
          href={photo.unsplash_page_url ?? undefined}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="absolute bottom-1.5 right-2 text-[9px] text-white/60 hover:text-white/90 transition-colors leading-none"
          title={`Photo by ${photo.photographer_name} on Unsplash`}
        >
          © {photo.photographer_name}
        </a>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main card
// ---------------------------------------------------------------------------

export default function TripCard({ trip, onDelete }: TripCardProps) {
  return (
    <div className="group relative bg-white rounded-lg border border-border flex flex-col hover:shadow-md transition-shadow overflow-hidden">
      {/* Destination photo banner */}
      <CardPhotoBanner destination={trip.destination} />

      {/* Card body */}
      <div className="flex flex-col gap-3 p-5 flex-1">
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
    </div>
  );
}
