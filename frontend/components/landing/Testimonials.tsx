import PageWrapper from "@/components/shared/PageWrapper";

const TESTIMONIALS = [
  {
    initials: "S",
    bg: "bg-indigo-500",
    name: "Sarah M.",
    location: "New York, USA",
    quote:
      "Planned my entire Japan trip in 3 minutes. The day-by-day breakdown was better than anything I'd have made myself.",
  },
  {
    initials: "J",
    bg: "bg-emerald-500",
    name: "James K.",
    location: "London, UK",
    quote:
      "The budget planner mode is insane. It found ryokans I never would have discovered on my own.",
  },
  {
    initials: "P",
    bg: "bg-amber-500",
    name: "Priya R.",
    location: "Sydney, AU",
    quote:
      "Used it for a 10-day Southeast Asia trip. Zero conflicts, perfect pacing. I was genuinely impressed.",
  },
];

export default function Testimonials() {
  return (
    <section className="py-20 sm:py-24">
      <PageWrapper>
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-semibold text-text-primary tracking-tight mb-4">
            Loved by Travelers Worldwide
          </h2>
          <div className="flex items-center justify-center gap-2 text-sm text-text-secondary">
            <span className="text-amber-400 text-lg">★★★★★</span>
            <span>4.9/5 from 200+ trips planned</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {TESTIMONIALS.map(({ initials, bg, name, location, quote }) => (
            <div key={name} className="bg-surface border border-border rounded-xl p-6 flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div
                  className={`h-10 w-10 rounded-full ${bg} flex items-center justify-center text-white text-sm font-semibold shrink-0`}
                >
                  {initials}
                </div>
                <div>
                  <p className="font-semibold text-text-primary text-sm">{name}</p>
                  <p className="text-xs text-text-muted">{location}</p>
                </div>
              </div>
              <div className="flex gap-0.5">
                {Array.from({ length: 5 }).map((_, i) => (
                  <span key={i} className="text-amber-400 text-sm">★</span>
                ))}
              </div>
              <p className="text-sm text-text-secondary italic leading-relaxed">&ldquo;{quote}&rdquo;</p>
            </div>
          ))}
        </div>
      </PageWrapper>
    </section>
  );
}
