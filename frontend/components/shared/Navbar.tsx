import Link from "next/link";
import PageWrapper from "./PageWrapper";

export default function Navbar() {
  return (
    <header className="border-b border-border bg-surface">
      <PageWrapper>
        <nav className="flex items-center justify-between h-14">
          <Link href="/" className="text-lg font-semibold text-text-primary tracking-tight focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded">
            Journey AI
          </Link>
        </nav>
      </PageWrapper>
    </header>
  );
}
