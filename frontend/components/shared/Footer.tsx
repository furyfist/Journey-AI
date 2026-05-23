import Link from "next/link";
import { Send, Camera, Code2 } from "lucide-react";
import PageWrapper from "./PageWrapper";

const LINKS = [
  {
    heading: "Product",
    items: ["Features", "How It Works", "Pricing", "Changelog"],
  },
  {
    heading: "Company",
    items: ["About", "Blog", "Careers", "Press"],
  },
  {
    heading: "Resources",
    items: ["Docs", "API", "Status", "Community"],
  },
  {
    heading: "Legal",
    items: ["Privacy", "Terms", "Cookies"],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-border bg-surface">
      <PageWrapper>
        <div className="py-12 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-8">
          {/* Brand column */}
          <div className="col-span-2 sm:col-span-3 lg:col-span-2 space-y-3">
            <Link
              href="/"
              className="text-lg font-semibold text-text-primary tracking-tight focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
            >
              Journey AI
            </Link>
            <p className="text-sm text-text-muted max-w-xs">
              AI-powered travel, built for curious minds.
            </p>
          </div>

          {/* Link columns */}
          {LINKS.map(({ heading, items }) => (
            <div key={heading} className="space-y-3">
              <p className="text-xs font-semibold uppercase tracking-wider text-text-primary">{heading}</p>
              <ul className="space-y-2">
                {items.map((item) => (
                  <li key={item}>
                    <a
                      href="#"
                      className="text-sm text-text-muted hover:text-text-primary transition-colors"
                    >
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom row */}
        <div className="border-t border-border py-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-text-muted">
            © 2025 Journey AI. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <a href="#" className="text-text-muted hover:text-text-primary transition-colors" aria-label="Twitter">
              <Send size={18} />
            </a>
            <a href="#" className="text-text-muted hover:text-text-primary transition-colors" aria-label="Instagram">
              <Camera size={18} />
            </a>
            <a href="#" className="text-text-muted hover:text-text-primary transition-colors" aria-label="GitHub">
              <Code2 size={18} />
            </a>
          </div>
        </div>
      </PageWrapper>
    </footer>
  );
}
