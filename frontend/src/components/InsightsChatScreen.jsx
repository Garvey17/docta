import React, { useState, useRef, useEffect } from 'react';
import { ArrowLeft, MoreVertical } from 'lucide-react';
import ChatMessageList from './ChatMessageList';
import ChatInputDock from './ChatInputDock';

function generateContextualAIResponse(query, mealHistory = [], user) {
  const q = query.toLowerCase();
  const totalCalories = Math.round(mealHistory.reduce((acc, m) => acc + (m.total_calories_kcal || 0), 0)) || 1250;
  const totalProtein = Math.round(mealHistory.reduce((acc, m) => acc + (m.total_protein_g || 0), 0)) || 64;
  const calTarget = user?.dailyCalorieTarget || 2200;
  const remainingCal = Math.max(0, calTarget - totalCalories);

  // 1. Protein inquiries
  if (q.includes('protein') || q.includes('muscle') || q.includes('egg') || q.includes('meat')) {
    return {
      text: `You currently have **${totalProtein}g of protein** tracked today (${Math.round((totalProtein / 110) * 100)}% of your 110g target).\n\n**To hit your goal today:**\n• **Moi-Moi / Akara**: Steamed bean pudding provides clean plant protein (~12g per wrap) with high fiber.\n• **Grilled Croaker or Tilapia**: ~24g lean protein per palm-sized fillet without excessive saturated fat.\n• **Peppered Chicken/Turkey Breast**: High bioavailability with moderate spice to support thermogenesis.`,
    };
  }

  // 2. Dinner or meal recommendations
  if (q.includes('dinner') || q.includes('suggest') || q.includes('eat') || q.includes('food') || q.includes('lunch') || q.includes('breakfast')) {
    return {
      text: `With **${remainingCal} kcal remaining** in your daily budget, here is an optimized Nigerian dinner recommendation:\n\n🍲 **Option 1: Okra & Seafood Soup with 1 Wrap of Amala** (~480 kcal)\n• High in soluble fiber (mucilage) which slows glucose absorption.\n• Includes fresh shrimp, fish, and moderate palm oil.\n\n🥗 **Option 2: Efo Riro (Spinach Stew) with Grilled Chicken** (~420 kcal)\n• Rich in dietary iron, folate, and lean protein with low glycemic impact.`,
    };
  }

  // 3. Heart rate / Vitals / Hydration
  if (q.includes('heart') || q.includes('rate') || q.includes('pressure') || q.includes('bpm') || q.includes('vitals')) {
    return {
      text: `Considering your current high heart rate (140 bpm) and other factors, perhaps you could benefit from a short meditation session or a lighter exercise. To balance nutrients, try this snack recommendation from your library:`,
      foodCards: [
        { name: 'Almonds', emoji: '🥜', kcal: 150 },
        { name: 'Banana', emoji: '🍌', kcal: 80 },
      ],
    };
  }

  // 4. Sodium, Salt, Water
  if (q.includes('sodium') || q.includes('salt') || q.includes('water') || q.includes('hydration')) {
    return {
      text: `Your cardiovascular telemetry indicates **120 bpm blood pressure** and **12 glasses of water logged**.\n\n**Sodium & Blood Pressure Tips:**\n• Traditional bouillon cubes (Maggi/Knorr) are high in sodium. Consider augmenting flavors with **dawadawa (fermented locust beans)**, ground crayfish, garlic, and scent leaves.\n• Your current hydration is optimal, which assists your kidneys in electrolyte clearance.`,
    };
  }

  // Default fallback response
  return {
    text: `Based on your today's log of **${totalCalories} kcal** across ${mealHistory.length || 1} meal(s), your dietary fiber and macronutrient proportions are in good balance.\n\nI can analyze your meals, recommend dishes with West African food composition data, or help you scale conventional portion units (serving spoons, wraps, cups). What would you like to explore next?`,
  };
}

function InsightsChatScreen({
  user,
  mealHistory = [],
  onBack,
  onOptionsClick,
  onStartCapture,
}) {
  const [messages, setMessages] = useState([
    {
      id: 'msg-1',
      sender: 'assistant',
      text: `Hello, ${user?.name || 'Alex Jemison'}. I've analyzed your data from today.\nHere are some insights:`,
      calorieCard: {
        current: 1250,
        goal: 1920,
        percent: 120,
        heartRate: 140,
        steps: 5234,
      },
      timestamp: 'Just now',
    },
    {
      id: 'msg-2',
      sender: 'user',
      text: 'Any tips to improve my heart rate?',
      timestamp: 'Just now',
    },
    {
      id: 'msg-3',
      sender: 'assistant',
      text: 'Considering your current high heart rate and other factors, perhaps you could benefit from a short meditation session or a lighter exercise. To balance nutrients, try this snack recommendation from your library:',
      foodCards: [
        { name: 'Almonds', emoji: '🥜', kcal: 150 },
        { name: 'Banana', emoji: '🍌', kcal: 80 },
      ],
      timestamp: 'Just now',
    },
  ]);

  const [isThinking, setIsThinking] = useState(false);
  const chatBottomRef = useRef(null);

  const quickPrompts = [
    'How is my protein balance today?',
    'Suggest a light dinner',
    'Any tips to improve heart rate?',
  ];

  const scrollToBottom = () => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, []);

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
          foodCards: responseData.foodCards,
          timestamp: 'Just now',
        },
      ]);
      setTimeout(scrollToBottom, 50);
    }, 700);
  };

  return (
    <div className="w-full max-w-md mx-auto h-[100dvh] max-h-screen flex flex-col bg-[#f7f8fa] select-none overflow-hidden">
      {/* 1. Static Top Header */}
      <header className="flex items-center justify-between pt-3 pb-2.5 px-4 shrink-0 bg-[#f7f8fa] z-10">
        {/* Back Button */}
        <button
          type="button"
          onClick={onBack}
          aria-label="Go back"
          className="w-11 h-11 bg-white hover:bg-gray-50 rounded-full flex items-center justify-center shadow-xs border border-gray-100 transition-transform active:scale-95 text-gray-800"
        >
          <ArrowLeft className="w-5 h-5 stroke-[2]" />
        </button>

        {/* Page Title */}
        <h1 className="text-[20px] sm:text-[22px] font-bold text-gray-900 tracking-tight">
          Chatbot Insights
        </h1>

        {/* Balance placeholder for centered title */}
        <div className="w-11" aria-hidden="true" />
      </header>

      {/* 2. Static Quick Suggestion Topic Chips */}
      <div className="flex gap-2 overflow-x-auto px-4 pb-2.5 scrollbar-none no-scrollbar shrink-0">
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleSendMessage(prompt)}
            className="shrink-0 text-[12px] font-bold text-gray-900 bg-[#e3f79e] hover:bg-[#d5ee8c] px-3.5 py-1.5 rounded-full transition-transform active:scale-95 shadow-2xs"
          >
            + {prompt}
          </button>
        ))}
      </div>

      {/* 3. Independent Scrollable Chat Area */}
      <div className="flex-1 overflow-y-auto px-4 py-1 space-y-4 no-scrollbar scroll-smooth">
        <ChatMessageList messages={messages} isThinking={isThinking} />
        <div ref={chatBottomRef} />
      </div>

      {/* 4. Static Bottom Chat Input Dock (Firmly pinned at bottom, never moves with scroll) */}
      <div className="shrink-0 px-4 pt-2 pb-4 sm:pb-5 bg-[#f7f8fa]">
        <ChatInputDock
          onSendMessage={handleSendMessage}
          onCameraClick={onStartCapture}
          disabled={isThinking}
        />
      </div>
    </div>
  );
}

export default InsightsChatScreen;
