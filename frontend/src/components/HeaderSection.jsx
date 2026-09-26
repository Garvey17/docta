import React from 'react';
import { Bell } from 'lucide-react';

function HeaderSection({ user, onNotificationClick }) {
  const userName = user?.name || 'Alex Jemison';

  return (
    <header className="flex items-center justify-between pt-2 pb-5 px-1">
      <div>
        <p className="text-xs sm:text-sm text-gray-400 font-medium tracking-normal flex items-center gap-1.5">
          Good morning <span className="inline-block animate-pulse">👋</span>
        </p>
        <h1 className="text-2xl sm:text-[26px] font-bold text-gray-900 tracking-tight mt-0.5">
          {userName}
        </h1>
      </div>

      <button
        type="button"
        onClick={onNotificationClick}
        aria-label="Notifications"
        className="w-11 h-11 bg-white hover:bg-gray-50 rounded-full flex items-center justify-center shadow-xs border border-gray-100 transition-transform active:scale-95 text-gray-700"
      >
        <Bell className="w-5 h-5 text-gray-800 stroke-[1.8]" />
      </button>
    </header>
  );
}

export default HeaderSection;
