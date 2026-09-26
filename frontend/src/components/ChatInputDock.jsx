import React, { useState } from 'react';
import { Mic, Camera, ArrowUp } from 'lucide-react';

function ChatInputDock({ onSendMessage, onCameraClick, disabled }) {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) {
      if (onCameraClick) onCameraClick();
      return;
    }
    if (disabled) return;
    onSendMessage(inputValue.trim());
    setInputValue('');
  };

  const handleMicClick = () => {
    if (!inputValue) {
      setInputValue('How can I optimize my Nigerian meal portion sizes?');
    }
  };

  return (
    <div className="w-full max-w-[380px] mx-auto bg-white rounded-full p-2 shadow-xl shadow-black/10 border border-gray-100 flex items-center gap-2 select-none">
      {/* 1. Left Circular Microphone Button */}
      <button
        type="button"
        onClick={handleMicClick}
        aria-label="Voice input"
        className="w-10 h-10 rounded-full bg-gray-50 hover:bg-gray-100 flex items-center justify-center text-gray-700 transition-transform active:scale-95 shrink-0"
      >
        <Mic className="w-4 h-4 stroke-[2.2] text-gray-800" />
      </button>

      {/* 2. Form Input Field & Send / Camera Button */}
      <form onSubmit={handleSubmit} className="flex-1 flex items-center justify-between min-w-0">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your message..."
          disabled={disabled}
          className="bg-transparent text-[14px] text-gray-950 placeholder:text-gray-400 outline-none w-full py-1 font-medium px-1"
        />

        {/* 3. Right Action Button (Scan / Camera button or send) */}
        <button
          type="submit"
          disabled={disabled}
          aria-label={inputValue.trim() ? "Send message" : "Scan meal"}
          className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 transition-transform active:scale-95 ${
            inputValue.trim()
              ? 'bg-gradient-to-tr from-[#bef264] to-[#a3e635] text-gray-950 shadow-md shadow-lime-300/40'
              : 'bg-gray-950 hover:bg-black text-white shadow-md shadow-black/20'
          }`}
        >
          {inputValue.trim() ? (
            <ArrowUp className="w-4 h-4 stroke-[2.5]" />
          ) : (
            <Camera className="w-4 h-4 stroke-[2.2] text-white" />
          )}
        </button>
      </form>
    </div>
  );
}

export default ChatInputDock;
