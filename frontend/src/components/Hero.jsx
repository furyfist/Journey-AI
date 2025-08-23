import React from 'react';

const Hero = () => {
  return (
    <section className="container mx-auto px-6 py-16 text-center flex flex-col items-center justify-center min-h-[45vh]">
      <h1 className="text-4xl md:text-6xl font-bold text-teal-heading">
        Where are you headed?
      </h1>
      <p className="mt-4 text-lg md:text-xl text-subtext-gray max-w-2xl">
        Your AI-powered trip planner that finds and books the best flights.
      </p>
      <div className="mt-8 flex flex-col sm:flex-row items-center gap-2 w-full max-w-2xl">
        <input
          type="text"
          placeholder="Plan a trip to Tokyo at the end of September"
          className="w-full px-5 py-3 text-base text-gray-700 placeholder-gray-400 bg-white border border-gray-300 rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-heading"
        />
        <button className="w-full sm:w-auto px-6 py-3 font-semibold text-white bg-soft-green rounded-full shadow-md hover:bg-green-600 transition-colors duration-300 flex items-center justify-center gap-2 whitespace-nowrap">
          Explore
          <span aria-hidden="true">→</span>
        </button>
      </div>
    </section>
  );
};

export default Hero;