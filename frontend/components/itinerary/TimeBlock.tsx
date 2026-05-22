import type { TimeBlock as TimeBlockType } from "@/lib/types/trip";
import ActivityCard from "./ActivityCard";

interface TimeBlockProps {
  block: TimeBlockType;
}

export default function TimeBlock({ block }: TimeBlockProps) {
  const label = block.label.charAt(0).toUpperCase() + block.label.slice(1);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-baseline gap-2">
        <h4 className="font-medium text-[var(--text-primary)]">{label}</h4>
        <span className="text-sm text-[var(--text-muted)]">
          {block.start_time} – {block.end_time}
        </span>
      </div>
      {block.block_summary && (
        <p className="text-sm text-[var(--text-secondary)]">{block.block_summary}</p>
      )}
      <div className="flex flex-col gap-3">
        {block.activities.map((activity, i) => (
          <ActivityCard key={i} activity={activity} />
        ))}
      </div>
    </div>
  );
}
