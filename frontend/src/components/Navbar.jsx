import React from 'react';
import { LayoutDashboard, Camera, ClipboardCheck, Database } from 'lucide-react';

function Navbar({ currentScreen, onNavigate, hasActiveReview }) {
  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-gray-200 z-50 px-4 py-2 shadow-lg">
      <div className="flex items-center justify-around max-w-md mx-auto">
        <button
          onClick={() => onNavigate('dashboard')}
          className={`flex flex-col items-center gap-1 py-1 px-3 rounded-lg transition-colors ${
            currentScreen === 'dashboard' ? 'text-indigo-600 font-semibold' : 'text-gray-500'
          }`}
        >
          <LayoutDashboard className="w-5 h-5" />
          <span className="text-[11px]">Dashboard</span>
        </button>

        {/* Capture Button with integrated purple indicator */}
        <button
          onClick={() => onNavigate('capture')}
          className={`flex flex-col items-center gap-1 py-1 px-3 rounded-lg transition-colors ${
            currentScreen === 'capture' ? 'text-indigo-600 font-semibold' : 'text-gray-500 hover:text-gray-900'
          }`}
        >
          <div className="w-9 h-9 bg-indigo-600 text-white rounded-full flex items-center justify-center shadow-md shadow-indigo-200 hover:bg-indigo-700 transition-transform active:scale-95">
            <Camera className="w-5 h-5" />
          </div>
          <span className="text-[11px]">Capture</span>
        </button>

        {/* Review Button - Always Accessible */}
        <button
          onClick={() => onNavigate('review')}
          className={`flex flex-col items-center gap-1 py-1 px-3 rounded-lg transition-colors ${
            currentScreen === 'review'
              ? 'text-indigo-600 font-semibold'
              : 'text-gray-500 hover:text-gray-900'
          }`}
        >
          <div className="relative">
            <ClipboardCheck className="w-5 h-5" />
            {hasActiveReview && (
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-indigo-600 rounded-full animate-pulse" />
            )}
          </div>
          <span className="text-[11px]">Review</span>
        </button>

        <button
          onClick={() => onNavigate('telemetry')}
          className={`flex flex-col items-center gap-1 py-1 px-3 rounded-lg transition-colors ${
            currentScreen === 'telemetry' ? 'text-indigo-600 font-semibold' : 'text-gray-500'
          }`}
        >
          <Database className="w-5 h-5" />
          <span className="text-[11px]">Telemetry</span>
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
