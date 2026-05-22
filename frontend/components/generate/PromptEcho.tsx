"use client";

import { useGenerateStore } from "@/store/generate";

export default function PromptEcho() {
  const prompt = useGenerateStore((s) => s.prompt);

  if (!prompt) return null;

  return (
    <blockquote className="border-l-2 border-[var(--border)] pl-4 py-2 text-sm text-[var(--text-muted)] italic bg-white/50 rounded-r-md">
      {prompt}
    </blockquote>
  );
}
