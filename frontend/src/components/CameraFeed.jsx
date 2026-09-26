import React, { useState, useRef, useEffect } from 'react';
import { Camera, Upload, Sparkles, AlertCircle } from 'lucide-react';
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
        className={`relative overflow-hidden rounded-[28px] border-2 border-dashed transition-all duration-200 bg-white ${
          dragOver ? 'border-[#84cc16] bg-[#e3f79e]/15' : 'border-gray-200/90 hover:border-gray-300'
        } shadow-xs`}
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
              <div className="w-56 h-56 border-2 border-white/60 rounded-3xl relative">
                <div className="absolute top-0 left-0 w-6 h-6 border-t-4 border-l-4 border-lime-400 -translate-x-1 -translate-y-1 rounded-tl-lg" />
                <div className="absolute top-0 right-0 w-6 h-6 border-t-4 border-r-4 border-lime-400 translate-x-1 -translate-y-1 rounded-tr-lg" />
                <div className="absolute bottom-0 left-0 w-6 h-6 border-b-4 border-l-4 border-lime-400 -translate-x-1 translate-y-1 rounded-bl-lg" />
                <div className="absolute bottom-0 right-0 w-6 h-6 border-b-4 border-r-4 border-lime-400 translate-x-1 translate-y-1 rounded-br-lg" />
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
                className="w-16 h-16 rounded-full bg-white border-4 border-gray-950 flex items-center justify-center shadow-xl active:scale-95 transition-transform"
                title="Capture Photo"
              >
                <div className="w-11 h-11 rounded-full bg-gray-950" />
              </button>
            </div>
          </div>
        ) : (
          <div className="py-10 px-5 flex flex-col items-center justify-center text-center">
            <div className="w-14 h-14 rounded-full bg-[#e3f79e] flex items-center justify-center text-gray-900 mb-3 shadow-xs">
              <Camera className="w-6 h-6 stroke-[2]" />
            </div>

            <h3 className="text-[17px] font-bold text-gray-900 mb-1">
              Capture or Upload Plate
            </h3>
            <p className="text-xs text-gray-500 max-w-xs mb-5">
              Snap a picture of your dish to automatically localize food items and scale portion nutrition.
            </p>

            {cameraError && (
              <div className="mb-4 flex items-center gap-2 text-xs text-amber-800 bg-amber-50 border border-amber-200 px-3 py-2 rounded-xl max-w-sm text-left">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{cameraError}</span>
              </div>
            )}

            <div className="flex flex-wrap items-center justify-center gap-2.5">
              <button
                type="button"
                onClick={startCamera}
                className="inline-flex items-center gap-2 bg-gray-950 hover:bg-black text-white px-5 py-2.5 rounded-full font-bold text-xs shadow-md transition-all active:scale-95"
              >
                <Camera className="w-3.5 h-3.5" />
                Live Camera
              </button>

              <label className="inline-flex items-center gap-2 bg-white hover:bg-gray-50 text-gray-800 border border-gray-200 px-5 py-2.5 rounded-full font-bold text-xs shadow-2xs transition-all cursor-pointer active:scale-95">
                <Upload className="w-3.5 h-3.5" />
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

      {/* Quick Demo Samples */}
      <div className="mt-5">
        <div className="flex items-center justify-between mb-2.5 px-1">
          <span className="text-[12px] font-bold text-gray-800 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-lime-600" />
            Quick Demo Meals
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2.5">
          <button
            type="button"
            onClick={() => onSelectSample(MOCK_ANALYZE_RESPONSE)}
            disabled={isAnalyzing}
            className="flex items-center gap-2.5 p-3 rounded-[20px] border border-gray-100 bg-white hover:border-gray-200 transition-all text-left group shadow-xs active:scale-98"
          >
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-800 font-bold flex items-center justify-center text-base shrink-0 overflow-hidden">
              🍛
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[12px] font-bold text-gray-900 group-hover:text-lime-700 truncate">
                Jollof & Dodo
              </p>
              <p className="text-[10px] text-gray-400 truncate">
                Multi-dish scan
              </p>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onSelectSample(MOCK_ALTERNATIVE_ANALYSIS)}
            disabled={isAnalyzing}
            className="flex items-center gap-2.5 p-3 rounded-[20px] border border-gray-100 bg-white hover:border-gray-200 transition-all text-left group shadow-xs active:scale-98"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-800 font-bold flex items-center justify-center text-base shrink-0 overflow-hidden">
              🍲
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[12px] font-bold text-gray-900 group-hover:text-lime-700 truncate">
                Amala & Egusi
              </p>
              <p className="text-[10px] text-gray-400 truncate">
                Swallow + soup
              </p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}

export default CameraFeed;
