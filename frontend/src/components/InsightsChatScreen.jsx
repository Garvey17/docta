import React, { useState, useRef, useEffect } from 'react';
import { X } from 'lucide-react';
import ChatMessageList from './ChatMessageList';
import ChatInputDock from './ChatInputDock';
import { sendInsightChatMessage } from '../api/insightApi';

function InsightsChatScreen({
  user,
  isOpen,
  onClose,
  onStartCapture,
}) {
  const [messages, setMessages] = useState([
    {
      id: 'msg-init',
      sender: 'assistant',
      text: `Hello ${user?.name ? user.name.split(' ')[0] : 'there'}! 👋 I am your AI Clinical Nutritionist for docta.\n\nI have access to your logged meals and nutrition targets. I can analyze your calorie & macro progress, answer dietary questions, or suggest healthy meals tailored to your goals. What would you like to know?`,
      timestamp: 'Just now',
    },
  ]);

  const [isThinking, setIsThinking] = useState(false);
  const chatBottomRef = useRef(null);

  const quickPrompts = [
    'How is my protein balance today?',
    'Suggest a healthy dinner',
    'Am I on track with my calories?',
    'What healthy snacks do you recommend?',
  ];

  const scrollToBottom = () => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) scrollToBottom();
  }, [isOpen]);

  const handleSendMessage = async (text) => {
    if (!text || !text.trim() || isThinking) return;

    const userMsg = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: text.trim(),
      timestamp: 'Just now',
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsThinking(true);
    setTimeout(scrollToBottom, 50);

    try {
      // Build conversation history for the agentic RAG backend
      const history = messages
        .filter((m) => m.text)
        .map((m) => ({
          role: m.sender === 'assistant' ? 'assistant' : 'user',
          content: m.text,
        }));

      const res = await sendInsightChatMessage(text.trim(), history);
      const replyText =
        res?.reply ||
        res?.text ||
        "I have reviewed your nutrition records. How else can I assist with your dietary goals?";

      setMessages((prev) => [
        ...prev,
        {
          id: `msg-res-${Date.now()}`,
          sender: 'assistant',
          text: replyText,
          timestamp: 'Just now',
        },
      ]);
    } catch (err) {
      console.error('Insight Chat error:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: `msg-err-${Date.now()}`,
          sender: 'assistant',
          text: `I'm having trouble connecting to the nutrition service (${err.message || 'Connection error'}). Please try again.`,
          timestamp: 'Just now',
        },
      ]);
    } finally {
      setIsThinking(false);
      setTimeout(scrollToBottom, 50);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[70] flex items-end justify-end bg-black/25 p-0 sm:p-5" onClick={onClose}>
      <section
        role="dialog"
        aria-modal="true"
        aria-label="Chatbot Insights"
        onClick={(event) => event.stopPropagation()}
        className="w-full sm:w-[min(420px,calc(100vw-2.5rem))] h-[100dvh] sm:h-[min(700px,calc(100dvh-2.5rem))] flex flex-col bg-[#f7f8fa] select-none overflow-hidden rounded-3xl sm:border sm:border-gray-200 sm:shadow-2xl animate-fade-in"
      >
        {/* 1. Static Top Header */}
        <header className="flex items-center justify-between pt-3 pb-2.5 px-4 shrink-0 bg-[#f7f8fa] z-10">
          {/* Back Button */}
          <button
            type="button"
            onClick={onClose}
            aria-label="Close insights chat"
            className="w-11 h-11 bg-white hover:bg-gray-50 rounded-full flex items-center justify-center shadow-xs border border-gray-100 transition-transform active:scale-95 text-gray-800"
          >
            <X className="w-5 h-5 stroke-[2]" />
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

        {/* 4. Static Bottom Chat Input Dock */}
        <div className="shrink-0 px-4 pt-2 pb-4 sm:pb-5 bg-[#f7f8fa]">
          <ChatInputDock
            onSendMessage={handleSendMessage}
            onCameraClick={onStartCapture}
            disabled={isThinking}
          />
        </div>
      </section>
    </div>
  );
}

export default InsightsChatScreen;
