import React, { useState } from 'react';
import { ArrowLeft, MoreVertical, Sparkles, MessageSquare, ArrowRight, Loader2 } from 'lucide-react';
import CameraFeed from './CameraFeed';

function CaptureScreen({ onAnalyze, isAnalyzing, onBack, onOptionsClick }) {
  const [capturedFile, setCapturedFile] = useState(null);
  const [capturedPreview, setCapturedPreview] = useState(null);
  const [promptText, setPromptText] = useState('');

  const handleCaptureImage = (file, previewUrl) => {
    setCapturedFile(file);
    setCapturedPreview(previewUrl);
  };

  const handleSelectSample = (sampleData) => {
    onAnalyze(null, '', sampleData);
  };

  const handleSubmitAnalysis = () => {
    if (!capturedFile) return;
    onAnalyze(capturedFile, promptText);
  };

  return (
    <div className="max-w-md mx-auto px-4 pt-2 pb-28 animate-fade-in select-none">
      {/* 1. Top Header */}
      <header className="flex items-center justify-between pt-2 pb-5 px-1">
        <button
          type="button"
          onClick={onBack || (() => window.history.back())}
          aria-label="Go back"
          className="w-11 h-11 bg-white hover:bg-gray-50 rounded-full flex items-center justify-center shadow-xs border border-gray-100 transition-transform active:scale-95 text-gray-800"
        >
          <ArrowLeft className="w-5 h-5 stroke-[2]" />
        </button>

        <h1 className="text-[20px] sm:text-[22px] font-bold text-gray-900 tracking-tight">
          Scan Meal
        </h1>

        <button
          type="button"
          onClick={onOptionsClick}
          aria-label="More options"
          className="w-11 h-11 bg-white hover:bg-gray-50 rounded-full flex items-center justify-center shadow-xs border border-gray-100 transition-transform active:scale-95 text-gray-800"
        >
          <MoreVertical className="w-5 h-5 stroke-[2]" />
        </button>
      </header>

      {/* 2. Camera Viewfinder or Photo Preview */}
      <div className="space-y-4">
        {capturedPreview ? (
          <div className="bg-white rounded-[28px] p-5 shadow-xs border border-gray-100/60">
            <div className="flex items-center justify-between mb-3 px-1">
              <span className="text-[12px] font-bold text-gray-900 bg-[#e3f79e] px-3 py-1 rounded-full">
                Ready for Analysis
              </span>
              <button
                type="button"
                onClick={() => {
                  setCapturedFile(null);
                  setCapturedPreview(null);
                }}
                className="text-[12px] text-gray-500 hover:text-gray-900 font-semibold"
              >
                Retake
              </button>
            </div>

            <div className="relative aspect-[4/3] rounded-[20px] overflow-hidden bg-slate-900 w-full shadow-inner">
              <img
                src={capturedPreview}
                alt="Captured Meal"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        ) : (
          <CameraFeed
            onCaptureImage={handleCaptureImage}
            onSelectSample={handleSelectSample}
            isAnalyzing={isAnalyzing}
          />
        )}

        {/* 3. Optional Context Input */}
        <div className="bg-white rounded-[28px] p-5 shadow-xs border border-gray-100/60">
          <label className="block text-[13px] font-bold text-gray-900 mb-1.5 flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-gray-700" />
            <span>Additional Context (Optional)</span>
          </label>
          <p className="text-[11px] text-gray-400 mb-3">
            Add context like extra oil, spicy stew, condiments, or swallow type.
          </p>
          <textarea
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            placeholder="e.g. Nigerian party jollof with extra plantains and beef..."
            rows={2}
            className="w-full bg-[#f8f9fa] border border-gray-100 rounded-2xl px-4 py-3 text-xs sm:text-sm text-gray-900 placeholder:text-gray-400 focus:bg-white focus:ring-2 focus:ring-lime-400 outline-none transition-all resize-none"
          />
        </div>

        {/* 4. Action Button */}
        {capturedPreview && (
          <div className="pt-2">
            <button
              type="button"
              onClick={handleSubmitAnalysis}
              disabled={isAnalyzing}
              className="w-full inline-flex items-center justify-center gap-2 bg-gray-950 hover:bg-black text-white font-bold py-4 rounded-full shadow-lg shadow-black/20 hover:shadow-xl transition-all active:scale-98 disabled:opacity-50 text-[15px]"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Running Vision Analysis...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-[#bef264]" />
                  Analyze Dish & Portions
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default CaptureScreen;
