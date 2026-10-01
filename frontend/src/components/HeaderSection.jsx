import React, { useEffect, useRef, useState } from 'react';
import { LogOut, Menu } from 'lucide-react';

function HeaderSection({ user, onLogout }) {
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef(null);
  const userName = user?.name || 'Alex Jemison';

  useEffect(() => {
    const onPointerDown = (event) => {
      if (!menuRef.current?.contains(event.target)) setShowMenu(false);
    };
    document.addEventListener('pointerdown', onPointerDown);
    return () => document.removeEventListener('pointerdown', onPointerDown);
  }, []);

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

      <div className="relative" ref={menuRef}>
        <button
          type="button"
          onClick={() => setShowMenu((open) => !open)}
          aria-label="Account menu"
          aria-expanded={showMenu}
          className="w-11 h-11 bg-white hover:bg-gray-50 rounded-full flex items-center justify-center shadow-xs border border-gray-100 transition-transform active:scale-95 text-gray-700"
        >
          <Menu className="w-5 h-5 text-gray-800 stroke-[2]" />
        </button>
        {showMenu && (
          <div className="absolute right-0 top-14 z-50 min-w-[160px] rounded-2xl border border-gray-100 bg-white p-1.5 shadow-xl animate-fade-in">
            <button
              type="button"
              onClick={() => {
                setShowMenu(false);
                onLogout?.();
              }}
              className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-left text-[13px] font-bold text-rose-600 transition-colors hover:bg-rose-50"
            >
              <LogOut className="h-4 w-4" />
              <span>Log out</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}

export default HeaderSection;
