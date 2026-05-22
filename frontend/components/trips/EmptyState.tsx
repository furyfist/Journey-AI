import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <h2 className="text-xl font-semibold text-text-primary mb-2">
        No trips yet
      </h2>
      <p className="text-sm text-text-muted mb-6">
        Plan your first trip and it will appear here.
      </p>
      <Link href="/" className={cn(buttonVariants())}>
        Plan a trip
      </Link>
    </div>
  );
}
