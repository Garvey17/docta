import React, { useState, useRef, useEffect } from 'react';
import { ArrowLeft, MoreVertical, Sparkles } from 'lucide-react';
import NutritionHighlightCard from './NutritionHighlightCard';
import ChatMessageList from './ChatMessageList';
import ChatInputDock from './ChatInputDock';

function generateContextualAIResponse(query, mealHistory, user) {
  const q = query.toLowerCase();
  const totalCalories = mealHistory.reduce((acc, m) => acc + (m.total_calories_kcal || 0), 0) || 1250;
  const totalProtein = mealHistory.reduce((acc, m) => acc + (m.total_protein_g || 0), 0) || 64;
  const calTarget = user?.dailyCalorieTarget || 2200;
  const remainingCal = Math.max(0, calTarget - totalCalories);

  // 1. Protein inquiries
  if (q.includes('protein') || q.includes('muscle') || q.includes('egg') || q.includes('meat')) {
    return {
      text: `You currently have **${totalProtein}g of protein** tracked today (${Math.round((totalProtein / 110) * 100)}% of your 110g target).\n\n**To hit your goal today:**\n• **Moi-Moi / Akara**: Steamed bean pudding provides clean plant protein (~12g per wrap) with high fiber.\n• **Grilled Croaker or Tilapia**: ~24g lean protein per palm-sized fillet without excessive saturated fat.\n• **Peppered Chicken/Turkey Breast**: High bioavailability with moderate spice to support thermogenesis.`,
      tags: [
        { label: `Current: ${totalProtein}g`, color: 'bg-[#e0f2fe] text-sky-800' },
        { label: `Goal: 110g`, color: 'bg-emerald-50 text-emerald-800' },
        { label: 'High Bioavailability', color: 'bg-[#e3f79e] text-gray-950' },
      ],
    };
  }

  // 2. Dinner or meal recommendations
  if (q.includes('dinner') || q.includes('suggest') || q.includes('eat') || q.includes('food') || q.includes('lunch') || q.includes('breakfast')) {
    return {
      text: `With **${remainingCal} kcal remaining** in your daily budget, here is an optimized Nigerian dinner recommendation:\n\n🍲 **Option 1: Okra & Seafood Soup with 1 Wrap of Amala** (~480 kcal)\n• High in soluble fiber (mucilage) which slows glucose absorption.\n• Includes fresh shrimp, fish, and moderate palm oil.\n\n🥗 **Option 2: Efo Riro (Spinach Stew) with Grilled Chicken** (~420 kcal)\n• Rich in dietary iron, folate, and lean protein with low glycemic impact.`,
      tags: [
        { label: `Budget: ${remainingCal} kcal`, color: 'bg-[#e3f79e] text-gray-950 font-bold' },
        { label: 'Low Glycemic Load', color: 'bg-emerald-50 text-emerald-800' },
        { label: 'WAFCT Optimized', color: 'bg-[#ffe4e6] text-rose-800' },
      ],
    };
  }

  // 3. Sodium, Vitals, Hydration
  if (q.includes('sodium') || q.includes('salt') || q.includes('water') || q.includes('pressure') || q.includes('hydration')) {
    return {
      text: `Your cardiovascular telemetry indicates **120 bpm blood pressure** and **12 glasses of water logged**.\n\n**Sodium & Blood Pressure Tips:**\n• Traditional bouillon cubes (Maggi/Knorr) are high in sodium. Consider augmenting flavors with **dawadawa (fermented locust beans)**, ground crayfish, garlic, and scent leaves.\n• Your current hydration is optimal, which assists your kidneys in electrolyte clearance.`,
      tags: [
        { label: 'Blood Pressure: 120 bpm', color: 'bg-[#e0f2fe] text-sky-800' },
        { label: 'Hydration: 12 glasses', color: 'bg-[#e3f79e] text-gray-950' },
        { label: 'Dawadawa Alternative', color: 'bg-amber-50 text-amber-800' },
      ],
    };
  }

  // 4. Calorie Deficit / Swallows
  if (q.includes('deficit') || q.includes('weight') || q.includes('swallow') || q.includes('fufu') || q.includes('eba') || q.includes('amala')) {
    return {
      text: `To sustain a healthy calorie deficit with African meals without feeling deprived:\n\n• **Swallow Hierarchy**: **Amala (Yam flour)** and **Oat Fufu** have higher fiber and lower caloric density than standard Pounded Yam or Garri (Eba).\n• **Soup to Swallow Ratio**: Shift your plate to **60% vegetable soup** and **40% swallow** rather than the inverse.\n• Avoid frying plantains (Dodo) when in deficit; opt for boiled ripe plantain with fish sauce instead.`,
      tags: [
        { label: 'Swallow Moderation', color: 'bg-[#e3f79e] text-gray-950' },
        { label: 'High Satiety', color: 'bg-emerald-50 text-emerald-800' },
      ],
    };
  }

  // Default fallback response
  return {
    text: `Based on your today's log of **${totalCalories} kcal** across ${mealHistory.length || 1} meal(s), your dietary fiber and macronutrient proportions are in good balance.\n\nI can analyze your meals, recommend dishes with West African food composition data, or help you scale conventional portion units (serving spoons, wraps, cups). What would you like to explore next?`,
    tags: [
      { label: `${totalCalories} kcal Tracked`, color: 'bg-[#e3f79e] text-gray-950 font-bold' },
      { label: 'WAFCT Active Learning', color: 'bg-indigo-50 text-indigo-800' },
    ],
  };
}

function InsightsChatScreen({
  user,
  mealHistory = [],
  onBack,
  onOptionsClick,
}) {
  const totalCalories = Math.round(mealHistory.reduce((acc, m) => acc + (m.total_calories_kcal || 0), 0)) || 1250;
  const totalProtein  = Math.round(mealHistory.reduce((acc, m) => acc + (m.total_protein_g  || 0), 0)) || 64;

  const [messages, setMessages] = useState([
    {
      id: 'msg-welcome',
      sender: 'assistant',
      text: `Hello ${user?.name || 'Alex'}! 👋 I've analyzed your nutrition history and WAFCT dietary composition for today.\n\nYou have consumed **${totalCalories} kcal** so far with **${totalProtein}g protein**. How can I assist you with your meals, portions, or metabolic targets?`,
      tags: [
        { label: `${totalCalories} / 2200 kcal`, color: 'bg-[#e3f79e] text-gray-950 font-bold' },
        { label: `Protein: ${totalProtein}g`, color: 'bg-[#e0f2fe] text-sky-800' },
        { label: 'African Gastronomy AI', color: 'bg-emerald-50 text-emerald-800' },
      ],
      timestamp: 'Just now',
    },
  ]);

  const [isThinking, setIsThinking] = useState(false);
  const chatBottomRef = useRef(null);

  const scrollToBottom = () => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = (text) => {
    const userMsg = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: 'Just now',
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsThinking(true);
    setTimeout(scrollToBottom, 50);

    setTimeout(() => {
      const responseData = generateContextualAIResponse(text, mealHistory, user);
      setIsThinking(false);
      setMessages((prev) => [
        ...prev,
        {
          id: `msg-res-${Date.now()}`,
          sender: 'assistant',
          text: responseData.text,
          tags: responseData.tags,
          timestamp: 'Just now',
        },
      ]);
      setTimeout(scrollToBottom, 50);
    }, 750);
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-3 sm:px-6 pt-2 pb-40 animate-fade-in select-none flex flex-col min-h-screen">
      {/* 1. Top Header */}
      <header className="flex items-center justify-between pt-3 pb-4 px-1 sticky top-0 bg-[#f7f8fa]/90 backdrop-blur-md z-30">
        {/* Back Button */}
        <button
          type="button"
          onClick={onBack}
          aria-label="Go back"
          className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-black/5 transition-colors text-gray-700 active:scale-95"
        >
          <ArrowLeft className="w-5 h-5 stroke-[2]" />
        </button>

        {/* Title — plain, no badge, no subtitle */}
        <h1 className="text-[18px] sm:text-[19px] font-bold text-gray-900 tracking-tight">
          Chatbot Insights
        </h1>

        {/* Options Button */}
        <button
          type="button"
          onClick={onOptionsClick}
          aria-label="More options"
          className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-black/5 transition-colors text-gray-700 active:scale-95"
        >
          <MoreVertical className="w-5 h-5 stroke-[2]" />
        </button>
      </header>

      {/* Chat Message Stream */}
      <ChatMessageList messages={messages} isThinking={isThinking} />

      <div ref={chatBottomRef} />

      {/* 4. Floating Chat Input Dock */}
      <ChatInputDock onSendMessage={handleSendMessage} disabled={isThinking} />
    </div>
  );
}

export default InsightsChatScreen;
