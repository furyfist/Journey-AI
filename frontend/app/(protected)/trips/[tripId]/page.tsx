"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Navbar from "@/components/shared/Navbar";
import PageWrapper from "@/components/shared/PageWrapper";
import TripHeader from "@/components/itinerary/TripHeader";
import DayNav from "@/components/itinerary/DayNav";
import DaySection from "@/components/itinerary/DaySection";
import RegenerateControl from "@/components/itinerary/RegenerateControl";
import { Skeleton } from "@/components/ui/skeleton";
import { useTrip } from "@/hooks/useTrip";
import type { Conflict, TripDetail } from "@/lib/types/trip";

function ActivityCardSkeleton() {
  return (
    <div className="rounded-lg border border-border bg-surface p-4 flex flex-col gap-2">
      <div className="flex items-start gap-3">
        <Skeleton className="mt-0.5 h-6 w-6 shrink-0 rounded" />
        <div className="flex-1 space-y-1.5">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
          <Skeleton className="h-3 w-1/4" />
        </div>
      </div>
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-5/6" />
    </div>
  );
}

function TimeBlockSkeleton() {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-baseline gap-2">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-3 w-28" />
      </div>
      <Skeleton className="h-3 w-2/3" />
      <div className="flex flex-col gap-3">
        <ActivityCardSkeleton />
        <ActivityCardSkeleton />
      </div>
    </div>
  );
}

function DaySectionSkeleton() {
  return (
    <div className="flex flex-col gap-6 border-b border-border py-8">
      <div className="flex items-center gap-3">
        <Skeleton className="h-7 w-7 rounded-full shrink-0" />
        <div className="space-y-1.5">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-5 w-48" />
        </div>
      </div>
      <div className="flex flex-col gap-8">
        <TimeBlockSkeleton />
        <TimeBlockSkeleton />
        <TimeBlockSkeleton />
      </div>
    </div>
  );
}

export default function TripDetailPage() {
  const params = useParams<{ tripId: string }>();
  const tripId = params?.tripId ?? "";

  const { trip, setTrip, itinerary, loading, error, refetch } = useTrip(tripId);

  const [activeDayNumber, setActiveDayNumber] = useState(1);
  const dayRefs = useRef<(HTMLDivElement | null)[]>([]);
  const visibleActiveDayNumber = itinerary?.days.some((day) => day.day_number === activeDayNumber)
    ? activeDayNumber
    : itinerary?.days[0]?.day_number ?? 1;

  const onSuccess = useCallback(
    (updated: TripDetail) => setTrip(updated),
    [setTrip],
  );

  useEffect(() => {
    if (!itinerary) return;

    const observers: IntersectionObserver[] = [];

    itinerary.days.forEach((day, index) => {
      const el = dayRefs.current[index];
      if (!el) return;

      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) setActiveDayNumber(day.day_number);
        },
        { rootMargin: "-30% 0px -60% 0px", threshold: 0 },
      );

      observer.observe(el);
      observers.push(observer);
    });

    return () => observers.forEach((o) => o.disconnect());
  }, [itinerary]);

  const scrollToDay = useCallback((dayNumber: number) => {
    const index = dayNumber - 1;
    dayRefs.current[index]?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const conflictsForDay = useCallback(
    (dayNumber: number): Conflict[] =>
      (trip?.conflicts ?? []).filter((c) => c.day_number === dayNumber),
    [trip],
  );

  if (loading) {
    return (
      <>
        <Navbar />
        <PageWrapper>
          <div className="flex flex-col gap-4 border-b border-border py-8">
            <Skeleton className="h-9 w-3/4 rounded" />
            <Skeleton className="h-5 w-1/3 rounded" />
            <Skeleton className="h-4 w-1/4 rounded" />
            <div className="flex gap-2">
              <Skeleton className="h-6 w-24 rounded-full" />
              <Skeleton className="h-6 w-20 rounded-full" />
            </div>
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
          <div className="py-4">
            <DaySectionSkeleton />
            <DaySectionSkeleton />
          </div>
        </PageWrapper>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <PageWrapper>
          <div className="py-16 text-center">
            <p className="mb-4 text-sm text-text-secondary">Failed to load itinerary.</p>
            <button
              onClick={refetch}
              className="text-sm text-accent-sage underline underline-offset-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
            >
              Try again
            </button>
          </div>
        </PageWrapper>
      </>
    );
  }

  if (!trip || !itinerary) return null;

  if (trip.status !== "completed") {
    return (
      <>
        <Navbar />
        <PageWrapper>
          <div className="py-16 text-center">
            <p className="text-text-secondary">
              Trip is still generating — check back shortly.
            </p>
          </div>
        </PageWrapper>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <PageWrapper>
        <TripHeader trip={trip} itinerary={itinerary} />

        <div className="flex flex-col gap-8 py-4 md:flex-row">
          {/* Desktop sidebar nav */}
          <aside className="hidden w-32 shrink-0 md:block">
            <DayNav
              days={itinerary.days}
              activeDayNumber={visibleActiveDayNumber}
              onDaySelect={scrollToDay}
            />
          </aside>

          {/* Mobile tab nav */}
          <div className="-mx-4 sm:-mx-6 md:hidden">
            <DayNav
              days={itinerary.days}
              activeDayNumber={visibleActiveDayNumber}
              onDaySelect={scrollToDay}
            />
          </div>

          {/* Day sections */}
          <div className="min-w-0 flex-1">
            {itinerary.days.map((day, index) => (
              <DaySection
                key={day.day_number}
                day={day}
                conflicts={conflictsForDay(day.day_number)}
                sectionRef={(el) => {
                  dayRefs.current[index] = el;
                }}
                tripId={tripId}
                onSuccess={onSuccess}
              />
            ))}

            <div className="relative py-6">
              <RegenerateControl
                tripId={tripId}
                scope="full_trip"
                onSuccess={onSuccess}
              />
            </div>
          </div>
        </div>
      </PageWrapper>
    </>
  );
}
