import { Globe, Wallet, Users, User, Utensils, Landmark } from "lucide-react";
import PageWrapper from "@/components/shared/PageWrapper";

const FEATURES = [
  {
    icon: Globe,
    title: "International Wanderer",
    description: "Multi-country routes, visa tips, and timezone handling built right in.",
  },
  {
    icon: Wallet,
    title: "Budget Planner",
    description: "Set a budget and AI picks stays and activities that fit without compromise.",
  },
  {
    icon: Users,
    title: "Family Trips",
    description: "Age-appropriate activities, stroller-friendly routes, and family pacing.",
  },
  {
    icon: User,
    title: "Solo Explorer",
    description: "Safe neighborhoods, solo-friendly experiences, and flexible schedules.",
  },
  {
    icon: Utensils,
    title: "Foodie Traveler",
    description: "Restaurants, markets, and food tours woven naturally into your days.",
  },
  {
    icon: Landmark,
    title: "Cultural Explorer",
    description: "Museums, heritage sites, and local festivals prioritized across your trip.",
  },
];

export default function FeaturesGrid() {
  return (
    <section id="features" className="py-20 sm:py-24">
      <PageWrapper>
        <div className="text-center mb-12">
          <p className="text-xs font-semibold uppercase tracking-widest text-text-muted mb-3">For every traveler</p>
          <h2 className="text-3xl sm:text-4xl font-semibold text-text-primary tracking-tight mb-4">
            Built Around You
          </h2>
          <p className="text-text-secondary max-w-xl mx-auto">
            Whatever kind of traveler you are, Journey AI adapts to your style, pace, and preferences.
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="bg-surface border border-border rounded-xl p-5 hover:shadow-md hover:border-brand-blue/30 transition-all group"
            >
              <div className="h-10 w-10 rounded-xl bg-accent-light flex items-center justify-center mb-4 group-hover:bg-blue-50 transition-colors">
                <Icon size={20} className="text-accent-sage group-hover:text-brand-blue transition-colors" />
              </div>
              <h3 className="font-semibold text-text-primary text-sm mb-1.5">{title}</h3>
              <p className="text-xs text-text-secondary leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </PageWrapper>
    </section>
  );
}
