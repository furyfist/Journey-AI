import type { Conflict } from "@/lib/types/trip";

interface ConflictBannerProps {
  conflict: Conflict;
}

export default function ConflictBanner({ conflict }: ConflictBannerProps) {
  const isError = conflict.severity === "error";

  return (
    <div
      role="alert"
      className={`flex items-start gap-3 rounded-lg border-l-4 px-4 py-3 ${
        isError ? "border-danger bg-red-50" : "border-warning bg-amber-50"
      }`}
    >
      <span className="mt-0.5 text-base leading-none">
        {isError ? "✕" : "⚠"}
      </span>
      <div>
        <p className="mb-0.5 text-xs font-semibold uppercase tracking-wide text-text-secondary">
          {conflict.type.replace(/_/g, " ")}
        </p>
        <p className="text-sm text-text-primary">{conflict.description}</p>
      </div>
    </div>
  );
}
