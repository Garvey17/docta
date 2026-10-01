import React from 'react';
import { Home, BarChart2, Scan } from 'lucide-react';

function Navbar({ currentScreen, onNavigate }) {
  const homeActive = currentScreen === 'dashboard';
  const statsActive = currentScreen === 'statistics' || currentScreen === 'telemetry';

  const itemClass = (active) => `transition-all duration-200 flex items-center justify-center ${
    active
      ? 'w-11 h-11 rounded-full bg-gradient-to-tr from-[#bef264] to-[#d9f99d] text-gray-950 shadow-md shadow-lime-300/50 scale-105'
      : 'w-10 h-10 rounded-full text-gray-700 hover:text-gray-950 hover:bg-gray-50'
  }`;

  return (
    <div className="fixed bottom-4 left-0 right-0 z-50 flex justify-center px-4 pointer-events-none select-none">
      <nav
        aria-label="Main navigation"
        className="pointer-events-auto bg-white/95 backdrop-blur-md rounded-full px-5 py-2 shadow-2xl shadow-black/15 border border-gray-100 flex items-center justify-between w-full max-w-[250px] relative"
      >
        <button
          type="button"
          onClick={() => onNavigate('dashboard')}
          aria-label="Home Dashboard"
          aria-current={homeActive ? 'page' : undefined}
          className={itemClass(homeActive)}
        >
          <Home className="w-5 h-5" fill={homeActive ? 'currentColor' : 'none'} strokeWidth={homeActive ? 1.5 : 2} />
        </button>

        <button
          type="button"
          onClick={() => onNavigate('capture')}
          aria-label="Scan Meal"
          className="w-12 h-12 -mt-6 rounded-full bg-gray-950 hover:bg-black text-white flex items-center justify-center shadow-xl shadow-black/30 border-[3px] border-white transition-transform active:scale-95"
        >
          <Scan className="w-5 h-5 text-white stroke-[2.2]" />
        </button>

        <button
          type="button"
          onClick={() => onNavigate('statistics')}
          aria-label="Statistics"
          aria-current={statsActive ? 'page' : undefined}
          className={itemClass(statsActive)}
        >
          <BarChart2 className="w-5 h-5 stroke-[2.2]" />
        </button>
      </nav>
    </div>
  );
}

export default Navbar;
