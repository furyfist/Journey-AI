import type { TimeBlock as TimeBlockType } from "@/lib/types/trip";
import type { TripDetail } from "@/lib/types/trip";
import ActivityCard from "./ActivityCard";
import RegenerateControl from "./RegenerateControl";

interface TimeBlockProps {
  block: TimeBlockType;
  tripId: string;
  dayNumber: number;
  onSuccess: (updated: TripDetail) => void;
}

export default function TimeBlock({
  block,
  tripId,
  dayNumber,
  onSuccess,
}: TimeBlockProps) {
  const label = block.label.charAt(0).toUpperCase() + block.label.slice(1);

  return (
    <div className="relative flex flex-col gap-3">
      <div className="flex items-baseline gap-2">
        <h4 className="font-medium text-text-primary">{label}</h4>
        <span className="text-sm text-text-muted">
          {block.start_time} – {block.end_time}
        </span>
      </div>
      {block.block_summary && (
        <p className="text-sm text-text-secondary">{block.block_summary}</p>
      )}
      <div className="flex flex-col gap-3">
        {block.activities.map((activity, i) => (
          <ActivityCard key={i} activity={activity} />
        ))}
      </div>
      <RegenerateControl
        tripId={tripId}
        scope="single_block"
        dayNumber={dayNumber}
        blockLabel={block.label}
        onSuccess={onSuccess}
      />
    </div>
  );
}
