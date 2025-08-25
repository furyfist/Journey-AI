import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import HowItWorks from './components/howitworks';
import Explore from './components/Explore';
import Footer from './components/Footer';
import { BACKEND_URL } from './apiConfig'; // --- IMPORT THE URL ---

function App() {
  const [serverStatus, setServerStatus] = useState('Connecting...');

  useEffect(() => {
    const checkServerHealth = async () => {
      try {
        // --- USE THE CORRECT, IMPORTED URL ---
        const response = await fetch(`${BACKEND_URL}/`, { 
          method: 'GET',
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        // Updated logic for a more descriptive status
        setServerStatus(data.status === 'OK' ? `🟢 Connected` : '🔴 Server Error');
      } catch (err) {
        console.error("Failed to check server health:", err);
        setServerStatus('🔴 Failed to connect');
      }
    };

    checkServerHealth();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-cream-50 to-cream-100">
      <Header />
      <main className="flex-grow pattern-grid">
        <div className="text-center py-2 text-sm text-sage-700 font-semibold">
          {serverStatus}
        </div>
        <Hero />
        <HowItWorks />
        <Explore />
      </main>
      <Footer className="mt-auto" />
    </div>
  );
}

export default App;