import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 px-4 text-center">
      <p className="text-sm text-text-secondary">This page does not exist.</p>
      <Link
        href="/"
        className="text-sm font-medium text-accent-sage underline underline-offset-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
      >
        Go home
      </Link>
    </div>
  );
}
