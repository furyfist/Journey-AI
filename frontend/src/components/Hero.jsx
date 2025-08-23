import React, { useState } from 'react';

const Hero = () => {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [itinerary, setItinerary] = useState('');
 
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault(); 
    setItinerary('');
    setError('');

    if (!prompt) {
      setError('Please enter a travel prompt.');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: prompt }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setItinerary(data.itinerary);

    } catch (err) {
      console.error("Failed to fetch itinerary:", err);
      setError('Sorry, something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <section className="container mx-auto px-6 py-16 text-center flex flex-col items-center justify-center min-h-[45vh]">
        <h1 className="text-4xl md:text-6xl font-bold text-teal-heading">
          Where are you headed?
        </h1>
        <p className="mt-4 text-lg md:text-xl text-subtext-gray max-w-2xl">
          Your AI-powered trip planner for flights, hotels, and activities.
        </p>
        
        {/* --- FORM & INPUT --- */}
        <form onSubmit={handleSubmit} className="mt-8 flex flex-col sm:flex-row items-center gap-2 w-full max-w-2xl">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Plan a 3-day trip to Rome for a foodie"
            className="w-full px-5 py-3 text-base text-gray-700 placeholder-gray-400 bg-white border border-gray-300 rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-heading"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="w-full sm:w-auto px-6 py-3 font-semibold text-white bg-soft-green rounded-full shadow-md hover:bg-green-600 transition-colors duration-300 flex items-center justify-center gap-2 whitespace-nowrap disabled:bg-gray-400 disabled:cursor-not-allowed"
            disabled={isLoading}
          >
            {isLoading ? 'Thinking...' : 'Explore'}
            {!isLoading && <span aria-hidden="true">→</span>}
          </button>
        </form>
      </section>

      {/* --- RESULTS SECTION --- */}
      <section className="container mx-auto px-6 pb-16 text-left">
        {isLoading && (
          <div className="text-center">
            <p className="text-lg text-subtext-gray animate-pulse">Journey AI is planning your trip...</p>
          </div>
        )}

        {error && (
          <div className="max-w-4xl mx-auto p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            <p>{error}</p>
          </div>
        )}

        {itinerary && (
          <div className="max-w-4xl mx-auto p-6 bg-white rounded-xl shadow-lg border border-gray-200">
            {/* The 'whitespace-pre-wrap' class is key to preserving line breaks and spacing from the AI's response */}
            <div 
              className="prose max-w-none text-gray-700 whitespace-pre-wrap" 
              dangerouslySetInnerHTML={{ __html: itinerary.replace(/\n/g, '<br />') }}
            />
          </div>
        )}
      </section>
    </>
  );
};

export default Hero;