"use client";

import { useState } from "react";
import { ChevronLeft } from "lucide-react";
import type { TripCreate } from "@/lib/types/trip";

const BUDGET_OPTIONS = ["Budget", "Mid-range", "Luxury"] as const;

const TRAVEL_STYLE_OPTIONS = [
  "Backpacker",
  "Foodie",
  "Culture Seeker",
  "Adventure Junkie",
  "Family Traveler",
  "Digital Nomad",
  "Luxury Explorer",
] as const;

const INTEREST_OPTIONS = [
  "Food",
  "Culture",
  "Nature",
  "Nightlife",
  "Shopping",
  "Art",
  "History",
  "Beaches",
  "Architecture",
] as const;

const CONSTRAINT_OPTIONS = [
  "Vegetarian",
  "Less walking",
  "Indoor mostly",
  "Family friendly",
  "Accessibility needs",
  "Halal food",
] as const;

const TRAVEL_PARTY_OPTIONS = ["Solo", "Couple", "Group", "Family"] as const;

function extractFromPrompt(prompt: string): { destination?: string; total_days?: number } {
  const daysMatch = prompt.match(/(\d+)\s*[-–]?\s*day/i);
  const total_days = daysMatch ? Math.min(30, Math.max(1, parseInt(daysMatch[1], 10))) : undefined;

  const destMatch = prompt.match(
    /(?:to|in|visit|explore|go\s+to|travel\s+to)\s+([A-Z][a-zA-Z\s]{2,30?}?)(?=\s+for|\s+trip|\s+holiday|\s+focused|\s+with|,|\.|$)/i
  );
  const destination = destMatch ? destMatch[1].trim() : undefined;

  return { destination, total_days };
}

interface TripDetailsFormProps {
  prompt: string;
  onBack: () => void;
  onSubmit: (payload: TripCreate) => void;
  loading?: boolean;
  error?: string | null;
}

export default function TripDetailsForm({
  prompt,
  onBack,
  onSubmit,
  loading = false,
  error,
}: TripDetailsFormProps) {
  const prefilled = extractFromPrompt(prompt);

  const [destination, setDestination] = useState(prefilled.destination ?? "");
  const [totalDays, setTotalDays] = useState<number>(prefilled.total_days ?? 5);
  const [budget, setBudget] = useState<string>("");
  const [travelStyle, setTravelStyle] = useState<string>("");
  const [interests, setInterests] = useState<string[]>([]);
  const [constraints, setConstraints] = useState<string[]>([]);
  const [travelParty, setTravelParty] = useState<string>("");

  function toggleMulti(value: string, list: string[], setter: (v: string[]) => void) {
    setter(list.includes(value) ? list.filter((v) => v !== value) : [...list, value]);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (loading) return;
    onSubmit({
      prompt,
      destination: destination.trim() || undefined,
      total_days: totalDays,
      budget: budget || undefined,
      persona_hint: travelStyle || undefined,
      interests: interests.length ? interests.map((i) => i.toLowerCase()) : undefined,
      constraints: constraints.length ? constraints.map((c) => c.toLowerCase()) : undefined,
      travel_party: travelParty || undefined,
    });
  }

  const canSubmit = !loading && destination.trim().length > 0;

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-5">
      {/* Back + heading */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onBack}
          className="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-muted transition-colors"
        >
          <ChevronLeft size={18} />
        </button>
        <p className="text-sm text-text-secondary">Tell us a bit more about your trip</p>
      </div>

      {/* Row 1: Destination + Trip length */}
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-text-secondary">Destination</label>
          <input
            type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            placeholder="e.g. Tokyo"
            disabled={loading}
            className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-brand-blue/30 disabled:opacity-50"
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-text-secondary">Trip length (days)</label>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setTotalDays((d) => Math.max(1, d - 1))}
              disabled={loading || totalDays <= 1}
              className="h-9 w-9 shrink-0 rounded-lg border border-border bg-surface text-text-primary hover:bg-muted disabled:opacity-40 transition-colors text-lg leading-none"
            >
              −
            </button>
            <span className="flex-1 text-center text-sm font-medium tabular-nums text-text-primary">{totalDays}</span>
            <button
              type="button"
              onClick={() => setTotalDays((d) => Math.min(30, d + 1))}
              disabled={loading || totalDays >= 30}
              className="h-9 w-9 shrink-0 rounded-lg border border-border bg-surface text-text-primary hover:bg-muted disabled:opacity-40 transition-colors text-lg leading-none"
            >
              +
            </button>
          </div>
        </div>
      </div>

      {/* Budget */}
      <ChipGroup
        label="Budget"
        options={BUDGET_OPTIONS}
        selected={budget ? [budget] : []}
        onToggle={(v) => setBudget((prev) => (prev === v ? "" : v))}
        disabled={loading}
      />

      {/* Travel style */}
      <ChipGroup
        label="Travel style"
        options={TRAVEL_STYLE_OPTIONS}
        selected={travelStyle ? [travelStyle] : []}
        onToggle={(v) => setTravelStyle((prev) => (prev === v ? "" : v))}
        disabled={loading}
      />

      {/* Interests */}
      <ChipGroup
        label="Interests"
        options={INTEREST_OPTIONS}
        selected={interests}
        onToggle={(v) => toggleMulti(v, interests, setInterests)}
        disabled={loading}
        multi
      />

      {/* Constraints */}
      <ChipGroup
        label="Constraints"
        options={CONSTRAINT_OPTIONS}
        selected={constraints}
        onToggle={(v) => toggleMulti(v, constraints, setConstraints)}
        disabled={loading}
        multi
      />

      {/* Travel party */}
      <ChipGroup
        label="Traveling with"
        options={TRAVEL_PARTY_OPTIONS}
        selected={travelParty ? [travelParty] : []}
        onToggle={(v) => setTravelParty((prev) => (prev === v ? "" : v))}
        disabled={loading}
      />

      {error && (
        <p className="text-sm text-danger" role="alert">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={!canSubmit}
        className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-brand-blue px-5 py-3 text-sm font-medium text-white transition-opacity hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-blue disabled:pointer-events-none disabled:opacity-50"
      >
        {loading && (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        )}
        {loading ? "Planning..." : "Generate Itinerary"}
      </button>
    </form>
  );
}

interface ChipGroupProps {
  label: string;
  options: readonly string[];
  selected: string[];
  onToggle: (value: string) => void;
  disabled?: boolean;
  multi?: boolean;
}

function ChipGroup({ label, options, selected, onToggle, disabled, multi }: ChipGroupProps) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-text-secondary">
        {label}
        {multi && <span className="ml-1 text-text-muted font-normal">(pick any)</span>}
      </label>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => {
          const active = selected.includes(opt);
          return (
            <button
              key={opt}
              type="button"
              onClick={() => onToggle(opt)}
              disabled={disabled}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors disabled:opacity-50 ${
                active
                  ? "bg-brand-blue text-white border-brand-blue"
                  : "bg-surface text-text-primary border-border hover:border-brand-blue/50 hover:bg-blue-50/50"
              }`}
            >
              {opt}
            </button>
          );
        })}
      </div>
    </div>
  );
}
