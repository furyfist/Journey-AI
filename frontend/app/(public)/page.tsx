"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "@/components/shared/Navbar";
import PageWrapper from "@/components/shared/PageWrapper";
import PromptInput from "@/components/landing/PromptInput";
import ExampleChips from "@/components/landing/ExampleChips";
import HowItWorks from "@/components/landing/HowItWorks";
import { createTrip } from "@/lib/api/trips";
import { useGenerateStore } from "@/store/generate";

export default function Home() {
  const router = useRouter();
  const setPrompt = useGenerateStore((s) => s.setPrompt);

  const [prompt, setLocalPrompt] = useState("");

  function handlePromptChange(v: string) {
    setLocalPrompt(v);
    if (error) setError(null);
  }
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(value: string) {
    setError(null);
    setLoading(true);
    try {
      const trip = await createTrip({ prompt: value });
      setPrompt(value);
      router.push(`/generate/${trip.id}`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  function handleExampleSelect(example: string) {
    setLocalPrompt(example);
    if (error) setError(null);
  }

  return (
    <>
      <Navbar />
      <PageWrapper>
        <div className="mx-auto max-w-2xl py-16 sm:py-24">
          <div className="mb-10 text-center">
            <h1 className="text-4xl font-semibold tracking-tight text-text-primary sm:text-5xl">
              Plan your next trip
            </h1>
            <p className="mt-3 text-lg text-text-secondary">
              Describe where you want to go. AI builds a full itinerary in seconds.
            </p>
          </div>

          <div className="space-y-4">
            <PromptInput
              value={prompt}
              onChange={handlePromptChange}
              onSubmit={handleSubmit}
              loading={loading}
              error={error}
            />

            <ExampleChips onSelect={handleExampleSelect} />
          </div>

          <div className="mt-16">
            <HowItWorks />
          </div>
        </div>
      </PageWrapper>
    </>
  );
}
