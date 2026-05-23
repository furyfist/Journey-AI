import { MapPin, Sparkles, PlaneTakeoff } from "lucide-react";
import PageWrapper from "@/components/shared/PageWrapper";

const STEPS = [
  {
    icon: MapPin,
    step: "01",
    title: "Tell your destination",
    description: "Where you want to go, how long, and what matters most — food, culture, adventure, or all of it.",
  },
  {
    icon: Sparkles,
    step: "02",
    title: "AI builds your itinerary",
    description: "Multiple agents research destinations, plan your days, and check for conflicts — in seconds.",
  },
  {
    icon: PlaneTakeoff,
    step: "03",
    title: "Travel stress-free",
    description: "Refine any day or block, regenerate just that part, and set off with a plan that fits perfectly.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 sm:py-24 bg-muted/40">
      <PageWrapper>
        <div className="text-center mb-14">
          <p className="text-xs font-semibold uppercase tracking-widest text-text-muted mb-3">The Process</p>
          <h2 className="text-3xl sm:text-4xl font-semibold text-text-primary tracking-tight">
            How Journey AI Works
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {STEPS.map(({ icon: Icon, step, title, description }) => (
            <div key={step} className="flex flex-col items-center text-center gap-4">
              <div className="relative">
                <div className="h-14 w-14 rounded-2xl bg-accent-light flex items-center justify-center">
                  <Icon size={24} className="text-accent-sage" />
                </div>
                <span className="absolute -top-2 -right-2 h-5 w-5 rounded-full bg-brand-blue flex items-center justify-center text-white text-[10px] font-bold">
                  {step.slice(1)}
                </span>
              </div>
              <div className="space-y-2">
                <h3 className="font-semibold text-text-primary text-lg">{title}</h3>
                <p className="text-sm text-text-secondary leading-relaxed max-w-xs mx-auto">{description}</p>
              </div>
            </div>
          ))}
        </div>
      </PageWrapper>
    </section>
  );
}
