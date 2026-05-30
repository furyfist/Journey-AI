import { apiFetch } from "./client";

export interface PhotoResult {
  query: string;
  image_url: string | null;
  thumb_url: string | null;
  alt_text: string | null;
  photographer_name: string | null;
  photographer_url: string | null;
  unsplash_page_url: string | null;
  source: "unsplash" | "fallback";
}

export function fetchPhoto(query: string): Promise<PhotoResult> {
  const params = new URLSearchParams({ query });
  return apiFetch<PhotoResult>(`/api/v1/photos/search?${params}`);
}
