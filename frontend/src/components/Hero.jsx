import React, { useState } from 'react';
// --- Import the new, more robust libraries ---
import MarkdownIt from 'markdown-it';
import DOMPurify from 'isomorphic-dompurify';

// --- Initialize the Markdown converter ---
const md = new MarkdownIt();

const Hero = () => {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!prompt || isLoading) return;

    const newUserMessage = { sender: 'user', content: prompt };
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setIsLoading(true);
    setPrompt('');

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();

      // --- NEW 2-STEP RENDERING PIPELINE ---
      // 1. Convert the AI's Markdown response to an HTML string
      const rawHtml = md.render(data.itinerary);
      // 2. Sanitize that HTML string to ensure it's safe to render
      const cleanHtml = DOMPurify.sanitize(rawHtml);

      const newAiMessage = { sender: 'ai', content: cleanHtml };
      setMessages(prevMessages => [...prevMessages, newAiMessage]);

    } catch (err) {
      console.error("Failed to fetch itinerary:", err);
      const errorMessage = { sender: 'ai', content: 'Sorry, something went wrong. Please check the backend connection and try again.' };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="container mx-auto px-6 py-10 flex flex-col items-center">
      {messages.length === 0 && (
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-teal-heading">Where are you headed?</h1>
          <p className="mt-4 text-lg md:text-xl text-subtext-gray max-w-2xl">Your AI-powered trip planner for flights, hotels, and activities.</p>
        </div>
      )}

      {/* --- CHAT DISPLAY AREA --- */}
      <div className="w-full max-w-4xl mt-8 space-y-4">
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xl p-4 rounded-xl ${message.sender === 'user' ? 'bg-soft-green text-white' : 'bg-white shadow border'}`}>
              {message.sender === 'ai' ? (
                // --- THE FIX IS HERE ---
                // We now render the pre-sanitized HTML using dangerouslySetInnerHTML
                <div 
                  className="prose max-w-none" 
                  dangerouslySetInnerHTML={{ __html: message.content }} 
                />
              ) : (
                <p>{message.content}</p>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
             <div className="max-w-xl p-4 rounded-xl bg-white shadow border">
               <p className="animate-pulse text-subtext-gray">Thinking...</p>
             </div>
          </div>
        )}
      </div>

      {/* --- INPUT FORM (Unchanged) --- */}
      <div className="mt-auto w-full max-w-4xl pt-8">
        <form onSubmit={handleSubmit} className="flex items-center gap-2">
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
            className="px-6 py-3 font-semibold text-white bg-soft-green rounded-full shadow-md hover:bg-green-600 transition-colors duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed"
            disabled={isLoading || !prompt}
          >
            <span aria-hidden="true">→</span>
          </button>
        </form>
      </div>
    </section>
  );
};

export default Hero;