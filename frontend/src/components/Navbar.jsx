import React from 'react';
import { Home, BarChart2, User, Scan } from 'lucide-react';

/** Custom AI chat icon — speech bubble with a small sparkle node */
function AiChatIcon({ className = 'w-5 h-5' }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Chat bubble */}
      <path
        d="M21 12c0 4.418-4.029 8-9 8a9.77 9.77 0 01-3.74-.74L3 21l1.8-4.5C3.66 15.07 3 13.6 3 12c0-4.418 4.029-8 9-8s9 3.582 9 8z"
        stroke="currentColor"
        strokeWidth="1.9"
        strokeLinejoin="round"
      />
      {/* Three dot nodes representing AI/neural thinking */}
      <circle cx="8.5" cy="12" r="1.1" fill="currentColor" />
      <circle cx="12" cy="12" r="1.1" fill="currentColor" />
      <circle cx="15.5" cy="12" r="1.1" fill="currentColor" />
    </svg>
  );
}

function Navbar({ currentScreen, onNavigate, hasActiveReview, onOpenAuth }) {
  return (
    <div className="fixed bottom-4 left-0 right-0 z-50 flex justify-center px-4 pointer-events-none">
      <nav className="pointer-events-auto bg-white/95 backdrop-blur-md rounded-full px-3 py-2 shadow-2xl shadow-black/15 border border-gray-100 flex items-center justify-between w-full max-w-[360px] relative">
        {/* 1. Home Tab */}
        <button
          type="button"
          onClick={() => onNavigate('dashboard')}
          aria-label="Home Dashboard"
          className={`transition-all duration-200 flex items-center justify-center ${
            currentScreen === 'dashboard'
              ? 'w-11 h-11 rounded-full bg-gradient-to-tr from-[#bef264] to-[#d9f99d] text-gray-950 shadow-md shadow-lime-300/50 scale-105'
              : 'w-10 h-10 rounded-full text-gray-700 hover:text-gray-950 hover:bg-gray-50'
          }`}
        >
          <Home
            className="w-5 h-5"
            fill={currentScreen === 'dashboard' ? 'currentColor' : 'none'}
            strokeWidth={currentScreen === 'dashboard' ? 1.5 : 2}
          />
        </button>

        {/* 2. Stats / Analytics Tab */}
        <button
          type="button"
          onClick={() => onNavigate('statistics')}
          aria-label="Statistics"
          className={`transition-all duration-200 flex items-center justify-center ${
            currentScreen === 'telemetry' || currentScreen === 'statistics'
              ? 'w-11 h-11 rounded-full bg-gradient-to-tr from-[#bef264] to-[#d9f99d] text-gray-950 shadow-md shadow-lime-300/50 scale-105'
              : 'w-10 h-10 rounded-full text-gray-700 hover:text-gray-950 hover:bg-gray-50'
          }`}
        >
          <BarChart2 className="w-5 h-5 stroke-[2.2]" />
        </button>


        {/* 3. Center Floating Scanner / Camera Button */}
        <div className="relative -mt-6">
          <button
            type="button"
            onClick={() => onNavigate('capture')}
            aria-label="Scan Meal"
            className="w-12 h-12 rounded-full bg-gray-950 hover:bg-black text-white flex items-center justify-center shadow-xl shadow-black/30 border-[3px] border-white transition-transform active:scale-95"
          >
            <Scan className="w-5 h-5 text-white stroke-[2.2]" />
          </button>
        </div>

        {/* 4. AI Insights Tab */}
        <button
          type="button"
          onClick={() => onNavigate('insights')}
          aria-label="AI Insights"
          className={`transition-all duration-200 flex items-center justify-center relative ${
            currentScreen === 'insights' || currentScreen === 'review'
              ? 'w-11 h-11 rounded-full bg-gradient-to-tr from-[#bef264] to-[#d9f99d] text-gray-950 shadow-md shadow-lime-300/50 scale-105'
              : 'w-10 h-10 rounded-full text-gray-700 hover:text-gray-950 hover:bg-gray-50'
          }`}
        >
          <AiChatIcon className="w-5 h-5" />
        </button>


        {/* 5. User Profile Tab */}
        <button
          type="button"
          onClick={() => (onOpenAuth ? onOpenAuth() : onNavigate('dashboard'))}
          aria-label="User Profile"
          className="w-10 h-10 rounded-full text-gray-700 hover:text-gray-950 hover:bg-gray-50 flex items-center justify-center transition-colors"
        >
          <User className="w-5 h-5 stroke-[2]" />
        </button>
      </nav>
    </div>
  );
}

export default Navbar;
