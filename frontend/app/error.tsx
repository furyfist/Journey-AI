"use client";

import Link from "next/link";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  if (error.digest) console.error("Error digest:", error.digest);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
      <h1 className="text-2xl font-semibold text-text-primary">
        Something went wrong
      </h1>
      <p className="text-sm text-text-secondary">
        An unexpected error occurred. Please try again or go back home.
      </p>
      <div className="flex gap-4">
        <button
          onClick={reset}
          className="text-sm font-medium text-accent-sage underline underline-offset-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
        >
          Try again
        </button>
        <Link
          href="/"
          className="text-sm text-text-secondary hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
        >
          Back to home
        </Link>
      </div>
    </div>
  );
}
