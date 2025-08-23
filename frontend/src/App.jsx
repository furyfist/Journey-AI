import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import RecentSearches from './components/RecentSearches';
import Explore from './components/Explore';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <Hero />
        <RecentSearches />
        <Explore />
      </main>
      <Footer />
    </div>
  )
}

export default App