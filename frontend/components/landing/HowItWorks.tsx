const STEPS = [
  { n: 1, heading: "Describe your trip", body: "Tell us where you want to go, for how long, and what matters most to you." },
  { n: 2, heading: "AI builds your itinerary", body: "Multiple AI agents research destinations, plan your days, and check for conflicts." },
  { n: 3, heading: "Refine and regenerate", body: "Not happy with a day or a time block? Regenerate just that part with a constraint." },
];

export default function HowItWorks() {
  return (
    <section className="w-full">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-muted">
        How it works
      </h2>
      <ol className="space-y-4">
        {STEPS.map(({ n, heading, body }) => (
          <li key={n} className="flex gap-4">
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent-light text-sm font-semibold text-primary">
              {n}
            </span>
            <div>
              <p className="font-medium text-text-primary">{heading}</p>
              <p className="mt-0.5 text-sm text-text-secondary">{body}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
