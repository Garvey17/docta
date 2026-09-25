import React from 'react';
import { LayoutDashboard, Camera, ClipboardCheck, Database, User, ShieldCheck } from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'capture', label: 'Capture', icon: Camera },
  { id: 'review', label: 'Review', icon: ClipboardCheck },
  { id: 'telemetry', label: 'Telemetry', icon: Database },
];

function RightSidebar({ currentScreen, onNavigate, hasActiveReview }) {
  return (
    <aside className="hidden lg:flex fixed right-0 top-0 h-screen w-20 bg-white border-l border-gray-200 flex-col items-center py-6 z-40 shadow-sm">
      {/* Brand Icon */}
      <div className="mb-8">
        <button
          onClick={() => onNavigate('dashboard')}
          className="w-11 h-11 bg-indigo-600 hover:bg-indigo-700 transition-colors rounded-xl flex items-center justify-center shadow-md shadow-indigo-200 group"
          title="docta Home"
        >
          <span className="text-white font-extrabold text-lg tracking-tight">d.</span>
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 flex flex-col gap-2 w-full px-3">
        {NAV_ITEMS.map((item) => {
          const isActive = currentScreen === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex flex-col items-center gap-1.5 py-3 rounded-xl transition-all duration-200 relative group ${
                isActive
                  ? 'bg-indigo-50 text-indigo-700 shadow-sm font-semibold'
                  : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'
              }`}
              title={item.label}
            >
              <div className="relative">
                <item.icon className="w-5 h-5 transition-transform group-hover:scale-110" />
                {item.id === 'review' && hasActiveReview && (
                  <span className="absolute -top-1 -right-1 w-2 h-2 bg-indigo-600 rounded-full animate-pulse" />
                )}
              </div>
              <span className="text-[10px] tracking-tight">{item.label}</span>
              {isActive && (
                <span className="absolute left-1 top-1/2 -translate-y-1/2 w-1 h-5 bg-indigo-600 rounded-full" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Info / Badge */}
      <div className="flex flex-col items-center gap-2">
        <div
          className="w-9 h-9 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-200 flex items-center justify-center text-xs font-bold"
          title="Active Learning Engine Online"
        >
          <ShieldCheck className="w-4 h-4" />
        </div>
      </div>
    </aside>
  );
}

export default RightSidebar;
