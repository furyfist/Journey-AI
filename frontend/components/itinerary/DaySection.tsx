import type { DayPlan, Conflict, TripDetail } from "@/lib/types/trip";
import WeatherStrip from "./WeatherStrip";
import TimeBlock from "./TimeBlock";
import RegenerateControl from "./RegenerateControl";
import ConflictBanner from "./ConflictBanner";

interface DaySectionProps {
  day: DayPlan;
  conflicts: Conflict[];
  sectionRef: React.RefCallback<HTMLDivElement>;
  tripId: string;
  onSuccess: (updated: TripDetail) => void;
}

export default function DaySection({
  day,
  conflicts,
  sectionRef,
  tripId,
  onSuccess,
}: DaySectionProps) {
  return (
    <div
      ref={sectionRef}
      className="relative flex flex-col gap-6 border-b border-border py-8 last:border-0"
    >
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-3">
          <span className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent-light text-sm font-semibold text-accent-sage">
            {day.day_number}
          </span>
          <div>
            {day.date && (
              <p className="text-xs uppercase tracking-wide text-text-muted">
                {new Date(day.date).toLocaleDateString("en-GB", {
                  weekday: "short",
                  month: "short",
                  day: "numeric",
                })}
              </p>
            )}
            <h3 className="text-lg font-semibold leading-snug text-text-primary">
              {day.title}
            </h3>
          </div>
        </div>
        {day.weather && <WeatherStrip weather={day.weather} />}
        {day.day_summary && (
          <p className="mt-1 text-sm text-text-secondary">{day.day_summary}</p>
        )}
      </div>

      {conflicts.length > 0 && (
        <div className="flex flex-col gap-2">
          {conflicts.map((conflict, i) => (
            <ConflictBanner key={i} conflict={conflict} />
          ))}
        </div>
      )}

      <div className="flex flex-col gap-8">
        <TimeBlock
          block={day.morning}
          tripId={tripId}
          dayNumber={day.day_number}
          onSuccess={onSuccess}
        />
        <TimeBlock
          block={day.afternoon}
          tripId={tripId}
          dayNumber={day.day_number}
          onSuccess={onSuccess}
        />
        <TimeBlock
          block={day.evening}
          tripId={tripId}
          dayNumber={day.day_number}
          onSuccess={onSuccess}
        />
      </div>

      <RegenerateControl
        tripId={tripId}
        scope="day"
        dayNumber={day.day_number}
        onSuccess={onSuccess}
      />
    </div>
  );
}
