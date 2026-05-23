import Navbar from "@/components/shared/Navbar";
import Footer from "@/components/shared/Footer";
import HeroSection from "@/components/landing/HeroSection";
import HowItWorks from "@/components/landing/HowItWorks";
import FeaturesGrid from "@/components/landing/FeaturesGrid";
import DestinationsShowcase from "@/components/landing/DestinationsShowcase";
import Testimonials from "@/components/landing/Testimonials";
import CTABanner from "@/components/landing/CTABanner";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <HeroSection />
        <HowItWorks />
        <FeaturesGrid />
        <DestinationsShowcase />
        <Testimonials />
        <CTABanner />
      </main>
      <Footer />
    </>
  );
}
