import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2">
        No trips yet
      </h2>
      <p className="text-sm text-[var(--text-muted)] mb-6">
        Plan your first trip and it will appear here.
      </p>
      <Button asChild>
        <Link href="/">Plan a trip</Link>
      </Button>
    </div>
  );
}
