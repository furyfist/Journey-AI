import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import HowItWorks from './components/howitworks';
import Explore from './components/Explore';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-cream-50 to-cream-100">
      <Header />
      <main className="flex-grow pattern-grid">
        <Hero />
        <HowItWorks/>
        <Explore />
      </main>
      <Footer className="mt-auto" />
    </div>
  )
}

export default App