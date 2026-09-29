import { apiRequest } from './apiClient.js';
import { MOCK_ANALYZE_RESPONSE, MOCK_MEAL_HISTORY } from '../data/mockData.js';

const USE_MOCK =
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_USE_MOCK === 'true') ||
  (typeof process !== 'undefined' && process.env?.VITE_USE_MOCK === 'true');

export async function analyzeMeal(imageFile, textPrompt = '') {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 650));
    return MOCK_ANALYZE_RESPONSE;
  }

  const formData = new FormData();
  if (imageFile) {
    formData.append('image', imageFile);
  }
  if (textPrompt) {
    formData.append('prompt', textPrompt);
  }

  return await apiRequest('/api/v1/analyze', {
    method: 'POST',
    body: formData,
  });
}

export async function logMeal(payload) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 450));
    return {
      status: 'success',
      meal_id: `meal_${Date.now().toString(16)}`,
      logged_at: payload.logged_at,
      items_logged: payload.items.length,
      feedback_telemetry_recorded: true,
      message: 'Meal and decision telemetry successfully recorded.',
    };
  }

  return await apiRequest('/api/v1/meals/log', {
    method: 'POST',
    body: payload,
  });
}

export async function fetchMealHistory() {
  if (USE_MOCK) {
    return MOCK_MEAL_HISTORY;
  }
  return await apiRequest('/api/v1/meals/history');
}

export async function fetchDashboardSummary() {
  if (USE_MOCK) {
    return null;
  }
  return await apiRequest('/api/v1/dashboard/summary');
}

export async function fetchDishDetails(dishId) {
  if (USE_MOCK) {
    return null;
  }
  return await apiRequest(`/api/v1/dishes/${encodeURIComponent(dishId)}`);
}

export async function exportTelemetry(format = 'json') {
  return await apiRequest(`/api/v1/telemetry/export?format=${format}`);
}
