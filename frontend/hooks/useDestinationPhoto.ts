"use client";

import { useEffect, useState } from "react";
import { fetchPhoto, type PhotoResult } from "@/lib/api/photos";

type PhotoStatus = "loading" | "ready" | "error";

interface UseDestinationPhotoResult {
  photo: PhotoResult | null;
  status: PhotoStatus;
}

/**
 * Fetches a single destination photo from the backend.
 *
 * Design rules (matching Phase 7 guardrails):
 * - Credentials never leave the backend — this hook only calls our own API.
 * - Cancels in-flight fetches on unmount / query change.
 * - Returns status="error" on network failure so callers can show a placeholder
 *   without crashing.
 * - The backend cache + dedup layer means multiple components on the same page
 *   requesting the same destination string generate only one upstream Unsplash call.
 *
 * @param query  Destination name, e.g. "Tokyo" or "Paris, France".
 *               Pass null/undefined to skip fetching (e.g. while the trip is loading).
 */
export function useDestinationPhoto(
  query: string | null | undefined,
): UseDestinationPhotoResult {
  const [photo, setPhoto] = useState<PhotoResult | null>(null);
  const [status, setStatus] = useState<PhotoStatus>("loading");

  useEffect(() => {
    if (!query) {
      setStatus("error");
      setPhoto(null);
      return;
    }

    let cancelled = false;
    setStatus("loading");

    fetchPhoto(query)
      .then((result) => {
        if (!cancelled) {
          setPhoto(result);
          setStatus("ready");
        }
      })
      .catch(() => {
        if (!cancelled) {
          setPhoto(null);
          setStatus("error");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [query]);

  return { photo, status };
}
