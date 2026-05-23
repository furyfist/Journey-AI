import Link from "next/link";
import PageWrapper from "./PageWrapper";

export default function Navbar() {
  return (
    <header className="border-b border-border bg-surface sticky top-0 z-40">
      <PageWrapper>
        <nav className="flex items-center justify-between h-14">
          <Link
            href="/"
            className="text-lg font-semibold text-text-primary tracking-tight focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
          >
            Journey AI
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-text-secondary hover:text-text-primary transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="text-sm text-text-secondary hover:text-text-primary transition-colors">
              Pricing
            </a>
            <a href="#explore" className="text-sm text-text-secondary hover:text-text-primary transition-colors">
              About
            </a>
          </div>

          <div className="flex items-center gap-2">
            <a
              href="#prompt"
              className="px-4 py-2 text-sm text-text-secondary hover:text-text-primary transition-colors"
            >
              Sign in
            </a>
            <a
              href="#prompt"
              className="px-4 py-2 text-sm font-medium text-white bg-brand-blue hover:bg-brand-blue-dark rounded-lg transition-colors"
            >
              Sign Up
            </a>
          </div>
        </nav>
      </PageWrapper>
    </header>
  );
}
