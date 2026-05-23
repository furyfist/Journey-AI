"use client";

import { useState } from "react";
import { Sparkles, PlayCircle } from "lucide-react";
import PageWrapper from "@/components/shared/PageWrapper";
import VideoModal from "@/components/shared/VideoModal";

const DEMO_ACTIVITIES = [
  { time: "9:00 AM", name: "Tsukiji Outer Market", tag: "Food", tagColor: "bg-orange-50 text-orange-600" },
  { time: "11:30 AM", name: "teamLab Borderless", tag: "Art", tagColor: "bg-purple-50 text-purple-600" },
  { time: "2:00 PM", name: "Senso-ji Temple", tag: "Culture", tagColor: "bg-blue-50 text-blue-600" },
];

export default function HeroSection() {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <section className="min-h-[85vh] flex items-center py-16 sm:py-20 overflow-hidden">
        <PageWrapper>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            {/* Left column */}
            <div className="space-y-7">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-brand-blue/30 bg-blue-50 text-brand-blue text-xs font-medium">
                <Sparkles size={12} />
                Powered by AI
              </div>

              <div className="space-y-4">
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight text-text-primary leading-[1.1]">
                  Your AI Travel{" "}
                  <span className="text-brand-blue">Companion</span>
                </h1>
                <p className="text-lg text-text-secondary max-w-md leading-relaxed">
                  Tell us where you want to go. Our AI builds a personalized day-by-day itinerary in seconds — then refine it however you like.
                </p>
              </div>

              <div className="flex items-center gap-3 flex-wrap">
                <a
                  href="#prompt"
                  className="inline-flex items-center gap-2 px-6 py-3 text-sm font-medium text-white bg-brand-blue hover:bg-brand-blue-dark rounded-xl transition-colors shadow-sm"
                >
                  Start Planning
                </a>
                <button
                  onClick={() => setShowModal(true)}
                  className="inline-flex items-center gap-2 px-6 py-3 text-sm font-medium text-text-primary border border-border rounded-xl hover:bg-muted transition-colors"
                >
                  <PlayCircle size={16} />
                  Watch Demo
                </button>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex -space-x-2">
                  {[
                    { initials: "SJ", bg: "bg-indigo-500" },
                    { initials: "MK", bg: "bg-emerald-500" },
                    { initials: "PR", bg: "bg-amber-500" },
                  ].map(({ initials, bg }) => (
                    <div
                      key={initials}
                      className={`h-8 w-8 rounded-full ${bg} flex items-center justify-center text-white text-xs font-semibold ring-2 ring-white`}
                    >
                      {initials}
                    </div>
                  ))}
                </div>
                <p className="text-sm text-text-secondary">
                  <span className="text-amber-400">★★★★★</span>{" "}
                  Trusted by travelers worldwide
                </p>
              </div>
            </div>

            {/* Right column — demo trip preview card */}
            <div className="relative">
              <div className="absolute -inset-6 bg-blue-50/40 rounded-3xl blur-sm" />
              <div id="prompt" className="relative bg-surface shadow-xl rounded-2xl border border-border overflow-hidden">
                {/* Card header */}
                <div className="px-6 pt-5 pb-4 border-b border-border">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-text-primary">Your Trip to Tokyo</span>
                    <span className="px-2.5 py-1 text-xs bg-blue-50 text-brand-blue rounded-full border border-brand-blue/20 font-medium">
                      5 days
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-1 text-sm text-text-secondary">
                    <span>☀️ 22°C</span>
                    <span className="text-border">·</span>
                    <span>Japan</span>
                  </div>
                </div>

                {/* Image thumbnails */}
                <div className="px-6 py-4 flex gap-3">
                  <div className="flex-1 aspect-video bg-muted rounded-lg" />
                  <div className="flex-1 aspect-video bg-muted rounded-lg" />
                  <div className="flex-1 aspect-video bg-muted rounded-lg" />
                </div>

                {/* Activities */}
                <div className="px-6 pb-4 space-y-2.5">
                  {DEMO_ACTIVITIES.map(({ time, name, tag, tagColor }) => (
                    <div key={time} className="flex items-center gap-3">
                      <span className="text-xs text-text-muted w-20 shrink-0">{time}</span>
                      <span className="text-sm text-text-primary flex-1 min-w-0 truncate">{name}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 font-medium ${tagColor}`}>
                        {tag}
                      </span>
                    </div>
                  ))}
                </div>

                {/* CTA */}
                <div className="px-6 pb-6">
                  <a
                    href="#prompt"
                    className="block w-full text-center py-2.5 bg-brand-blue hover:bg-brand-blue-dark text-white text-sm font-medium rounded-xl transition-colors"
                  >
                    Plan My Trip →
                  </a>
                </div>
              </div>
            </div>
          </div>
        </PageWrapper>
      </section>

      {showModal && <VideoModal onClose={() => setShowModal(false)} />}
    </>
  );
}
