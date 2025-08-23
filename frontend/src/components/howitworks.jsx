import React from 'react';

// A reusable Step component for our diagram
const FlowStep = ({ icon, title, description }) => (
  <div className="flex flex-col items-center text-center p-4">
    <div className="flex items-center justify-center h-16 w-16 bg-soft-green/20 rounded-full">
      {icon}
    </div>
    <h3 className="mt-4 text-lg font-bold text-teal-heading">{title}</h3>
    <p className="mt-2 text-sm text-subtext-gray max-w-xs">{description}</p>
  </div>
);

// The main component for the diagram
const HowItWorks = () => {
  return (
    <section className="bg-cream py-16 sm:py-20">
      <div className="container mx-auto px-6 text-center">
        <h2 className="text-3xl font-bold text-teal-heading">Your Journey in 4 Simple Steps</h2>
        <p className="mt-2 text-subtext-gray">See how our AI crafts your perfect trip from a single idea.</p>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-4">
          <FlowStep
            icon={<IconClipboardList />}
            title="1. Share Your Dream"
            description="Tell us your destination, budget, and travel style in a simple prompt."
          />
          <FlowStep
            icon={<IconMapPin />}
            title="2. Pick a Location"
            description="Our AI researches and suggests 3 perfect, personalized destinations for you to choose from."
          />
          <FlowStep
            icon={<IconPlaneHotel />}
            title="3. Confirm the Details"
            description="Select your preferred hotels and flights from a curated list that fits your budget."
          />
          <FlowStep
            icon={<IconDocumentDownload />}
            title="4. Get Your Itinerary"
            description="Receive a complete, day-by-day travel plan, ready for your adventure and sent to your email."
          />
        </div>
      </div>
    </section>
  );
};

// --- SVG Icons (included for simplicity) ---

const IconClipboardList = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-soft-green" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
  </svg>
);

const IconMapPin = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-soft-green" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const IconPlaneHotel = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-soft-green" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l2-2m0 0l2-2m-2 2L12 10l-2 2m2 2l-2 2" />
  </svg>
);

const IconDocumentDownload = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-soft-green" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

export default HowItWorks;