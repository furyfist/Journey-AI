import React from 'react';
import { motion } from 'framer-motion';

// A reusable Step component with animations
const FlowStep = ({ icon, title, description, index }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ 
      opacity: 1, 
      y: 0,
      transition: { delay: index * 0.2, duration: 0.5 }
    }}
    whileHover={{ 
      scale: 1.05,
      transition: { duration: 0.2 }
    }}
    className="flex flex-col items-center text-center p-6 bg-cream-50/90 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-shadow"
  >
    <motion.div 
      whileHover={{ rotate: 360 }}
      transition={{ duration: 0.5 }}
      className="flex items-center justify-center h-16 w-16 bg-sage-100 rounded-full"
    >
      {icon}
    </motion.div>
    <h3 className="mt-4 text-lg font-bold text-sage-700">{title}</h3>
    <p className="mt-2 text-sm text-sage-600 max-w-xs">{description}</p>
  </motion.div>
);

// The main component for the diagram
const HowItWorks = () => {
  return (
    <section className="relative bg-cream-50 py-16 sm:py-20 pattern-grid overflow-hidden">
      {/* Add decorative blobs in background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute w-[500px] h-[500px] bg-sage-100/30 rounded-full blur-3xl -right-64 top-0"/>
        <div className="absolute w-[500px] h-[500px] bg-cream-200/50 rounded-full blur-3xl -left-64 bottom-0"/>
      </div>

      <div className="container mx-auto px-6 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl font-bold text-neutral-900">Your Journey in 4 Simple Steps</h2>
          <p className="mt-2 text-neutral-600">See how our AI crafts your perfect trip from a single idea.</p>
        </motion.div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-4">
          <FlowStep
            icon={<IconClipboardList />}
            title="1. Share Your Dream"
            description="Tell us your destination, budget, and travel style in a simple prompt."
            index={0}
          />
          <FlowStep
            icon={<IconMapPin />}
            title="2. Pick a Location"
            description="Our AI researches and suggests 3 perfect, personalized destinations for you to choose from."
            index={1}
          />
          <FlowStep
            icon={<IconPlaneHotel />}
            title="3. Confirm the Details"
            description="Select your preferred hotels and flights from a curated list that fits your budget."
            index={2}
          />
          <FlowStep
            icon={<IconDocumentDownload />}
            title="4. Get Your Itinerary"
            description="Receive a complete, day-by-day travel plan, ready for your adventure and sent to your email."
            index={3}
          />
        </div>
      </div>
    </section>
  );
};

// Update icon components to use sage color instead of blue
const IconClipboardList = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-sage-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
  </svg>
);

const IconMapPin = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-sage-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const IconPlaneHotel = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-sage-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l2-2m0 0l2-2m-2 2L12 10l-2 2m2 2l-2 2" />
  </svg>
);

const IconDocumentDownload = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-sage-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

export default HowItWorks;