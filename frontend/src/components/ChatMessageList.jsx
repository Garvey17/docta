import React from 'react';

/**
 * Parses **bold** markdown into <strong> spans.
 */
function renderText(text = '') {
  const parts = text.split(/\*\*(.*?)\*\*/g);
  return parts.map((part, i) =>
    i % 2 === 1
      ? <strong key={i} className="font-semibold text-gray-900">{part}</strong>
      : <React.Fragment key={i}>{part}</React.Fragment>
  );
}

/** Small green robot icon used on every bot bubble */
function BotAvatar() {
  return (
    <div className="shrink-0 w-8 h-8 rounded-full bg-[#e3f79e] border border-[#c8e87a] flex items-center justify-center self-start mt-0.5">
      <svg className="w-4 h-4 text-gray-800" viewBox="0 0 24 24" fill="none">
        {/* Robot head */}
        <rect x="5" y="9" width="14" height="10" rx="3" stroke="currentColor" strokeWidth="1.8" />
        {/* Eyes */}
        <circle cx="9.5" cy="14" r="1.2" fill="currentColor" />
        <circle cx="14.5" cy="14" r="1.2" fill="currentColor" />
        {/* Antenna */}
        <line x1="12" y1="9" x2="12" y2="5.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <circle cx="12" cy="4.5" r="1.2" fill="currentColor" />
      </svg>
    </div>
  );
}

/**
 * Inline calorie progress card rendered inside a bot message.
 * Shown when msg.calorieCard is provided.
 */
function CalorieProgressCard({ current, goal, percent }) {
  const pct = Math.min(100, percent || Math.round((current / goal) * 100));
  return (
    <div className="bg-white rounded-[18px] p-4 mt-2 shadow-xs border border-gray-100">
      {/* Header row */}
      <div className="flex items-center gap-1.5 mb-3">
        <span className="text-base">🔥</span>
        <span className="text-[15px] font-bold text-gray-900">{current.toLocaleString()}</span>
        <span className="text-[13px] text-gray-400 font-medium">/ {goal.toLocaleString()} kcal</span>
      </div>

      {/* Progress bar track */}
      <div className="relative w-full h-2.5 bg-gray-100 rounded-full overflow-visible mb-1">
        <div
          className="h-full rounded-full bg-gradient-to-r from-[#bef264] to-[#84cc16]"
          style={{ width: `${pct}%` }}
        />
        {/* Floating badge above the bar end */}
        <div
          className="absolute -top-6 flex items-center justify-center"
          style={{ left: `calc(${pct}% - 18px)` }}
        >
          <span className="bg-gray-900 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow">
            {pct}%
          </span>
        </div>
      </div>
    </div>
  );
}

function ChatMessageList({ messages = [], isThinking = false }) {
  return (
    <div className="space-y-3 pt-1 pb-4">
      {messages.map((msg) => {
        const isBot = msg.sender === 'assistant';

        if (isBot) {
          return (
            <div key={msg.id} className="flex items-start gap-2.5 animate-fade-in">
              <BotAvatar />
              <div className="flex-1 min-w-0">
                {/* Gray bubble */}
                <div className="bg-gray-100 rounded-[20px] rounded-tl-[6px] px-4 py-3 text-[13px] sm:text-[14px] text-gray-800 leading-relaxed font-normal whitespace-pre-line max-w-[85%]">
                  {renderText(msg.text)}

                  {/* Inline calorie progress card */}
                  {msg.calorieCard && (
                    <CalorieProgressCard
                      current={msg.calorieCard.current}
                      goal={msg.calorieCard.goal}
                      percent={msg.calorieCard.percent}
                    />
                  )}

                  {/* Inline food suggestion cards */}
                  {msg.foodCards && msg.foodCards.length > 0 && (
                    <div className="flex gap-2 mt-3 flex-wrap">
                      {msg.foodCards.map((card, idx) => (
                        <div
                          key={idx}
                          className="bg-gray-50 border border-gray-100 rounded-[14px] px-3 py-2 flex flex-col items-center min-w-[80px] shadow-2xs"
                        >
                          <span className="text-2xl mb-1">{card.emoji}</span>
                          <span className="text-[11px] font-bold text-gray-700">{card.kcal} kcal</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        }

        // User message — lime green bubble, right-aligned
        return (
          <div key={msg.id} className="flex justify-end animate-fade-in">
            <div className="bg-[#d4f576] text-gray-900 rounded-[20px] rounded-br-[6px] px-4 py-3 text-[13px] sm:text-[14px] font-medium max-w-[80%] leading-relaxed">
              {msg.text}
            </div>
          </div>
        );
      })}

      {/* Thinking indicator */}
      {isThinking && (
        <div className="flex items-start gap-2.5 animate-fade-in">
          <BotAvatar />
          <div className="bg-gray-100 rounded-[20px] rounded-tl-[6px] px-4 py-3 flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatMessageList;
