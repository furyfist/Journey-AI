"use client";

const EXAMPLES = [
  "7 days in Japan — food, culture, and temples, mid-range budget",
  "10-day road trip through Patagonia on a shoestring",
  "Long weekend in Rome: art, history, and excellent pasta",
  "2 weeks backpacking Southeast Asia — beaches and night markets",
  "Family-friendly 5 days in Costa Rica: wildlife and adventure",
];

interface ExampleChipsProps {
  onSelect: (example: string) => void;
}

export default function ExampleChips({ onSelect }: ExampleChipsProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1 scrollbar-none">
      {EXAMPLES.map((ex) => (
        <button
          key={ex}
          type="button"
          onClick={() => onSelect(ex)}
          className="shrink-0 rounded-full border border-border bg-surface px-3 py-1.5 text-xs text-text-secondary whitespace-nowrap transition-colors hover:border-brand-blue hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-blue"
        >
          {ex}
        </button>
      ))}
    </div>
  );
}
