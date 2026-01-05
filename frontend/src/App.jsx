import React, { useCallback } from 'react';
import Navbar from './components/layouts/Navbar';
import Footer from './components/layouts/Footer';
import Hero from './components/sections/Hero';
import TopDeals from './components/sections/TopDeals';
import LiveFeed from './components/sections/LiveFeed';
import Features from './components/sections/Features';
import Pricing from './components/sections/Pricing';

const App = () => {
  const handleLinkClick = useCallback((e) => {
    e.preventDefault();
    const href = e.currentTarget.getAttribute('href');
    if (href && href.startsWith('#')) {
      const target = document.querySelector(href);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 font-sans text-slate-900 dark:text-slate-100 antialiased selection:bg-indigo-500/30 selection:text-indigo-600 dark:selection:text-indigo-300">
      <Navbar onLinkClick={handleLinkClick} />

      <main>
        <Hero />
        <TopDeals />
        <LiveFeed />
        <Features />
        <Pricing />
      </main>

      <Footer />
    </div>
  );
};

export default App;
