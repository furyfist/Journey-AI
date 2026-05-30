"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Sparkles, PlayCircle } from "lucide-react";
import PageWrapper from "@/components/shared/PageWrapper";
import VideoModal from "@/components/shared/VideoModal";
import PromptInput from "@/components/landing/PromptInput";
import ExampleChips from "@/components/landing/ExampleChips";
import TripDetailsForm from "@/components/landing/TripDetailsForm";
import { createTrip } from "@/lib/api/trips";
import { useGenerateStore } from "@/store/generate";
import type { TripCreate } from "@/lib/types/trip";
import { useDestinationPhoto } from "@/hooks/useDestinationPhoto";

const DEMO_ACTIVITIES = [
  { time: "9:00 AM", name: "Tsukiji Outer Market", tag: "Food", tagColor: "bg-orange-50 text-orange-600" },
  { time: "11:30 AM", name: "teamLab Borderless", tag: "Art", tagColor: "bg-purple-50 text-purple-600" },
  { time: "2:00 PM", name: "Senso-ji Temple", tag: "Culture", tagColor: "bg-blue-50 text-blue-600" },
];

type Step = "prompt" | "details";

// Three distinct Tokyo scenes for the hero demo card
const DEMO_PHOTO_QUERIES = [
  "Senso-ji Temple Tokyo",
  "Shibuya crossing night",
  "Mount Fuji Japan",
] as const;

function DemoPhoto({ query }: { query: string }) {
  const { photo, status } = useDestinationPhoto(query);

  if (status === "loading") {
    return (
      <div className="flex-1 aspect-video bg-muted rounded-lg overflow-hidden relative">
        <div className="absolute inset-0 -translate-x-full animate-[shimmer_1.4s_infinite] bg-gradient-to-r from-transparent via-white/30 to-transparent" />
      </div>
    );
  }

  if (status === "error" || !photo || photo.source === "fallback" || !photo.image_url) {
    return <div className="flex-1 aspect-video bg-muted rounded-lg" />;
  }

  return (
    <div className="flex-1 aspect-video rounded-lg overflow-hidden relative">
      <Image
        src={photo.image_url}
        alt={photo.alt_text ?? query}
        fill
        sizes="(max-width: 1024px) 33vw, 200px"
        className="object-cover"
      />
    </div>
  );
}

export default function HeroSection() {
  const router = useRouter();
  const setStorePrompt = useGenerateStore((s) => s.setPrompt);
  const [showModal, setShowModal] = useState(false);
  const [step, setStep] = useState<Step>("prompt");
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handlePromptChange(v: string) {
    setPrompt(v);
    if (error) setError(null);
  }

  function handlePromptSubmit(value: string) {
    setPrompt(value);
    setError(null);
    setStep("details");
  }

  async function handleDetailsSubmit(payload: TripCreate) {
    setError(null);
    setLoading(true);
    try {
      const trip = await createTrip(payload);
      setStorePrompt(payload.prompt);
      router.push(`/generate/${trip.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleExampleSelect(example: string) {
    setPrompt(example);
    if (error) setError(null);
  }

  return (
    <>
      <section className="py-16 sm:py-20 overflow-hidden">
        <PageWrapper>
          {/* Two-column hero */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center min-h-[55vh]">
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
              <div className="relative bg-surface shadow-xl rounded-2xl border border-border overflow-hidden">
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

                <div className="px-6 py-4 flex gap-3">
                  {DEMO_PHOTO_QUERIES.map((q) => (
                    <DemoPhoto key={q} query={q} />
                  ))}
                </div>

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

          {/* Prompt input / details form — scroll target for all CTAs */}
          <div id="prompt" className="mt-16 max-w-2xl mx-auto">
            <p className="text-center text-sm text-text-muted mb-4">
              {step === "prompt" ? "Where do you want to go?" : "Almost there — a few more details"}
            </p>
            <div className="bg-surface shadow-xl rounded-2xl border border-border p-6">
              {step === "prompt" ? (
                <>
                  <PromptInput
                    value={prompt}
                    onChange={handlePromptChange}
                    onSubmit={handlePromptSubmit}
                    loading={loading}
                    error={error}
                  />
                  <div className="mt-3">
                    <ExampleChips onSelect={handleExampleSelect} />
                  </div>
                </>
              ) : (
                <TripDetailsForm
                  prompt={prompt}
                  onBack={() => { setStep("prompt"); setError(null); }}
                  onSubmit={handleDetailsSubmit}
                  loading={loading}
                  error={error}
                />
              )}
            </div>
          </div>
        </PageWrapper>
      </section>

      {showModal && <VideoModal onClose={() => setShowModal(false)} />}
    </>
  );
}
