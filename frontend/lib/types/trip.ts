export interface TripCreate {
  prompt: string;
  destination?: string;
  budget?: string;
  total_days?: number;
  persona_hint?: string;
  interests?: string[];
  constraints?: string[];
  travel_party?: string;
}

export interface TripResponse {
  id: string;
  prompt: string;
  destination: string;
  title: string;
  status: "pending" | "generating" | "completed" | "failed";
  persona?: string;
  budget_level?: string;
  total_days?: number;
  summary?: string;
  created_at: string;
  updated_at?: string;
}

export interface Activity {
  name: string;
  description: string;
  location: string;
  latitude?: number;
  longitude?: number;
  duration_minutes: number;
  cost_estimate?: string;
  category: string;
  reasoning: string;
}

export interface TimeBlock {
  label: "morning" | "afternoon" | "evening";
  start_time: string;
  end_time: string;
  activities: Activity[];
  block_summary: string;
}

export interface DayPlan {
  day_number: number;
  date?: string;
  title: string;
  weather?: { description: string; temperature_max: number; temperature_min: number; precipitation_mm: number; weather_code: number; date?: string } | null;
  morning: TimeBlock;
  afternoon: TimeBlock;
  evening: TimeBlock;
  day_summary: string;
}

export interface ItinerarySchema {
  title: string;
  destination: string;
  total_days: number;
  budget_level: string;
  persona: string;
  summary: string;
  days: DayPlan[];
  tips: string[];
}

export interface Conflict {
  type: string;
  severity: "warning" | "error";
  day_number: number;
  description: string;
  activities: string[];
}

export interface TripDetail extends TripResponse {
  itinerary?: ItinerarySchema;
  conflicts?: Conflict[];
  reasoning?: string;
  weather_data?: Record<string, unknown>;
}

export interface TripListItem {
  id: string;
  title: string;
  destination: string;
  total_days?: number;
  status: TripResponse["status"];
  created_at: string;
}
