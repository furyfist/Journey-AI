import { Map } from "lucide-react";
import PageWrapper from "@/components/shared/PageWrapper";

const PANELS = [
  {
    city: "Tokyo, Japan",
    weather: "☀️ 22°C",
    activities: [
      { time: "9:00 AM", name: "Tsukiji Outer Market", tag: "Food", tagColor: "bg-orange-50 text-orange-600" },
      { time: "11:30 AM", name: "teamLab Borderless", tag: "Art", tagColor: "bg-purple-50 text-purple-600" },
      { time: "2:00 PM", name: "Senso-ji Temple", tag: "Culture", tagColor: "bg-blue-50 text-blue-600" },
    ],
  },
  {
    city: "Shibuya & Harajuku",
    weather: "🌤 20°C",
    activities: [
      { time: "10:00 AM", name: "Shibuya Crossing", tag: "Landmark", tagColor: "bg-blue-50 text-blue-600" },
      { time: "12:30 PM", name: "Takeshita Street", tag: "Shopping", tagColor: "bg-pink-50 text-pink-600" },
      { time: "3:00 PM", name: "Yoyogi Park", tag: "Outdoors", tagColor: "bg-green-50 text-green-600" },
    ],
  },
];

export default function DestinationsShowcase() {
  return (
    <section id="explore" className="py-20 sm:py-24 bg-muted/40">
      <PageWrapper>
        <div className="text-center mb-12">
          <p className="text-xs font-semibold uppercase tracking-widest text-text-muted mb-3">Live example</p>
          <h2 className="text-3xl sm:text-4xl font-semibold text-text-primary tracking-tight">
            See What a Real Trip Looks Like
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {PANELS.map(({ city, weather, activities }) => (
            <div key={city} className="bg-surface border border-border rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-border">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-text-primary">{city}</span>
                  <span className="text-sm text-text-secondary">{weather}</span>
                </div>
              </div>

              <div className="px-5 py-3 space-y-3">
                {activities.map(({ time, name, tag, tagColor }) => (
                  <div key={time} className="flex items-center gap-3">
                    <span className="text-xs text-text-muted w-[72px] shrink-0">{time}</span>
                    <div className="h-4 w-4 rounded-full bg-muted shrink-0" />
                    <span className="text-sm text-text-primary flex-1 min-w-0 truncate">{name}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 font-medium ${tagColor}`}>
                      {tag}
                    </span>
                  </div>
                ))}
              </div>

              <div className="px-5 pb-5 pt-2">
                <div className="w-full aspect-video bg-muted rounded-xl" />
              </div>
            </div>
          ))}
        </div>

        {/* Map placeholder */}
        <div className="relative w-full rounded-2xl bg-muted aspect-[16/5] flex items-center justify-center">
          <div className="flex flex-col items-center gap-2 text-text-muted">
            <Map size={32} />
            <p className="text-sm">Interactive map — coming soon</p>
          </div>
        </div>
      </PageWrapper>
    </section>
  );
}
