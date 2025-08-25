import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import MarkdownIt from 'markdown-it';
import DOMPurify from 'isomorphic-dompurify';
import { BACKEND_URL } from '../apiConfig';

// --- Initialize the Markdown converter ---
const md = new MarkdownIt();

// --- BEST PRACTICE: Define the backend URL in one place ---
//const BACKEND_URL = 'http://122.0.0.1:8000';

// AnimatedBackground component (unchanged)
const AnimatedBackground = () => (
  <div className="absolute inset-0 overflow-hidden -z-10">
    <div className="absolute w-[500px] h-[500px] bg-sage-100/50 rounded-full blur-3xl -top-32 -left-32 animate-blob"/>
    <div className="absolute w-[500px] h-[500px] bg-cream-200/50 rounded-full blur-3xl top-32 -right-32 animate-blob animation-delay-2000"/>
    <div className="absolute w-[500px] h-[500px] bg-teal-500/30 rounded-full blur-3xl bottom-32 left-32 animate-blob animation-delay-4000"/>
    <div className="absolute top-20 left-[20%] animate-float-slow">
      <div className="w-12 h-12 rounded-full bg-cream-300/80 flex items-center justify-center">
        <span className="text-2xl">✈️</span>
      </div>
    </div>
    <div className="absolute top-40 right-[15%] animate-float-slower">
      <div className="w-10 h-10 rounded-full bg-sage-100/80 flex items-center justify-center">
        <span className="text-xl">🗺️</span>
      </div>
    </div>
    <div className="absolute bottom-32 left-[30%] animate-float">
      <div className="w-8 h-8 rounded-full bg-cream-200/80 flex items-center justify-center">
        <span className="text-lg">🌴</span>
      </div>
    </div>
  </div>
);

const Hero = () => {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [sendCopyTo, setSendCopyTo] = useState('');
  const [calendarAttendees, setCalendarAttendees] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [itinerary, setItinerary] = useState('');
  // NOTE: In a real app, this email would come from an auth system.
  const userEmail = 'im.tsukiyuki@gmail.com'; 

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!prompt || isLoading) return;

    const newUserMessage = { sender: 'user', content: prompt };
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setIsLoading(true);
    setPrompt('');

    try {
      const payload = {
        main_prompt: newUserMessage.content, // Use content from the message object for consistency
        user_email: userEmail,
        send_copy_to: sendCopyTo || undefined,
        calendar_attendees: calendarAttendees ? calendarAttendees.split(',').map(email => email.trim()) : undefined,
      };

      // --- CORRECTION: Use the correct backend URL ---
      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setItinerary(data.itinerary);

      const rawHtml = md.render(data.itinerary);
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

  const handleDownloadPDF = async () => {
    if (!itinerary || isLoading) return;

    try {
      // --- CORRECTION: Use the correct backend URL ---
      const response = await fetch(`${BACKEND_URL}/api/download-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ markdown_text: itinerary }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'itinerary.pdf';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (err) {
      console.error("Failed to download PDF:", err);
      // To avoid clutter, you might want a different way to show this error (e.g., a toast notification)
      const errorMessage = { sender: 'ai', content: 'Failed to download PDF. Please try again.' };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    }
  };

  return (
    <section className="pt-32 md:pt-40 relative min-h-[80vh] bg-gradient-to-b from-transparent to-white/90 overflow-hidden">
      <AnimatedBackground />
      <div className="container mx-auto px-6 py-16 flex flex-col items-center relative z-10">
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="text-center"
            >
              <motion.h1 
                className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-sage-600 via-teal-600 to-sage-500 text-transparent bg-clip-text"
                animate={{ 
                  backgroundPosition: ['0%', '100%'],
                  transition: { duration: 3, repeat: Infinity, repeatType: "reverse" } 
                }}
                style={{ backgroundSize: '200%' }}
              >
                Where are you headed?
              </motion.h1>
              <p className="mt-6 text-xl md:text-2xl text-sage-700 max-w-2xl mx-auto font-light">
                Your AI-powered trip planner for flights, hotels, and activities.
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        <motion.div layout className="w-full max-w-4xl mt-8 space-y-6 backdrop-blur-sm">
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-xl p-6 rounded-2xl backdrop-blur-sm ${
                  message.sender === 'user' 
                    ? 'bg-gradient-to-r from-teal-600 to-sage-600 text-cream-50 shadow-sage-200'
                    : 'bg-cream-50/90 shadow-lg border border-cream-200'
                } shadow-lg hover:shadow-xl transition-shadow duration-300`}
              >
                {message.sender === 'ai' ? (
                  <div className="prose prose-sage max-w-none" dangerouslySetInnerHTML={{ __html: message.content }} />
                ) : (
                  <p className="text-lg">{message.content}</p>
                )}
              </div>
            </motion.div>
          ))}

          {isLoading && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="max-w-xl p-6 rounded-2xl bg-cream-50 shadow-lg border border-cream-200">
                <div className="flex items-center space-x-3">
                  <div className="flex space-x-1">
                    <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce"></div>
                  </div>
                  <p className="text-gray-500">Crafting your perfect itinerary...</p>
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>

        <motion.div 
          layout
          className="mt-auto w-full max-w-4xl pt-8"
        >
          <form onSubmit={handleSubmit} className="flex flex-col gap-3 relative">
            <div className="relative w-full group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-sage-500 via-teal-500 to-sage-600 rounded-full opacity-75 group-hover:opacity-100 blur transition duration-1000 group-hover:duration-200 animate-gradient-x"></div>
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Plan a 3-day trip to Rome for a foodie"
                className="relative w-full px-6 py-4 text-lg text-sage-700 placeholder-sage-500/60 
                  bg-cream-50/90 backdrop-blur-sm border border-transparent rounded-full shadow-lg
                  focus:outline-none focus:ring-2 focus:ring-sage-500 focus:border-transparent
                  transition-all duration-300"
                disabled={isLoading}
              />
            </div>
            <div className="flex gap-3">
              <input
                type="email"
                value={sendCopyTo}
                onChange={(e) => setSendCopyTo(e.target.value)}
                placeholder="Send copy to (optional)"
                className="w-full px-6 py-4 text-lg text-sage-700 placeholder-sage-500/60 
                  bg-cream-50/90 backdrop-blur-sm border border-transparent rounded-full shadow-lg
                  focus:outline-none focus:ring-2 focus:ring-sage-500 focus:border-transparent
                  transition-all duration-300"
                disabled={isLoading}
              />
              <input
                type="text"
                value={calendarAttendees}
                onChange={(e) => setCalendarAttendees(e.target.value)}
                placeholder="Calendar attendees (comma-separated, optional)"
                className="w-full px-6 py-4 text-lg text-sage-700 placeholder-sage-500/60 
                  bg-cream-50/90 backdrop-blur-sm border border-transparent rounded-full shadow-lg
                  focus:outline-none focus:ring-2 focus:ring-sage-500 focus:border-transparent
                  transition-all duration-300"
                disabled={isLoading}
              />
            </div>
            <div className="flex gap-3">
              <button 
                type="submit" 
                className="px-8 py-4 font-semibold text-cream-50 bg-gradient-to-r 
                  from-teal-600 to-sage-600 rounded-full shadow-lg
                  hover:from-teal-700 hover:to-sage-700 
                  transform hover:scale-105 transition-all duration-300
                  disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                disabled={isLoading || !prompt}
              >
                 <span className="text-xl">→</span>
              </button>
              {itinerary && ( // Conditionally render the download button
                <button 
                  type="button" 
                  onClick={handleDownloadPDF}
                  className="px-8 py-4 font-semibold text-cream-50 bg-gradient-to-r 
                    from-sage-600 to-teal-600 rounded-full shadow-lg
                    hover:from-sage-700 hover:to-teal-700 
                    transform hover:scale-105 transition-all duration-300
                    disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                  disabled={isLoading}
                >
                  Download PDF
                </button>
              )}
            </div>
          </form>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;