import type { DayPlan } from "@/lib/types/trip";

interface DayNavProps {
  days: DayPlan[];
  activeDayNumber: number;
  onDaySelect: (dayNumber: number) => void;
}

export default function DayNav({ days, activeDayNumber, onDaySelect }: DayNavProps) {
  return (
    <>
      {/* Desktop — sticky sidebar */}
      <nav className="hidden md:flex flex-col gap-1 sticky top-24 self-start">
        {days.map((day) => {
          const isActive = day.day_number === activeDayNumber;
          return (
            <button
              key={day.day_number}
              onClick={() => onDaySelect(day.day_number)}
              className={`text-left px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-accent-light text-accent-sage font-medium"
                  : "text-text-secondary hover:text-text-primary hover:bg-border"
              }`}
            >
              Day {day.day_number}
            </button>
          );
        })}
      </nav>

      {/* Mobile — horizontal scroll tab bar */}
      <nav
        className="md:hidden sticky top-0 z-10 bg-background border-b border-border overflow-x-auto"
        style={{ scrollbarWidth: "none" }}
      >
        <div className="flex gap-1 px-4 py-2 min-w-max">
          {days.map((day) => {
            const isActive = day.day_number === activeDayNumber;
            return (
              <button
                key={day.day_number}
                onClick={() => onDaySelect(day.day_number)}
                className={`px-4 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
                  isActive
                    ? "bg-accent-sage text-white font-medium"
                    : "text-text-secondary hover:text-text-primary"
                }`}
              >
                Day {day.day_number}
              </button>
            );
          })}
        </div>
      </nav>
    </>
  );
}
