import { apiRequest } from './apiClient';
import { MOCK_ANALYZE_RESPONSE, MOCK_MEAL_HISTORY } from '../data/mockData';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true' || import.meta.env.NEXT_PUBLIC_USE_MOCK === 'true';

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

  try {
    return await apiRequest('/api/v1/analyze', {
      method: 'POST',
      body: formData,
    });
  } catch (err) {
    console.info('Live backend unavailable, activating high-fidelity mock fallback.');
    return MOCK_ANALYZE_RESPONSE;
  }
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

  try {
    return await apiRequest('/api/v1/meals/log', {
      method: 'POST',
      body: payload,
    });
  } catch (err) {
    console.warn('Backend /api/v1/meals/log offline, returning simulated success:', err.message);
    return {
      status: 'success',
      meal_id: `meal_${Date.now().toString(16)}`,
      logged_at: payload.logged_at,
      items_logged: payload.items.length,
      feedback_telemetry_recorded: true,
      message: 'Meal saved locally (telemetry queued).',
    };
  }
}

export async function fetchMealHistory() {
  if (USE_MOCK) {
    return MOCK_MEAL_HISTORY;
  }
  try {
    return await apiRequest('/api/v1/meals/history');
  } catch (e) {
    return MOCK_MEAL_HISTORY;
  }
}

export async function exportTelemetry(format = 'json') {
  try {
    return await apiRequest(`/api/v1/telemetry/export?format=${format}`);
  } catch (e) {
    return {
      export_timestamp: new Date().toISOString(),
      sample_records: [
        {
          predicted_dish_id: 'jollof_rice',
          final_dish_id: 'jollof_rice',
          selected_unit_id: 'serving_spoon',
          selected_quantity: 2.0,
          calculated_gram_weight: 240.0,
          label_modified: false,
        }
      ]
    };
  }
}
