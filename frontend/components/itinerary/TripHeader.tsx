import type { TripDetail, ItinerarySchema } from "@/lib/types/trip";
import Badge from "@/components/shared/Badge";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";

interface TripHeaderProps {
  trip: TripDetail;
  itinerary: ItinerarySchema;
}

export default function TripHeader({ itinerary }: TripHeaderProps) {
  return (
    <div className="flex flex-col gap-4 py-8 border-b border-border">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold text-text-primary leading-tight">
          {itinerary.title}
        </h1>
        <p className="text-lg text-text-secondary">{itinerary.destination}</p>
        <p className="text-sm text-text-muted">
          {itinerary.total_days} {itinerary.total_days === 1 ? "day" : "days"}
        </p>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        {itinerary.persona && (
          <Badge variant="persona">{itinerary.persona}</Badge>
        )}
        {itinerary.budget_level && (
          <Badge variant="budget">{itinerary.budget_level}</Badge>
        )}
      </div>

      {itinerary.summary && (
        <p className="text-text-secondary leading-relaxed max-w-2xl">
          {itinerary.summary}
        </p>
      )}

      {itinerary.tips && itinerary.tips.length > 0 && (
        <Accordion className="max-w-2xl">
          <AccordionItem value="tips">
            <AccordionTrigger className="text-sm font-medium text-text-primary">
              Travel Tips ({itinerary.tips.length})
            </AccordionTrigger>
            <AccordionContent>
              <ul className="flex flex-col gap-2 pt-1">
                {itinerary.tips.map((tip, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                    <span className="text-accent-sage mt-0.5 shrink-0">·</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      )}
    </div>
  );
}
