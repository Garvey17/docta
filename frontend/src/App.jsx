import React, { useState, useEffect } from 'react';
import RightSidebar from './components/RightSidebar';
import Navbar from './components/Navbar';
import DashboardScreen from './components/DashboardScreen';
import CaptureScreen from './components/CaptureScreen';
import ReviewScreen from './components/ReviewScreen';
import TelemetryModal from './components/TelemetryModal';
import AuthScreen from './components/AuthScreen';
import { analyzeMeal, logMeal, fetchMealHistory, fetchDashboardSummary } from './api/mealApi';
import { fetchCurrentUser, logoutUser } from './api/authApi';
import { initializeDraftItems, buildTelemetryPayload } from './store/mealDraftStore';
import { getStoredAuth, clearAuth } from './store/authStore';
import { CheckCircle2, AlertTriangle, MessageCircle } from 'lucide-react';

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
  const [showTelemetryModal, setShowTelemetryModal] = useState(false);
  const [isInsightsOpen, setIsInsightsOpen] = useState(false);

  const [draftMeal, setDraftMeal] = useState(null);
  const [mealHistory, setMealHistory] = useState([]);
  const [dashboardDate, setDashboardDate] = useState(() => new Date());
  const [dashboardData, setDashboardData] = useState(null);
  const [lastTelemetryPayload, setLastTelemetryPayload] = useState(null);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLogging, setIsLogging] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  useEffect(() => {
    const handleUnauthorized = () => {
      clearAuth();
      setAuth({ token: null, user: null, isAuthenticated: false });
      setCurrentScreen('auth');
      showToast('Session expired. Please sign in again.');
    };
    window.addEventListener('docta:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('docta:unauthorized', handleUnauthorized);
  }, []);

  // Validate stored token on startup via GET /api/v1/auth/me
  useEffect(() => {
    const stored = getStoredAuth();
    if (stored.token) {
      fetchCurrentUser()
        .then((userProfile) => {
          if (userProfile && userProfile.id) {
            setAuth({ token: stored.token, user: userProfile, isAuthenticated: true });
          } else {
            clearAuth();
            setAuth({ token: null, user: null, isAuthenticated: false });
          }
        })
        .catch(() => {
          clearAuth();
          setAuth({ token: null, user: null, isAuthenticated: false });
        });
    }
  }, []);

  useEffect(() => {
    if (auth?.isAuthenticated) {
      fetchMealHistory()
        .then((data) => {
          if (Array.isArray(data)) {
            setMealHistory(data);
          }
        })
        .catch((err) => {
          console.error('Failed to load meal history:', err);
          showToast(`Backend connection notice: ${err.message}`);
        });

      fetchDashboardSummary()
        .then((summary) => {
          if (summary) {
            setDashboardData(summary);
          }
        })
        .catch((err) => {
          console.debug('Dashboard summary note:', err);
        });
    }
  }, [auth?.isAuthenticated]);

  const showToast = (message) => {
    setToastMessage(message);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  const handleStartCapture = () => {
    setIsInsightsOpen(false);
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
        image_url: analysisResult.image_url || (imageFile ? URL.createObjectURL(imageFile) : null),
      };

      setDraftMeal(draft);
      setCurrentScreen('review');
    } catch (err) {
      console.error('Analysis failed:', err);
      showToast(`Analysis failed: ${err.message}`);
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
        meal_id: response.meal_id || response.id || `meal_${Date.now()}`,
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
      showToast(`Failed to log meal: ${err.message}`);
    } finally {
      setIsLogging(false);
    }
  };

  const handleNavigate = (screenId) => {
    if (screenId === 'review' && !draftMeal) {
      showToast('No active meal capture to review. Please capture a plate first.');
      setCurrentScreen('capture');
      return;
    }
    setCurrentScreen(screenId);
  };

  const handleLogout = async () => {
    try {
      await logoutUser();
    } catch (e) {
      console.warn('Backend logout failed:', e);
    }
    clearAuth();
    setAuth({ token: null, user: null, isAuthenticated: false });
    setCurrentScreen('auth');
    showToast('Logged out successfully');
  };

  const handleAuthSuccess = (userData, token) => {
    const activeToken = token || localStorage.getItem('docta_auth_token');
    setAuth({ token: activeToken, user: userData, isAuthenticated: true });
    setCurrentScreen('dashboard');
    showToast(`Welcome, ${userData.name || 'User'}!`);
  };

  // If user is logged out or auth screen is requested
  if (!auth?.isAuthenticated || currentScreen === 'auth') {
    return (
      <ErrorBoundary>
        <AuthScreen onAuthSuccess={handleAuthSuccess} />
      </ErrorBoundary>
    );
  }

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
              selectedDate={dashboardDate}
              onDateChange={setDashboardDate}
              dashboardData={dashboardData}
              onStartCapture={handleStartCapture}
              onOpenTelemetry={() => setCurrentScreen('telemetry')}
              onLogout={handleLogout}
            />
          )}

          {(currentScreen === 'telemetry' || currentScreen === 'statistics') && (
            <StatisticScreen
              user={auth.user}
              mealHistory={mealHistory}
              onBack={() => setCurrentScreen('dashboard')}
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



        {/* Floating Bottom Navigation Bar (Shown on Dashboard & Statistics) */}
        {currentScreen !== 'review' && (
          <Navbar
            currentScreen={currentScreen}
            onNavigate={handleNavigate}
          />
        )}

        {currentScreen !== 'capture' && currentScreen !== 'review' && (
          <button
            type="button"
            onClick={() => setIsInsightsOpen(true)}
            aria-label="Open AI insights chat"
            className="fixed bottom-[88px] right-5 lg:right-28 z-[65] flex h-14 w-14 items-center justify-center rounded-full bg-gray-950 text-white shadow-xl shadow-black/20 transition-transform hover:scale-105 active:scale-95"
          >
            <MessageCircle className="h-6 w-6" strokeWidth={2} />
            <span className="absolute -right-0.5 -top-0.5 h-3.5 w-3.5 rounded-full border-2 border-white bg-lime-400" />
          </button>
        )}

        <InsightsChatScreen
          user={auth.user}
          mealHistory={mealHistory}
          isOpen={isInsightsOpen}
          onClose={() => setIsInsightsOpen(false)}
          onStartCapture={handleStartCapture}
        />


        {/* Active Learning Telemetry Modal */}
        <TelemetryModal
          isOpen={showTelemetryModal}
          onClose={() => setShowTelemetryModal(false)}
          lastTelemetryPayload={lastTelemetryPayload}
        />
      </div>
    </ErrorBoundary>
  );
}

export default App;
