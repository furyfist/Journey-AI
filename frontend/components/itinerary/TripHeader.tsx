"use client";

import Image from "next/image";
import { Camera } from "lucide-react";
import type { TripDetail, ItinerarySchema } from "@/lib/types/trip";
import Badge from "@/components/shared/Badge";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";
import { useDestinationPhoto } from "@/hooks/useDestinationPhoto";

interface TripHeaderProps {
  trip: TripDetail;
  itinerary: ItinerarySchema;
}

// ---------------------------------------------------------------------------
// Hero image — full-width, 16:5 aspect ratio with a bottom gradient overlay
// so the title text remains legible over any photo tone.
// ---------------------------------------------------------------------------

function HeroImage({ destination }: { destination: string }) {
  const { photo, status } = useDestinationPhoto(destination);

  // Loading shimmer — same height as the rendered hero
  if (status === "loading") {
    return (
      <div className="relative w-full aspect-[16/5] bg-muted overflow-hidden rounded-xl">
        <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.4s_infinite] bg-gradient-to-r from-transparent via-white/30 to-transparent" />
      </div>
    );
  }

  // Fallback — subtle muted band with destination-initial monogram
  if (status === "error" || !photo || photo.source === "fallback" || !photo.image_url) {
    return (
      <div className="relative w-full aspect-[16/5] bg-muted rounded-xl flex items-center justify-center">
        <div className="flex flex-col items-center gap-1.5 text-text-muted">
          <Camera size={28} strokeWidth={1.5} />
          <span className="text-xs">{destination}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full aspect-[16/5] rounded-xl overflow-hidden">
      <Image
        src={photo.image_url}
        alt={photo.alt_text ?? destination}
        fill
        priority
        sizes="(max-width: 1280px) 100vw, 1280px"
        className="object-cover"
      />

      {/* Bottom gradient so title text is always readable */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent pointer-events-none" />

      {/* Attribution — bottom-right micro label */}
      {photo.photographer_name && (
        <a
          href={photo.unsplash_page_url ?? undefined}
          target="_blank"
          rel="noopener noreferrer"
          className="absolute bottom-2 right-3 text-[10px] text-white/60 hover:text-white/90 transition-colors leading-none"
          title={`Photo by ${photo.photographer_name} on Unsplash`}
        >
          Photo by{" "}
          <span className="underline underline-offset-2">{photo.photographer_name}</span>{" "}
          on Unsplash
        </a>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main header
// ---------------------------------------------------------------------------

export default function TripHeader({ trip, itinerary }: TripHeaderProps) {
  const destination = itinerary.destination || trip.destination;

  return (
    <div className="flex flex-col gap-5 py-8 border-b border-border">
      {/* Hero photo */}
      <HeroImage destination={destination} />

      {/* Title block */}
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold text-text-primary leading-tight">
          {itinerary.title}
        </h1>
        <p className="text-lg text-text-secondary">{itinerary.destination}</p>
        <p className="text-sm text-text-muted">
          {itinerary.total_days} {itinerary.total_days === 1 ? "day" : "days"}
        </p>
      </div>

      {/* Persona / budget badges */}
      <div className="flex items-center gap-2 flex-wrap">
        {itinerary.persona && (
          <Badge variant="persona">{itinerary.persona}</Badge>
        )}
        {itinerary.budget_level && (
          <Badge variant="budget">{itinerary.budget_level}</Badge>
        )}
      </div>

      {/* Summary */}
      {itinerary.summary && (
        <p className="text-text-secondary leading-relaxed max-w-2xl">
          {itinerary.summary}
        </p>
      )}

      {/* Travel tips accordion */}
      {itinerary.tips && itinerary.tips.length > 0 && (
        <Accordion className="max-w-2xl">
          <AccordionItem value="tips">
            <AccordionTrigger className="text-sm font-medium text-text-primary">
              Travel Tips ({itinerary.tips.length})
            </AccordionTrigger>
            <AccordionContent>
              <ul className="flex flex-col gap-2 pt-1">
                {itinerary.tips.map((tip, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                    <span className="text-accent-sage mt-0.5 shrink-0">·</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      )}
    </div>
  );
}
