"use client";

const MAX_CHARS = 2000;

interface PromptInputProps {
  value: string;
  onChange: (v: string) => void;
  onSubmit: (prompt: string) => void;
  loading?: boolean;
  error?: string | null;
}

export default function PromptInput({
  value,
  onChange,
  onSubmit,
  loading = false,
  error,
}: PromptInputProps) {
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
  }

  const remaining = MAX_CHARS - value.length;
  const overLimit = remaining < 0;

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="bg-surface rounded-xl shadow-sm border border-border overflow-hidden">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Describe your ideal trip... e.g. '7 days in Japan focused on food and culture, mid-range budget'"
          rows={5}
          maxLength={MAX_CHARS}
          disabled={loading}
          className="w-full resize-none border-0 bg-transparent px-4 pt-4 pb-2 text-text-primary placeholder:text-text-muted focus:outline-none disabled:opacity-50"
          style={{ fontSize: "16px" }}
        />

        <div className="flex items-center justify-between px-4 py-3 border-t border-border">
          <span
            className={`text-xs tabular-nums ${
              overLimit ? "text-danger" : remaining < 200 ? "text-warning" : "text-text-muted"
            }`}
          >
            {remaining} remaining
          </span>

          <button
            type="submit"
            disabled={loading || !value.trim() || overLimit}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-blue px-5 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-blue disabled:pointer-events-none disabled:opacity-50"
          >
            {loading && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            )}
            {loading ? "Planning..." : "Plan my trip"}
          </button>
        </div>
      </div>

      {error && (
        <p className="mt-2 text-sm text-danger" role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
