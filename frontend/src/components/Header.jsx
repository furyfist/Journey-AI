import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false);

  React.useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="fixed w-full z-50 flex justify-center">
      <motion.header
        initial={{ width: "100%", y: -100 }}
        animate={{ 
          width: isScrolled ? "90%" : "100%",
          y: 0,
        }}
        transition={{
          width: { type: "spring", stiffness: 300, damping: 30 },
          y: { duration: 0.3 }
        }}
        className={`transition-all duration-300 ${
          isScrolled 
            ? 'h-16 py-2 bg-cream-50/80 backdrop-blur-lg shadow-lg rounded-b-2xl mx-auto' 
            : 'h-20 py-4 bg-transparent'
        }`}
      >
        <nav className={`container mx-auto px-6 flex justify-between items-center h-full transition-all duration-300 ${
          isScrolled ? 'max-w-7xl' : ''
        }`}>
          {/* Logo */}
          <motion.div 
            className="flex items-center gap-2"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className={`transition-all duration-300 ${
                isScrolled ? 'h-6 w-6' : 'h-8 w-8'
              } text-teal-600`}
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className={`font-bold bg-gradient-to-r from-sage-600 to-teal-600 text-transparent bg-clip-text transition-all duration-300 ${
              isScrolled ? 'text-lg' : 'text-xl'
            }`}>
              Journey AI
            </span>
          </motion.div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-8">
            <NavLink href="#explore">Explore</NavLink>
            <NavLink href="#how-it-works">How it Works</NavLink>
            <NavLink href="#about">About</NavLink>
          </div>

          {/* User Info */}
          <div className="flex items-center gap-4">
            <motion.div 
              className={`flex items-center gap-2 px-4 py-2 rounded-full bg-cream-200/50 backdrop-blur-sm transition-all duration-300 ${
                isScrolled ? 'scale-95' : ''
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className={`rounded-full bg-sage-100 flex items-center justify-center transition-all duration-300 ${
                isScrolled ? 'w-6 h-6' : 'w-8 h-8'
              }`}>
                <span className="text-sm font-medium text-sage-700">U</span>
              </div>
              <span className={`font-medium text-sage-700 transition-all duration-300 ${
                isScrolled ? 'text-xs' : 'text-sm'
              }`}>
                im.tsukiyuki@gmail.com
              </span>
            </motion.div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`font-medium text-sage-700 hover:text-teal-600 transition-all duration-300 ${
                isScrolled ? 'text-xs' : 'text-sm'
              }`}
            >
              Log Out
            </motion.button>
          </div>
        </nav>
      </motion.header>
    </div>
  );
};

// NavLink component for consistent styling
const NavLink = ({ href, children }) => (
  <motion.a
    href={href}
    className="text-sage-600 hover:text-teal-600 font-medium transition-colors"
    whileHover={{ scale: 1.05 }}
    whileTap={{ scale: 0.95 }}
  >
    {children}
  </motion.a>
);

export default Header;