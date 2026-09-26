import React, { useState, useRef, useEffect } from 'react';
import { Camera, Upload, RefreshCw, Sparkles, Image as ImageIcon, AlertCircle } from 'lucide-react';
import { MOCK_ANALYZE_RESPONSE, MOCK_ALTERNATIVE_ANALYSIS } from '../data/mockData';

function CameraFeed({ onCaptureImage, onSelectSample, isAnalyzing }) {
  const [streamActive, setStreamActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  // Initialize WebRTC Camera
  const startCamera = async () => {
    setCameraError(null);
    try {
      if (!navigator?.mediaDevices?.getUserMedia) {
        throw new Error('Camera API is not supported in this browser.');
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setStreamActive(true);
    } catch (err) {
      console.warn('Unable to access device camera:', err.message);
      setCameraError('Camera access unavailable. You can upload an image or choose a demo sample.');
      setStreamActive(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setStreamActive(false);
  };

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const captureFrame = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `meal_${Date.now()}.jpg`, { type: 'image/jpeg' });
        const previewUrl = URL.createObjectURL(blob);
        stopCamera();
        onCaptureImage(file, previewUrl);
      }
    }, 'image/jpeg', 0.92);
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const previewUrl = URL.createObjectURL(file);
      onCaptureImage(file, previewUrl);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      const previewUrl = URL.createObjectURL(file);
      onCaptureImage(file, previewUrl);
    }
  };

  return (
    <div className="w-full">
      {/* Viewport Card */}
      <div
        className={`relative overflow-hidden rounded-2xl border-2 border-dashed transition-all duration-200 bg-white ${
          dragOver ? 'border-indigo-500 bg-indigo-50/20' : 'border-gray-200 hover:border-gray-300'
        } shadow-sm`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        {streamActive ? (
          <div className="relative aspect-[4/3] w-full bg-black flex items-center justify-center">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            {/* Viewfinder Target Overlay */}
            <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
              <div className="w-64 h-64 border-2 border-white/60 rounded-3xl relative">
                <div className="absolute top-0 left-0 w-6 h-6 border-t-4 border-l-4 border-indigo-400 -translate-x-1 -translate-y-1 rounded-tl-lg" />
                <div className="absolute top-0 right-0 w-6 h-6 border-t-4 border-r-4 border-indigo-400 translate-x-1 -translate-y-1 rounded-tr-lg" />
                <div className="absolute bottom-0 left-0 w-6 h-6 border-b-4 border-l-4 border-indigo-400 -translate-x-1 translate-y-1 rounded-bl-lg" />
                <div className="absolute bottom-0 right-0 w-6 h-6 border-b-4 border-r-4 border-indigo-400 translate-x-1 translate-y-1 rounded-br-lg" />
              </div>
            </div>

            {/* In-stream Controls */}
            <div className="absolute bottom-4 left-0 right-0 flex items-center justify-center gap-4 z-10 px-4">
              <button
                type="button"
                onClick={stopCamera}
                className="bg-black/60 backdrop-blur-md text-white text-xs px-4 py-2.5 rounded-full hover:bg-black/80 font-medium"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={captureFrame}
                className="w-16 h-16 rounded-full bg-white border-4 border-indigo-600 flex items-center justify-center shadow-xl active:scale-95 transition-transform"
                title="Capture Photo"
              >
                <div className="w-11 h-11 rounded-full bg-indigo-600" />
              </button>
            </div>
          </div>
        ) : (
          <div className="py-12 px-6 flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 mb-4 shadow-sm">
              <Camera className="w-8 h-8" />
            </div>

            <h3 className="text-lg font-bold text-gray-900 mb-1">
              Capture or Upload African Meal
            </h3>
            <p className="text-sm text-gray-500 max-w-sm mb-6">
              Take a photo of your plate or drop an image file here to identify dishes and conventional portions.
            </p>

            {cameraError && (
              <div className="mb-6 flex items-center gap-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 px-3 py-2 rounded-xl max-w-md text-left">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{cameraError}</span>
              </div>
            )}

            <div className="flex flex-wrap items-center justify-center gap-3">
              <button
                type="button"
                onClick={startCamera}
                className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-semibold text-sm shadow-md shadow-indigo-100 transition-all active:scale-95"
              >
                <Camera className="w-4 h-4" />
                Launch Live Camera
              </button>

              <label className="inline-flex items-center gap-2 bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 px-5 py-2.5 rounded-xl font-semibold text-sm shadow-sm transition-all cursor-pointer active:scale-95">
                <Upload className="w-4 h-4" />
                Upload Photo
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Quick Test Samples */}
      <div className="mt-6">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
            Quick Demo Meals (Offline Mock Mode)
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => onSelectSample(MOCK_ANALYZE_RESPONSE)}
            disabled={isAnalyzing}
            className="flex items-center gap-3 p-3.5 rounded-xl border border-gray-200 bg-white hover:border-indigo-300 hover:bg-indigo-50/30 transition-all text-left group shadow-xs"
          >
            <div className="w-12 h-12 rounded-lg bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-xs shrink-0 overflow-hidden">
              <img
                src={MOCK_ANALYZE_RESPONSE.image_url}
                alt="Jollof & Dodo"
                className="w-full h-full object-cover"
                onError={(e) => { e.target.style.display = 'none'; }}
              />
              <span className="p-1">🍛</span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-gray-900 group-hover:text-indigo-600 truncate">
                Jollof Rice + Fried Plantain
              </p>
              <p className="text-xs text-gray-500 truncate">
                Multi-dish detection (2 items detected)
              </p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onSelectSample(MOCK_ALTERNATIVE_ANALYSIS)}
            disabled={isAnalyzing}
            className="flex items-center gap-3 p-3.5 rounded-xl border border-gray-200 bg-white hover:border-indigo-300 hover:bg-indigo-50/30 transition-all text-left group shadow-xs"
          >
            <div className="w-12 h-12 rounded-lg bg-emerald-100 text-emerald-700 font-bold flex items-center justify-center text-xs shrink-0 overflow-hidden">
              <img
                src={MOCK_ALTERNATIVE_ANALYSIS.image_url}
                alt="Amala & Egusi"
                className="w-full h-full object-cover"
                onError={(e) => { e.target.style.display = 'none'; }}
              />
              <span className="p-1">🍲</span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-gray-900 group-hover:text-indigo-600 truncate">
                Amala + Egusi Melon Soup
              </p>
              <p className="text-xs text-gray-500 truncate">
                Swallow + Soup portion units
              </p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}

export default CameraFeed;
