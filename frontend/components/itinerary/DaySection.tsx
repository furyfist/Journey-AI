import type { DayPlan, Conflict } from "@/lib/types/trip";
import WeatherStrip from "./WeatherStrip";
import TimeBlock from "./TimeBlock";

interface DaySectionProps {
  day: DayPlan;
  conflicts: Conflict[];
  sectionRef: React.RefCallback<HTMLDivElement>;
}

export default function DaySection({ day, conflicts, sectionRef }: DaySectionProps) {
  return (
    <div ref={sectionRef} className="flex flex-col gap-6 py-8 border-b border-border last:border-0">
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-accent-light text-accent-sage text-sm font-semibold shrink-0">
            {day.day_number}
          </span>
          <div>
            {day.date && (
              <p className="text-xs text-text-muted uppercase tracking-wide">
                {new Date(day.date).toLocaleDateString("en-GB", {
                  weekday: "short",
                  month: "short",
                  day: "numeric",
                })}
              </p>
            )}
            <h3 className="text-lg font-semibold text-text-primary leading-snug">
              {day.title}
            </h3>
          </div>
        </div>
        {day.weather && <WeatherStrip weather={day.weather} />}
        {day.day_summary && (
          <p className="text-sm text-text-secondary mt-1">{day.day_summary}</p>
        )}
      </div>

      {conflicts.length > 0 && (
        <div className="flex flex-col gap-2">
          {conflicts.map((conflict, i) => (
            <div
              key={i}
              role="alert"
              className={`flex items-start gap-3 rounded-lg px-4 py-3 border-l-4 ${
                conflict.severity === "error"
                  ? "bg-red-50 border-danger"
                  : "bg-amber-50 border-warning"
              }`}
            >
              <span className="text-base leading-none mt-0.5">
                {conflict.severity === "error" ? "✕" : "⚠"}
              </span>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-text-secondary mb-0.5">
                  {conflict.type.replace(/_/g, " ")}
                </p>
                <p className="text-sm text-text-primary">{conflict.description}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-col gap-8">
        <TimeBlock block={day.morning} />
        <TimeBlock block={day.afternoon} />
        <TimeBlock block={day.evening} />
      </div>
    </div>
  );
}
