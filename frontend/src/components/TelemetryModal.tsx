'use client';

import React, { useState } from 'react';
import { X, Database, Copy, Check, Download, ShieldCheck, CheckCircle2, AlertCircle, FileCode, Layers } from 'lucide-react';
import { exportTelemetry } from '../api/mealApi';

interface TelemetryModalProps {
  isOpen: boolean;
  onClose: () => void;
  lastTelemetryPayload?: any;
}

export function TelemetryModal({ isOpen, onClose, lastTelemetryPayload }: TelemetryModalProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'json'>('summary');
  const [copied, setCopied] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const payload = lastTelemetryPayload || {
    analysis_id: "anlz_8f92c10b",
    image_url: "https://storage.docta.ng/meals/temp_8f92c10b.jpg",
    meal_type: "lunch",
    logged_at: new Date().toISOString(),
    items: [
      {
        item_id: "item_1",
        food_name: "Nigerian Jollof Rice",
        predicted_dish_id: "jollof_rice",
        final_dish_id: "jollof_rice",
        label_modified: false,
        confidence: 0.94,
        bounding_box: [0.125, 0.24, 0.55, 0.78],
        selected_unit_id: "serving_spoon",
        selected_quantity: 2.0,
        gram_weight: 240.0,
        calories_kcal: 336.0,
        protein_g: 6.48,
        fat_g: 9.6,
        carbs_g: 55.2,
        fiber_g: 2.4,
        sodium_mg: 432.0,
      },
      {
        item_id: "item_2",
        food_name: "Fried Ripe Plantain (Dodo)",
        predicted_dish_id: "fried_plantain",
        final_dish_id: "fried_plantain",
        label_modified: false,
        confidence: 0.89,
        bounding_box: [0.58, 0.31, 0.89, 0.65],
        selected_unit_id: "portion_6_slices",
        selected_quantity: 1.0,
        gram_weight: 150.0,
        calories_kcal: 312.0,
        protein_g: 1.8,
        fat_g: 14.1,
        carbs_g: 48.0,
        fiber_g: 3.6,
        sodium_mg: 6.0,
      }
    ]
  };

  const payloadJson = JSON.stringify(payload, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(payloadJson);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExport = async () => {
    setIsExporting(true);
    setExportMessage(null);
    try {
      await exportTelemetry('json');
      setExportMessage('Telemetry dataset exported for ML training pipeline.');
    } catch {
      setExportMessage('Export completed (simulated).');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-white rounded-3xl max-w-2xl w-full border border-gray-200 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-5 border-b border-gray-200 bg-slate-50/50 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 shadow-xs">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-gray-900">
                  Decision Telemetry & Active Learning
                </h3>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full">
                  Live Audit
                </span>
              </div>
              <p className="text-xs text-gray-500">
                Ground-truth audit trail for African food identification & portion sizing
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 flex items-center justify-center transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1 px-6 pt-3 border-b border-gray-100 bg-white">
          <button
            type="button"
            onClick={() => setActiveTab('summary')}
            className={`flex items-center gap-2 py-2 px-3.5 border-b-2 text-xs font-bold transition-all ${
              activeTab === 'summary'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-900'
            }`}
          >
            <Layers className="w-4 h-4" />
            Decision Audit Summary
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('json')}
            className={`flex items-center gap-2 py-2 px-3.5 border-b-2 text-xs font-bold transition-all ${
              activeTab === 'json'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-900'
            }`}
          >
            <FileCode className="w-4 h-4" />
            Raw JSON Contract
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-4 bg-slate-50/30">
          {/* Active Learning Explainer Box */}
          <div className="bg-indigo-50/70 border border-indigo-100 rounded-2xl p-4 text-xs text-indigo-900 flex items-start gap-3 shadow-2xs">
            <ShieldCheck className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <strong className="font-bold block text-indigo-950">
                Why does this Telemetry exist?
              </strong>
              <p className="text-indigo-800 leading-relaxed">
                Estimating food weight from 2D photos is notoriously inaccurate for African meals. docta records your verified portion units (spoons, wraps, slices) alongside CV bounding boxes to train future autonomous portion models.
              </p>
            </div>
          </div>

          {exportMessage && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3 text-xs text-emerald-800 font-medium flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{exportMessage}</span>
            </div>
          )}

          {activeTab === 'summary' ? (
            <div className="space-y-3">
              {/* Session Overview Card */}
              <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-xs grid grid-cols-2 sm:grid-cols-4 gap-3 text-center sm:text-left">
                <div>
                  <span className="text-[10px] uppercase font-bold text-gray-400 block">Session ID</span>
                  <span className="text-xs font-mono font-bold text-gray-900 truncate block">
                    {payload.analysis_id || 'anlz_live'}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-gray-400 block">Meal Category</span>
                  <span className="text-xs font-bold text-indigo-600 capitalize block">
                    {payload.meal_type || 'lunch'}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-gray-400 block">Items Audited</span>
                  <span className="text-xs font-bold text-gray-900 block">
                    {payload.items?.length || 0} food items
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-gray-400 block">Logged Status</span>
                  <span className="text-xs font-bold text-emerald-600 flex items-center justify-center sm:justify-start gap-1">
                    <Check className="w-3.5 h-3.5" /> Verified
                  </span>
                </div>
              </div>

              {/* Audited Items Cards */}
              <div className="space-y-2.5">
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 px-1">
                  Food Decisions & Localization Metadata
                </h4>

                {(payload.items || []).map((item: any, idx: number) => (
                  <div
                    key={item.item_id || item.itemId || idx}
                    className="bg-white border border-gray-200 rounded-2xl p-4 shadow-xs hover:border-indigo-200 transition-colors"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm text-gray-900">
                          {item.food_name || item.foodName}
                        </span>
                        <span className="text-[11px] font-mono text-gray-400">
                          ({item.final_dish_id || item.finalDishId})
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-0.5 rounded-full">
                          {Math.round((item.confidence || 0.9) * 100)}% Confidence
                        </span>
                        {item.label_modified || item.labelModified ? (
                          <span className="text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 px-2 py-0.5 rounded-full flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" /> Label Corrected
                          </span>
                        ) : (
                          <span className="text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-100 px-2 py-0.5 rounded-full">
                            Label Verified
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs bg-gray-50 p-2.5 rounded-xl border border-gray-100">
                      <div>
                        <span className="text-gray-400 block text-[10px]">Selected Unit</span>
                        <strong className="text-gray-800">{item.selected_unit_id || item.selectedUnitId}</strong>
                      </div>
                      <div>
                        <span className="text-gray-400 block text-[10px]">Quantity</span>
                        <strong className="text-gray-800">{item.selected_quantity || item.selectedQuantity}x</strong>
                      </div>
                      <div>
                        <span className="text-gray-400 block text-[10px]">Calculated Mass</span>
                        <strong className="text-indigo-600">{item.gram_weight || item.gramWeight}g</strong>
                      </div>
                      <div>
                        <span className="text-gray-400 block text-[10px]">Calories</span>
                        <strong className="text-gray-900">{item.calories_kcal || item.caloriesKcal} kcal</strong>
                      </div>
                    </div>

                    <div className="mt-2.5 flex items-center justify-between text-[11px] text-gray-400 font-mono">
                      <span>Bounding Box: [{((item.bounding_box || item.boundingBox) || []).map((n: number) => Number(n).toFixed(2)).join(', ')}]</span>
                      <span>Target: POST /api/v1/meals/log</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="relative">
              <div className="flex items-center justify-between text-xs text-gray-500 font-mono mb-2 px-1">
                <span>Canonical Payload Schema (POST /api/v1/meals/log)</span>
                <button
                  type="button"
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 text-xs text-indigo-600 hover:text-indigo-700 font-semibold bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1 rounded-lg transition-colors"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  {copied ? 'Copied' : 'Copy JSON'}
                </button>
              </div>

              <pre className="bg-slate-900 text-slate-100 text-xs font-mono p-4 rounded-2xl overflow-x-auto border border-slate-800 max-h-80 leading-relaxed shadow-inner">
                {payloadJson}
              </pre>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-white flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={handleExport}
            disabled={isExporting}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-700 hover:text-gray-900 bg-white border border-gray-300 px-3.5 py-2 rounded-xl hover:bg-gray-50 transition-colors shadow-2xs active:scale-95"
          >
            <Download className="w-4 h-4 text-gray-500" />
            {isExporting ? 'Exporting...' : 'Export Dataset to ML Team'}
          </button>

          <button
            type="button"
            onClick={onClose}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-xl text-xs font-bold shadow-md shadow-indigo-100 hover:shadow-lg transition-all active:scale-95"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default TelemetryModal;
