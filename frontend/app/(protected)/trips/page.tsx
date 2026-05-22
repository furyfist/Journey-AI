"use client";

import Link from "next/link";
import Navbar from "@/components/shared/Navbar";
import PageWrapper from "@/components/shared/PageWrapper";
import TripCard from "@/components/trips/TripCard";
import EmptyState from "@/components/trips/EmptyState";
import { Skeleton } from "@/components/ui/skeleton";
import { useTrips } from "@/hooks/useTrips";

function TripCardSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-[var(--border)] p-5 flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <Skeleton className="w-2 h-2 rounded-full" />
        <Skeleton className="h-5 w-40" />
      </div>
      <div className="space-y-1.5">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-3 w-24" />
      </div>
    </div>
  );
}

export default function TripsPage() {
  const { trips, loading, error, deleteAndRefresh } = useTrips();

  return (
    <>
      <Navbar />
      <PageWrapper>
        <div className="py-10">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-semibold text-[var(--text-primary)]">
              My Trips
            </h1>
            <Link
              href="/"
              className="text-sm font-medium text-[var(--accent)] hover:underline"
            >
              Plan a new trip
            </Link>
          </div>

          {loading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <TripCardSkeleton key={i} />
              ))}
            </div>
          )}

          {error && !loading && (
            <div className="text-center py-16">
              <p className="text-sm text-rose-500 mb-4">{error}</p>
              <button
                onClick={() => window.location.reload()}
                className="text-sm text-[var(--accent)] hover:underline"
              >
                Retry
              </button>
            </div>
          )}

          {!loading && !error && trips.length === 0 && <EmptyState />}

          {!loading && !error && trips.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {trips.map((trip) => (
                <TripCard
                  key={trip.id}
                  trip={trip}
                  onDelete={deleteAndRefresh}
                />
              ))}
            </div>
          )}
        </div>
      </PageWrapper>
    </>
  );
}
