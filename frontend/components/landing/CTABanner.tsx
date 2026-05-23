import { PlaneTakeoff } from "lucide-react";
import PageWrapper from "@/components/shared/PageWrapper";

export default function CTABanner() {
  return (
    <section className="py-24">
      <PageWrapper>
        <div className="bg-gradient-brand rounded-3xl mx-0 sm:mx-2 overflow-hidden relative">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center px-8 sm:px-12 py-12">
            {/* Left */}
            <div className="space-y-6">
              <h2 className="text-3xl sm:text-4xl font-semibold text-white leading-tight tracking-tight">
                Start your next journey with AI
              </h2>
              <p className="text-white/80 text-lg leading-relaxed">
                Join thousands of travelers who plan smarter, explore deeper, and stress less.
              </p>
              <a
                href="#prompt"
                className="inline-flex items-center gap-2 px-6 py-3 bg-white text-brand-blue text-sm font-semibold rounded-xl hover:bg-blue-50 transition-colors shadow-sm"
              >
                Plan My Trip →
              </a>
            </div>

            {/* Right — decorative plane */}
            <div className="hidden md:flex items-center justify-end">
              <PlaneTakeoff
                size={120}
                className="text-white/20 rotate-12"
                strokeWidth={1}
              />
            </div>
          </div>
        </div>
      </PageWrapper>
    </section>
  );
}
