import type { Activity } from "@/lib/types/trip";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";

const CATEGORY_EMOJI: Record<string, string> = {
  food: "🍽",
  attraction: "🏛",
  transport: "🚌",
  shopping: "🛍",
  nature: "🌿",
  culture: "🎭",
  nightlife: "🌙",
};

function formatDuration(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h === 0) return `${m}m`;
  if (m === 0) return `${h}h`;
  return `${h}h ${m}m`;
}

interface ActivityCardProps {
  activity: Activity;
}

export default function ActivityCard({ activity }: ActivityCardProps) {
  const emoji = CATEGORY_EMOJI[activity.category] ?? "📍";

  return (
    <div className="bg-surface border border-border rounded-lg p-4 flex flex-col gap-2">
      <div className="flex items-start gap-3">
        <span className="text-xl leading-none mt-0.5">{emoji}</span>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-text-primary leading-snug">{activity.name}</p>
          <p className="text-sm text-text-muted mt-0.5">{activity.location}</p>
          <div className="flex items-center gap-3 mt-1 text-sm text-text-secondary">
            <span>{formatDuration(activity.duration_minutes)}</span>
            {activity.cost_estimate && (
              <>
                <span className="text-border">·</span>
                <span>{activity.cost_estimate}</span>
              </>
            )}
          </div>
        </div>
      </div>

      <p className="text-sm text-text-secondary leading-relaxed">{activity.description}</p>

      <Accordion>
        <AccordionItem value="why-this" className="border-0">
          <AccordionTrigger className="text-xs text-text-muted font-normal hover:no-underline py-1">
            Why This?
          </AccordionTrigger>
          <AccordionContent className="text-sm text-text-secondary">
            {activity.reasoning}
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
