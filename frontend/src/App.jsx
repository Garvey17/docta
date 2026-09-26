import React, { useState, useEffect } from 'react';
import RightSidebar from './components/RightSidebar';
import Navbar from './components/Navbar';
import DashboardScreen from './components/DashboardScreen';
import CaptureScreen from './components/CaptureScreen';
import ReviewScreen from './components/ReviewScreen';
import TelemetryModal from './components/TelemetryModal';
import AuthModal from './components/AuthModal';
import { analyzeMeal, logMeal, fetchMealHistory } from './api/mealApi';
import { initializeDraftItems, buildTelemetryPayload } from './store/mealDraftStore';
import { getStoredAuth } from './store/authStore';
import { MOCK_ANALYZE_RESPONSE, MOCK_MEAL_HISTORY } from './data/mockData';
import { CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('UI ErrorBoundary caught an exception:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 text-center">
          <div className="bg-white border border-gray-200 rounded-3xl p-8 max-w-md shadow-xl">
            <div className="w-12 h-12 bg-rose-50 text-rose-600 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-rose-100">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Something went wrong</h2>
            <p className="text-sm text-gray-600 mb-6">
              {this.state.error?.message || 'An unexpected rendering error occurred.'}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false });
                window.location.reload();
              }}
              className="bg-indigo-600 text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-700 shadow-md shadow-indigo-100 transition-colors"
            >
              Reload Application
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

import StatisticScreen from './components/StatisticScreen';
import InsightsChatScreen from './components/InsightsChatScreen';


function App() {
  const [currentScreen, setCurrentScreen] = useState('dashboard');
  const [auth, setAuth] = useState(getStoredAuth());
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showTelemetryModal, setShowTelemetryModal] = useState(false);

  const [draftMeal, setDraftMeal] = useState(null);
  const [mealHistory, setMealHistory] = useState(MOCK_MEAL_HISTORY);
  const [lastTelemetryPayload, setLastTelemetryPayload] = useState(null);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLogging, setIsLogging] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  useEffect(() => {
    // Attempt loading meal history from backend or local mock
    fetchMealHistory().then((data) => {
      if (Array.isArray(data) && data.length > 0) {
        setMealHistory(data);
      }
    });
  }, []);

  const showToast = (message) => {
    setToastMessage(message);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  const handleStartCapture = () => {
    setCurrentScreen('capture');
  };

  const handleAnalyze = async (imageFile, textPrompt = '', presetData = null) => {
    setIsAnalyzing(true);
    try {
      let analysisResult = presetData;
      if (!analysisResult) {
        analysisResult = await analyzeMeal(imageFile, textPrompt);
      }

      const initializedItems = initializeDraftItems(analysisResult.detected_items || []);
      const draft = {
        ...analysisResult,
        items: initializedItems,
        image_url: analysisResult.image_url || (imageFile ? URL.createObjectURL(imageFile) : MOCK_ANALYZE_RESPONSE.image_url),
      };

      setDraftMeal(draft);
      setCurrentScreen('review');
    } catch (err) {
      console.error('Analysis failed:', err);
      // Fallback to deterministic mock
      const initializedItems = initializeDraftItems(MOCK_ANALYZE_RESPONSE.detected_items);
      setDraftMeal({
        ...MOCK_ANALYZE_RESPONSE,
        items: initializedItems,
      });
      setCurrentScreen('review');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUpdateDraftItems = (updatedItems) => {
    setDraftMeal((prev) => ({
      ...prev,
      items: updatedItems,
    }));
  };

  const handleConfirmLogMeal = async (telemetryPayload) => {
    setIsLogging(true);
    try {
      const response = await logMeal(telemetryPayload);
      setLastTelemetryPayload(telemetryPayload);

      // Create local history entry
      const totalCals = telemetryPayload.items.reduce((acc, i) => acc + (i.calories_kcal || 0), 0);
      const totalProt = telemetryPayload.items.reduce((acc, i) => acc + (i.protein_g || 0), 0);
      const totalCarb = telemetryPayload.items.reduce((acc, i) => acc + (i.carbs_g || 0), 0);
      const totalFat = telemetryPayload.items.reduce((acc, i) => acc + (i.fat_g || 0), 0);

      const newHistoryEntry = {
        meal_id: response.meal_id || `meal_${Date.now()}`,
        meal_type: telemetryPayload.meal_type || 'lunch',
        logged_at: telemetryPayload.logged_at || new Date().toISOString(),
        total_calories_kcal: totalCals,
        total_protein_g: totalProt,
        total_carbs_g: totalCarb,
        total_fat_g: totalFat,
        items: telemetryPayload.items.map((i) => ({
          food_name: i.food_name,
          unit_name: i.selected_unit_id,
          quantity: i.selected_quantity,
          gram_weight: i.gram_weight,
          calories_kcal: i.calories_kcal,
        })),
      };

      setMealHistory((prev) => [newHistoryEntry, ...prev]);
      setDraftMeal(null);
      setCurrentScreen('dashboard');
      showToast('Meal successfully recorded! Decisions saved to active learning telemetry.');
    } catch (err) {
      console.error('Failed to log meal:', err);
    } finally {
      setIsLogging(false);
    }
  };

  const handleNavigate = (screenId) => {
    if (screenId === 'review' && !draftMeal) {
      // Auto-load demo meal so review is always accessible even before capturing
      const initializedItems = initializeDraftItems(MOCK_ANALYZE_RESPONSE.detected_items);
      setDraftMeal({
        ...MOCK_ANALYZE_RESPONSE,
        items: initializedItems,
      });
    }
    setCurrentScreen(screenId);
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-[#f7f8fa] font-sans text-gray-900 flex flex-col antialiased">
        {/* Right Sidebar for Desktop */}
        <RightSidebar
          currentScreen={currentScreen}
          onNavigate={handleNavigate}
          hasActiveReview={Boolean(draftMeal)}
        />

        {/* Toast Notification */}
        {toastMessage && (
          <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50 bg-emerald-600 text-white text-xs font-semibold px-4 py-2.5 rounded-2xl shadow-xl flex items-center gap-2 animate-fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-200" />
            <span>{toastMessage}</span>
          </div>
        )}

        {/* Main Application Content Area */}
        <main className="flex-1">
          {currentScreen === 'dashboard' && (
            <DashboardScreen
              user={auth.user}
              mealHistory={mealHistory}
              onStartCapture={handleStartCapture}
              onOpenTelemetry={() => setCurrentScreen('telemetry')}
            />
          )}

          {(currentScreen === 'telemetry' || currentScreen === 'statistics') && (
            <StatisticScreen
              onBack={() => setCurrentScreen('dashboard')}
              onOptionsClick={() => setShowTelemetryModal(true)}
            />
          )}

          {(currentScreen === 'insights' || (currentScreen === 'review' && !draftMeal)) && (
            <InsightsChatScreen
              user={auth.user}
              mealHistory={mealHistory}
              onBack={() => setCurrentScreen('dashboard')}
              onOptionsClick={() => setShowTelemetryModal(true)}
            />
          )}

          {currentScreen === 'capture' && (
            <CaptureScreen
              onAnalyze={handleAnalyze}
              isAnalyzing={isAnalyzing}
              onBack={() => setCurrentScreen('dashboard')}
            />
          )}

          {currentScreen === 'review' && draftMeal && (
            <ReviewScreen
              draft={draftMeal}
              onUpdateDraftItems={handleUpdateDraftItems}
              onConfirmLogMeal={handleConfirmLogMeal}
              onBack={() => setCurrentScreen('capture')}
              isLogging={isLogging}
            />
          )}
        </main>



        {/* Floating Bottom Navigation Bar */}
        {currentScreen !== 'review' && (
          <Navbar
            currentScreen={currentScreen}
            onNavigate={handleNavigate}
            hasActiveReview={Boolean(draftMeal)}
            onOpenAuth={() => setShowAuthModal(true)}
          />
        )}


        {/* Active Learning Telemetry Modal */}
        <TelemetryModal
          isOpen={showTelemetryModal}
          onClose={() => setShowTelemetryModal(false)}
          lastTelemetryPayload={lastTelemetryPayload}
        />

        {/* Auth / Profile Modal */}
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          onAuthSuccess={(u) => setAuth((prev) => ({ ...prev, user: u }))}
        />
      </div>
    </ErrorBoundary>
  );
}

export default App;
