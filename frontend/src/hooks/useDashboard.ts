import { useState, useEffect, useCallback } from 'react';
import { MealHistoryRecord } from '../types/api';
import { apiClient } from '../lib/apiClient';
import { MOCK_MEAL_HISTORY } from '../lib/mockData';

export function useDashboard() {
  const [history, setHistory] = useState<MealHistoryRecord[]>(MOCK_MEAL_HISTORY);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiClient<MealHistoryRecord[]>('/api/v1/meals/history');
      if (Array.isArray(data) && data.length > 0) {
        setHistory(data);
      }
    } catch {
      setHistory(MOCK_MEAL_HISTORY);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const addMealToHistory = (newMeal: MealHistoryRecord) => {
    setHistory((prev) => [newMeal, ...prev]);
  };

  const dailyTotals = history.reduce(
    (acc, m) => {
      acc.calories += m.total_calories_kcal || 0;
      acc.protein += m.total_protein_g || 0;
      acc.carbs += m.total_carbs_g || 0;
      acc.fat += m.total_fat_g || 0;
      return acc;
    },
    { calories: 0, protein: 0, carbs: 0, fat: 0 }
  );

  return {
    history,
    dailyTotals,
    loading,
    refresh: fetchHistory,
    addMealToHistory,
  };
}
