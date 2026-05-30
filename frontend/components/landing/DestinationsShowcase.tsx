"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import dynamic from "next/dynamic";
import { Camera } from "lucide-react";
import PageWrapper from "@/components/shared/PageWrapper";
import { fetchPhoto, type PhotoResult } from "@/lib/api/photos";

// Dynamically import InteractiveMap to prevent Next.js SSR window reference errors
const InteractiveMap = dynamic(
  () => import("./InteractiveMap"),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full bg-muted/40 animate-pulse rounded-2xl flex items-center justify-center border border-border">
        <div className="flex flex-col items-center gap-2 text-text-muted">
          <div className="h-5 w-5 rounded-full border-2 border-accent-sage border-t-transparent animate-spin" />
          <span className="text-xs">Loading live interactive map...</span>
        </div>
      </div>
    ),
  }
);

// ---------------------------------------------------------------------------
// Static panel data — the activities and city metadata stay here;
// photos are fetched from the backend at runtime.
// ---------------------------------------------------------------------------
const PANELS = [
  {
    city: "Tokyo, Japan",
    weather: "☀️ 22°C",
    activities: [
      { time: "9:00 AM",  name: "Tsukiji Outer Market", tag: "Food",    tagColor: "bg-orange-50 text-orange-600" },
      { time: "11:30 AM", name: "teamLab Borderless",   tag: "Art",     tagColor: "bg-purple-50 text-purple-600" },
      { time: "2:00 PM",  name: "Senso-ji Temple",      tag: "Culture", tagColor: "bg-blue-50   text-blue-600"   },
    ],
  },
  {
    city: "Shibuya & Harajuku",
    weather: "🌤 20°C",
    activities: [
      { time: "10:00 AM", name: "Shibuya Crossing", tag: "Landmark", tagColor: "bg-blue-50  text-blue-600"  },
      { time: "12:30 PM", name: "Takeshita Street", tag: "Shopping", tagColor: "bg-pink-50  text-pink-600"  },
      { time: "3:00 PM",  name: "Yoyogi Park",      tag: "Outdoors", tagColor: "bg-green-50 text-green-600" },
    ],
  },
];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

/** Shimmer skeleton that holds the aspect-video slot while the photo loads. */
function PhotoSkeleton() {
  return (
    <div className="w-full aspect-video rounded-xl bg-muted overflow-hidden relative">
      <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.4s_infinite] bg-gradient-to-r from-transparent via-white/30 to-transparent" />
    </div>
  );
}

/** Styled placeholder shown when no photo is available (fallback or error). */
function PhotoPlaceholder({ city }: { city: string }) {
  return (
    <div className="w-full aspect-video rounded-xl bg-muted flex items-center justify-center">
      <div className="flex flex-col items-center gap-1.5 text-text-muted">
        <Camera size={24} strokeWidth={1.5} />
        <span className="text-xs">{city}</span>
      </div>
    </div>
  );
}

interface AttributionProps {
  photographerName: string | null;
  photographerUrl: string | null;
  unsplashPageUrl: string | null;
}

/** Small Unsplash attribution line — required by Unsplash API guidelines. */
function Attribution({ photographerName, photographerUrl, unsplashPageUrl }: AttributionProps) {
  if (!photographerName) return null;

  return (
    <p className="mt-1.5 text-[10px] text-text-muted leading-none">
      Photo by{" "}
      {photographerUrl ? (
        <a
          href={photographerUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="underline underline-offset-2 hover:text-text-secondary transition-colors"
        >
          {photographerName}
        </a>
      ) : (
        photographerName
      )}{" "}
      on{" "}
      {unsplashPageUrl ? (
        <a
          href={unsplashPageUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="underline underline-offset-2 hover:text-text-secondary transition-colors"
        >
          Unsplash
        </a>
      ) : (
        "Unsplash"
      )}
    </p>
  );
}

interface DestinationPhotoProps {
  city: string;
}

/** Fetches and renders a single destination photo with loading and fallback states. */
function DestinationPhoto({ city }: DestinationPhotoProps) {
  const [photo, setPhoto] = useState<PhotoResult | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let cancelled = false;

    fetchPhoto(city)
      .then((result) => {
        if (!cancelled) {
          setPhoto(result);
          setStatus("ready");
        }
      })
      .catch(() => {
        if (!cancelled) setStatus("error");
      });

    return () => { cancelled = true; };
  }, [city]);

  if (status === "loading") {
    return <PhotoSkeleton />;
  }

  if (status === "error" || !photo || photo.source === "fallback" || !photo.image_url) {
    return <PhotoPlaceholder city={city} />;
  }

  return (
    <div>
      <div className="w-full aspect-video rounded-xl overflow-hidden relative group">
        <Image
          src={photo.image_url}
          alt={photo.alt_text ?? city}
          fill
          sizes="(max-width: 768px) 100vw, 50vw"
          className="object-cover transition-transform duration-500 group-hover:scale-105"
          unoptimized={false}
        />
      </div>
      <Attribution
        photographerName={photo.photographer_name}
        photographerUrl={photo.photographer_url}
        unsplashPageUrl={photo.unsplash_page_url}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

export default function DestinationsShowcase() {
  const [activeCityIndex, setActiveCityIndex] = useState<number | null>(null);

  return (
    <section id="explore" className="py-20 sm:py-24 bg-muted/40">
      <PageWrapper>
        <div className="text-center mb-12">
          <p className="text-xs font-semibold uppercase tracking-widest text-text-muted mb-3">
            Live example
          </p>
          <h2 className="text-3xl sm:text-4xl font-semibold text-text-primary tracking-tight">
            See What a Real Trip Looks Like
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {PANELS.map(({ city, weather, activities }, idx) => {
            const isActive = activeCityIndex === idx;
            return (
              <div
                key={city}
                onClick={() => setActiveCityIndex(isActive ? null : idx)}
                className={`bg-surface border rounded-2xl overflow-hidden cursor-pointer transition-all duration-300 ${
                  isActive
                    ? "border-accent-sage ring-2 ring-accent-sage/20 shadow-md scale-[1.01]"
                    : "border-border hover:border-text-muted/40 shadow-sm"
                }`}
              >
                {/* Card header */}
                <div className="px-5 py-4 border-b border-border">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-text-primary">{city}</span>
                    <span className="text-sm text-text-secondary">{weather}</span>
                  </div>
                </div>

                {/* Activity list */}
                <div className="px-5 py-3 space-y-3">
                  {activities.map(({ time, name, tag, tagColor }) => (
                    <div key={time} className="flex items-center gap-3">
                      <span className="text-xs text-text-muted w-[72px] shrink-0">{time}</span>
                      <div className="h-4 w-4 rounded-full bg-muted shrink-0" />
                      <span className="text-sm text-text-primary flex-1 min-w-0 truncate">{name}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 font-medium ${tagColor}`}>
                        {tag}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Destination photo */}
                <div className="px-5 pb-5 pt-2">
                  <DestinationPhoto city={city} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Interactive Map */}
        <div className="relative w-full rounded-2xl aspect-[16/6] md:aspect-[16/5] min-h-[320px] overflow-hidden">
          <InteractiveMap
            activeCityIndex={activeCityIndex}
            onSelectCity={setActiveCityIndex}
          />
        </div>
      </PageWrapper>
    </section>
  );
}
