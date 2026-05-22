"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Navbar from "@/components/shared/Navbar";
import PageWrapper from "@/components/shared/PageWrapper";
import TripHeader from "@/components/itinerary/TripHeader";
import DayNav from "@/components/itinerary/DayNav";
import DaySection from "@/components/itinerary/DaySection";
import { Skeleton } from "@/components/ui/skeleton";
import { useTrip } from "@/hooks/useTrip";
import type { Conflict } from "@/lib/types/trip";

export default function TripDetailPage() {
  const params = useParams<{ tripId: string }>();
  const tripId = params?.tripId ?? "";

  const { trip, itinerary, loading, error } = useTrip(tripId);

  const [activeDayNumber, setActiveDayNumber] = useState(1);
  const dayRefs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    if (!itinerary) return;

    const observers: IntersectionObserver[] = [];

    itinerary.days.forEach((day, index) => {
      const el = dayRefs.current[index];
      if (!el) return;

      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setActiveDayNumber(day.day_number);
          }
        },
        { rootMargin: "-30% 0px -60% 0px", threshold: 0 }
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
    [trip]
  );

  if (loading) {
    return (
      <>
        <Navbar />
        <PageWrapper>
          <div className="flex flex-col gap-6 py-8">
            <Skeleton className="h-10 w-3/4 rounded" />
            <Skeleton className="h-5 w-1/3 rounded" />
            <Skeleton className="h-4 w-1/4 rounded" />
            <div className="flex gap-2 mt-2">
              <Skeleton className="h-6 w-24 rounded-full" />
              <Skeleton className="h-6 w-20 rounded-full" />
            </div>
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
            <p className="text-text-secondary mb-4">Failed to load itinerary.</p>
            <button
              onClick={() => window.location.reload()}
              className="text-sm text-accent-sage underline underline-offset-2"
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

        <div className="flex flex-col md:flex-row gap-8 py-4">
          {/* Desktop sidebar nav */}
          <aside className="hidden md:block w-32 shrink-0">
            <DayNav
              days={itinerary.days}
              activeDayNumber={activeDayNumber}
              onDaySelect={scrollToDay}
            />
          </aside>

          {/* Mobile tab nav */}
          <div className="md:hidden -mx-4 sm:-mx-6">
            <DayNav
              days={itinerary.days}
              activeDayNumber={activeDayNumber}
              onDaySelect={scrollToDay}
            />
          </div>

          {/* Day sections */}
          <div className="flex-1 min-w-0">
            {itinerary.days.map((day, index) => (
              <DaySection
                key={day.day_number}
                day={day}
                conflicts={conflictsForDay(day.day_number)}
                sectionRef={(el) => {
                  dayRefs.current[index] = el;
                }}
              />
            ))}
          </div>
        </div>
      </PageWrapper>
    </>
  );
}
