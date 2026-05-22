import { cn } from "@/lib/utils";

interface BadgeProps {
  variant: "persona" | "budget";
  children: React.ReactNode;
  className?: string;
}

export default function Badge({ variant, children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        variant === "persona" && "bg-accent-light text-accent-sage",
        variant === "budget" && "bg-neutral-100 text-text-secondary",
        className
      )}
    >
      {children}
    </span>
  );
}
