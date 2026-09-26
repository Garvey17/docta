import React from 'react';
import { Footprints, Droplets, Heart, ArrowUpRight } from 'lucide-react';

/**
 * Parses **bold** markdown into <strong> spans.
 */
function renderText(text = '') {
  const parts = text.split(/\*\*(.*?)\*\*/g);
  return parts.map((part, i) =>
    i % 2 === 1
      ? <strong key={i} className="font-bold text-gray-950">{part}</strong>
      : <React.Fragment key={i}>{part}</React.Fragment>
  );
}

/** Cute mint robot avatar with Homepage-inspired gradient & shadow */
function BotAvatar() {
  return (
    <div className="shrink-0 w-9 h-9 rounded-full bg-gradient-to-tr from-[#bef264] to-[#d9f99d] border border-lime-300/60 flex items-center justify-center self-start mt-0.5 shadow-md shadow-lime-300/30">
      <svg className="w-5 h-5 text-gray-950" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        {/* Antenna */}
        <path d="M12 2v3m-2-1.5h4" strokeWidth="1.9" strokeLinecap="round" />
        {/* Ears */}
        <rect x="2.5" y="10" width="2" height="4" rx="1" fill="currentColor" />
        <rect x="19.5" y="10" width="2" height="4" rx="1" fill="currentColor" />
        {/* Robot head */}
        <rect x="4.5" y="5.5" width="15" height="13" rx="4" strokeWidth="1.9" fill="#f4fee7" />
        {/* Eyes */}
        <circle cx="9" cy="11.5" r="1.5" fill="currentColor" />
        <circle cx="15" cy="11.5" r="1.5" fill="currentColor" />
        {/* Smile mouth */}
        <path d="M9.5 15c.8.6 1.7.9 2.5.9s1.7-.3 2.5-.9" strokeWidth="1.7" strokeLinecap="round" />
      </svg>
    </div>
  );
}

/**
 * Inline Calorie & Health Card combining patterns from MealProgressCard & HeartRateCard
 */
function CalorieProgressCard({
  current = 1250,
  goal = 1920,
  percent = 120,
  heartRate = 140,
  steps = 5234,
}) {
  const percentage = Math.min(100, Math.round((current / goal) * 100)) || 65;

  return (
    <div className="bg-white rounded-[26px] p-4 sm:p-5 mt-3 shadow-xs border border-gray-100/70 select-none">
      {/* 1. Header row: Flame + Macro Title & Target */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <span className="text-[16px]">🔥</span>
          <div className="text-[20px] sm:text-[22px] font-extrabold text-gray-950 tracking-tight leading-none">
            {current.toLocaleString()}{' '}
            <span className="text-gray-400 font-normal text-[16px]">/</span>{' '}
            <span className="text-gray-900 font-bold">{goal.toLocaleString()}</span>{' '}
            <span className="text-[12px] font-semibold text-gray-500">kcal</span>
          </div>
        </div>

        {/* Floating percentage badge */}
        <span className="bg-gray-950 text-white text-[10px] font-extrabold px-2.5 py-0.5 rounded-full shadow-2xs tracking-tight">
          {percent}%
        </span>
      </div>

      {/* 2. Striped Progress Bar inherited directly from MealProgressCard */}
      <div className="w-full h-5 rounded-full overflow-hidden bg-striped-pattern flex p-0.5 border border-gray-100/80 mb-3">
        <div
          className="h-full rounded-full bg-gradient-to-r from-[#dcfce7] via-[#bef264] to-[#84cc16] transition-all duration-700 ease-out shadow-2xs"
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* 3. Contextual Insight Paragraph */}
      <p className="text-[13px] sm:text-[13.5px] text-gray-800 leading-relaxed font-normal mb-3">
        Your calorie intake is <strong className="font-bold text-gray-950">{current} kcal</strong> towards your goal of {goal}. Heart Rate is elevated at <strong className="font-bold text-gray-950">{heartRate} bpm</strong>. Steps: <strong className="font-bold text-gray-950">{steps.toLocaleString()}</strong>.
      </p>

      {/* 4. Mini Vitals Indicators (Inherited from ActivityMetricCards) */}
      <div className="grid grid-cols-2 gap-2 pt-2 border-t border-gray-50">
        <div className="bg-[#f8fafc] rounded-2xl p-2.5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center">
              <Heart className="w-3.5 h-3.5 stroke-[2.2] fill-rose-500/20" />
            </div>
            <div>
              <span className="text-[10px] font-medium text-gray-400 block leading-tight">Heart Rate</span>
              <span className="text-[12px] font-extrabold text-gray-900">{heartRate} bpm</span>
            </div>
          </div>
          <span className="text-[9px] font-bold text-rose-700 bg-rose-100/80 px-1.5 py-0.5 rounded-md">
            High
          </span>
        </div>

        <div className="bg-[#f8fafc] rounded-2xl p-2.5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-lime-50 text-lime-700 flex items-center justify-center">
              <Footprints className="w-3.5 h-3.5 stroke-[2.2]" />
            </div>
            <div>
              <span className="text-[10px] font-medium text-gray-400 block leading-tight">Daily Steps</span>
              <span className="text-[12px] font-extrabold text-gray-900">{steps.toLocaleString()}</span>
            </div>
          </div>
          <span className="text-[9px] font-bold text-lime-800 bg-[#e3f79e] px-1.5 py-0.5 rounded-md">
            Active
          </span>
        </div>
      </div>
    </div>
  );
}

/**
 * Detailed Almonds Vector Illustration
 */
function AlmondsIllustration() {
  return (
    <svg className="w-16 h-12 my-1 drop-shadow-sm" viewBox="0 0 100 70" fill="none">
      <defs>
        <radialGradient id="almondGrad1" cx="40%" cy="35%" r="65%">
          <stop offset="0%" stopColor="#d97706" />
          <stop offset="60%" stopColor="#b45309" />
          <stop offset="100%" stopColor="#78350f" />
        </radialGradient>
        <radialGradient id="almondGrad2" cx="35%" cy="30%" r="65%">
          <stop offset="0%" stopColor="#f59e0b" />
          <stop offset="70%" stopColor="#b45309" />
          <stop offset="100%" stopColor="#78350f" />
        </radialGradient>
      </defs>
      <ellipse cx="50" cy="58" rx="42" ry="7" fill="#000000" fillOpacity="0.08" />
      <path
        d="M22 42C12 36 20 22 35 24C48 26 50 44 38 48C30 50 26 45 22 42Z"
        fill="url(#almondGrad1)"
      />
      <path
        d="M78 40C88 34 82 20 67 22C54 24 50 42 62 47C70 50 74 44 78 40Z"
        fill="url(#almondGrad1)"
      />
      <path
        d="M32 46C20 38 28 18 48 20C62 21 66 42 52 50C42 55 36 50 32 46Z"
        fill="url(#almondGrad2)"
      />
      <path
        d="M66 48C76 40 70 22 52 24C38 26 36 46 50 52C60 55 64 51 66 48Z"
        fill="url(#almondGrad2)"
      />
      <path d="M42 26C45 34 44 42 41 46" stroke="#fde68a" strokeWidth="0.9" strokeLinecap="round" strokeOpacity="0.6" />
      <path d="M58 28C56 36 57 44 60 48" stroke="#fde68a" strokeWidth="0.9" strokeLinecap="round" strokeOpacity="0.6" />
      <path d="M49 24C50 32 50 40 48 48" stroke="#fde68a" strokeWidth="0.8" strokeLinecap="round" strokeOpacity="0.5" />
    </svg>
  );
}

/**
 * Detailed Banana Vector Illustration
 */
function BananaIllustration() {
  return (
    <svg className="w-16 h-12 my-1 drop-shadow-sm" viewBox="0 0 100 70" fill="none">
      <defs>
        <linearGradient id="bananaYellow" x1="10%" y1="20%" x2="90%" y2="80%">
          <stop offset="0%" stopColor="#fef08a" />
          <stop offset="35%" stopColor="#facc15" />
          <stop offset="85%" stopColor="#eab308" />
          <stop offset="100%" stopColor="#ca8a04" />
        </linearGradient>
      </defs>
      <ellipse cx="50" cy="58" rx="38" ry="6" fill="#000000" fillOpacity="0.08" />
      <path
        d="M15 32C25 48 45 56 75 46C82 43 85 36 82 32C62 44 40 40 22 26C18 24 14 27 15 32Z"
        fill="url(#bananaYellow)"
      />
      <path
        d="M17 31C32 44 54 46 80 34"
        stroke="#fef9c3"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeOpacity="0.9"
      />
      <path
        d="M15 32L10 33C9 33 8.5 32 9 31L13 27C14 26 15 27 15 28L15 32Z"
        fill="#4d7c0f"
      />
      <circle cx="82.5" cy="33" r="1.5" fill="#713f12" />
    </svg>
  );
}

/**
 * Dual Snack Suggestion Cards matching ActivityMetricCards architecture
 */
function FoodRecommendationCards({ cards = [] }) {
  return (
    <div className="grid grid-cols-2 gap-3 mt-3 select-none">
      {cards.map((card, idx) => {
        const isAlmond = card.name?.toLowerCase().includes('almond') || card.id === 'almonds' || idx === 0;
        const title = isAlmond ? 'Almonds' : 'Banana';
        const tag = isAlmond ? 'High Magnesium' : 'Potassium Boost';

        return (
          <div
            key={idx}
            className="bg-white rounded-[24px] p-4 shadow-xs border border-gray-100/70 hover:border-gray-200 transition-all flex flex-col justify-between group cursor-pointer active:scale-98"
          >
            {/* Top row: Title & Calorie Badge */}
            <div className="flex items-start justify-between mb-2">
              <div>
                <h4 className="text-[14px] font-bold text-gray-900 leading-tight">
                  {title}
                </h4>
                <span className="text-[10px] font-medium text-gray-400 block mt-0.5">
                  {tag}
                </span>
              </div>

              {/* Floating Calorie Pill */}
              <span className="bg-gray-950 text-white text-[10px] font-extrabold px-2 py-0.5 rounded-full shadow-2xs">
                {card.kcal} kcal
              </span>
            </div>

            {/* Illustration */}
            <div className="py-2 flex items-center justify-center">
              {isAlmond ? <AlmondsIllustration /> : <BananaIllustration />}
            </div>

            {/* Bottom status */}
            <div className="pt-1 text-center">
              <span className="text-[11px] font-bold text-gray-800 bg-[#f4f6ef] px-2.5 py-1 rounded-full inline-block">
                1 standard snack
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ChatMessageList({ messages = [], isThinking = false }) {
  return (
    <div className="space-y-4 pt-1 pb-6">
      {messages.map((msg) => {
        const isBot = msg.sender === 'assistant';

        if (isBot) {
          return (
            <div key={msg.id} className="flex items-start gap-2.5 animate-fade-in">
              <BotAvatar />
              <div className="flex-1 min-w-0 max-w-[94%] sm:max-w-[88%]">
                {/* Clean Assistant Card Bubble */}
                <div className="bg-white text-gray-900 border border-gray-100/80 rounded-[26px] rounded-tl-[4px] p-4 sm:p-5 shadow-xs text-[13.5px] sm:text-[14px] leading-relaxed whitespace-pre-line">
                  {renderText(msg.text)}

                  {/* Inline Calorie & Health Card */}
                  {msg.calorieCard && (
                    <CalorieProgressCard
                      current={msg.calorieCard.current}
                      goal={msg.calorieCard.goal}
                      percent={msg.calorieCard.percent}
                      heartRate={msg.calorieCard.heartRate}
                      steps={msg.calorieCard.steps}
                    />
                  )}

                  {/* Inline Food Suggestion Cards */}
                  {msg.foodCards && msg.foodCards.length > 0 && (
                    <FoodRecommendationCards cards={msg.foodCards} />
                  )}
                </div>
              </div>
            </div>
          );
        }

        // User message — Homepage-style Lime Pill Bubble
        return (
          <div key={msg.id} className="flex justify-end animate-fade-in">
            <div className="bg-[#e3f79e] text-gray-950 rounded-[24px] rounded-br-[4px] px-4.5 py-3 text-[13.5px] sm:text-[14px] font-semibold max-w-[82%] leading-relaxed shadow-2xs border border-[#d6f284]/60">
              {msg.text}
            </div>
          </div>
        );
      })}

      {/* Thinking Indicator */}
      {isThinking && (
        <div className="flex items-start gap-2.5 animate-fade-in">
          <BotAvatar />
          <div className="bg-white border border-gray-100 rounded-[22px] rounded-tl-[4px] px-4 py-3 flex items-center gap-1.5 shadow-xs">
            <div className="w-2 h-2 rounded-full bg-[#bef264] animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 rounded-full bg-[#84cc16] animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatMessageList;
