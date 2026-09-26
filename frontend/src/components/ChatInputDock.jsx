import React, { useState } from 'react';
import { ArrowUp, Sparkles } from 'lucide-react';

function ChatInputDock({ onSendMessage, disabled }) {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim() || disabled) return;
    onSendMessage(inputValue.trim());
    setInputValue('');
  };

  return (
    <div className="fixed bottom-20 sm:bottom-24 left-0 right-0 z-40 flex justify-center px-3 sm:px-6 pointer-events-none">
      <form
        onSubmit={handleSubmit}
        className="pointer-events-auto bg-white/95 backdrop-blur-md rounded-full pl-4 sm:pl-5 pr-1.5 py-1.5 shadow-2xl shadow-black/15 border border-gray-100 flex items-center justify-between w-full max-w-[380px] sm:max-w-2xl gap-2 transition-all focus-within:border-lime-400 focus-within:ring-2 focus-within:ring-lime-300/30"
      >
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask Docta AI about meals & macros..."
          disabled={disabled}
          className="bg-transparent text-[13px] text-gray-900 placeholder:text-gray-400 outline-none w-full py-1 font-medium"
        />

        <button
          type="submit"
          disabled={!inputValue.trim() || disabled}
          aria-label="Send message"
          className={`w-8 h-8 rounded-full flex items-center justify-center transition-all active:scale-95 ${
            inputValue.trim() && !disabled
              ? 'bg-gray-950 hover:bg-black text-white shadow-sm'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
          }`}
        >
          <ArrowUp className="w-4 h-4 stroke-[2.5]" />
        </button>
      </form>
    </div>
  );
}

export default ChatInputDock;
