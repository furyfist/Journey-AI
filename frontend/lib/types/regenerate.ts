export type RegenerateScope = "full_trip" | "day" | "single_block";

export interface RegenerateRequest {
  scope: RegenerateScope;
  day_number?: number;
  block_label?: "morning" | "afternoon" | "evening";
  constraint?: string;
}
