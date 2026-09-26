'use client';

import React, { useRef } from 'react';

const COLORS = [
  { border: '#5B50E5', fill: 'rgba(91, 80, 229, 0.18)' },
  { border: '#10B981', fill: 'rgba(16, 185, 129, 0.18)' },
  { border: '#F59E0B', fill: 'rgba(245, 158, 11, 0.18)' },
  { border: '#EC4899', fill: 'rgba(236, 72, 153, 0.18)' },
];

interface BoundingOverlayProps {
  imageUrl?: string;
  items?: Array<{
    item_id: string;
    food_name?: string;
    display_name?: string;
    confidence?: number;
    bounding_box?: [number, number, number, number];
  }>;
  activeItemId?: string | null;
  onSelectItem?: (id: string) => void;
}

export function BoundingOverlay({
  imageUrl = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80',
  items = [],
  activeItemId,
  onSelectItem,
}: BoundingOverlayProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <div
      ref={containerRef}
      className="relative w-full aspect-[4/3] rounded-2xl overflow-hidden bg-slate-900 shadow-md group select-none"
    >
      <img
        src={imageUrl}
        alt="Captured Meal"
        className="w-full h-full object-cover"
      />

      <div className="absolute inset-0">
        {items.map((item, idx) => {
          const color = COLORS[idx % COLORS.length];
          const isActive = activeItemId === item.item_id;
          const box = item.bounding_box || [0.1, 0.1, 0.9, 0.9];

          const leftPct = Math.min(box[0], box[2]) * 100;
          const topPct = Math.min(box[1], box[3]) * 100;
          const widthPct = Math.abs(box[2] - box[0]) * 100;
          const heightPct = Math.abs(box[3] - box[1]) * 100;

          return (
            <div
              key={item.item_id || idx}
              onClick={() => onSelectItem && onSelectItem(item.item_id)}
              style={{
                left: `${leftPct}%`,
                top: `${topPct}%`,
                width: `${widthPct}%`,
                height: `${heightPct}%`,
                borderColor: color.border,
                backgroundColor: isActive ? color.fill : 'rgba(0,0,0,0.05)',
              }}
              className={`absolute border-2 rounded-xl transition-all duration-200 cursor-pointer ${
                isActive
                  ? 'ring-4 ring-white/50 scale-[1.01] z-20 shadow-lg'
                  : 'hover:border-white hover:scale-[1.005] z-10'
              }`}
            >
              <div
                style={{ backgroundColor: color.border }}
                className="absolute -top-3.5 left-2 px-2 py-0.5 rounded-md text-[11px] font-bold text-white shadow-md flex items-center gap-1.5 whitespace-nowrap"
              >
                <span>{item.food_name || item.display_name}</span>
                <span className="opacity-80 font-normal">
                  {Math.round((item.confidence || 0.9) * 100)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent p-3 text-white flex items-center justify-between text-xs">
        <span className="font-medium flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          CV Multi-Food Localization ({items.length} items detected)
        </span>
        <span className="text-gray-300 text-[11px]">Click box to focus dish</span>
      </div>
    </div>
  );
}

export default BoundingOverlay;
