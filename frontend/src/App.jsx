import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import HowItWorks from './components/howitworks';
import Explore from './components/Explore';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <Hero />
        <HowItWorks/>
        <Explore />
      </main>
      <Footer />
    </div>
  )
}

export default App