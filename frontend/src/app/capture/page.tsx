'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Sparkles, MessageSquare, ArrowRight, ArrowLeft, Loader2 } from 'lucide-react';
import { CameraFeed } from '../../components/CameraFeed';
import { useAnalyzeMeal } from '../../hooks/useAnalyzeMeal';
import { useMealDraftStore } from '../../store/mealDraftStore';
import { AnalyzeMealResponse } from '../../types/api';

export default function CapturePage() {
  const router = useRouter();
  const { analyze, loading } = useAnalyzeMeal();
  const { setDraft } = useMealDraftStore();

  const [capturedFile, setCapturedFile] = useState<File | null>(null);
  const [capturedPreview, setCapturedPreview] = useState<string | null>(null);
  const [promptText, setPromptText] = useState<string>('');

  const handleCaptureImage = (file: File, previewUrl: string) => {
    setCapturedFile(file);
    setCapturedPreview(previewUrl);
  };

  const handleSelectSample = (sampleData: AnalyzeMealResponse) => {
    setDraft(sampleData);
    router.push('/review');
  };

  const handleAnalyze = async () => {
    const result = await analyze(capturedFile, promptText);
    setDraft(result, capturedPreview || undefined);
    router.push('/review');
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-gray-900 flex flex-col">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-2xs">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-900 bg-white border border-gray-200 px-3 py-1.5 rounded-xl hover:bg-gray-50 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-full">
            CV Food Scanner
          </span>
        </div>
      </header>

      <main className="flex-1 max-w-4xl mx-auto px-4 py-8 animate-fade-in w-full pb-16">
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
            Scan African Dish & Ingredients
          </h1>
          <p className="text-sm text-gray-500 mt-1 max-w-xl">
            Point your camera at any African or Nigerian dish. The vision system localizes food items, while conventional portion sizing ensures precise nutritional scaling.
          </p>
        </div>

        <div className="space-y-6">
          {capturedPreview ? (
            <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Photo Ready for Analysis
                </span>
                <button
                  type="button"
                  onClick={() => {
                    setCapturedFile(null);
                    setCapturedPreview(null);
                  }}
                  className="text-xs text-indigo-600 hover:text-indigo-700 font-semibold"
                >
                  Retake Photo
                </button>
              </div>

              <div className="relative aspect-[4/3] rounded-xl overflow-hidden bg-slate-900 max-h-96 w-full">
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
              isAnalyzing={loading}
            />
          )}

          <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm">
            <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2 flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-indigo-500" />
              <span>Additional Context Prompt (Optional)</span>
            </label>
            <p className="text-xs text-gray-400 mb-3">
              Add context like extra palm oil, pepper sauce, or specific swallow type.
            </p>
            <textarea
              value={promptText}
              onChange={(e) => setPromptText(e.target.value)}
              placeholder="e.g., Nigerian party jollof with 2 extra fried plantains and peppered beef..."
              rows={2}
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder:text-gray-400 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none transition-all resize-none"
            />
          </div>

          {capturedPreview && (
            <div className="flex justify-end">
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={loading}
                className="inline-flex items-center gap-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-8 py-4 rounded-2xl shadow-lg shadow-indigo-200 hover:shadow-xl transition-all active:scale-98 disabled:opacity-50 text-base"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Running Food Identification...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Analyze Meal & Portions
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
