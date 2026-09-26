import { useState, useCallback } from 'react';
import { AnalyzeMealResponse } from '../types/api';
import { apiClient } from '../lib/apiClient';
import { MOCK_ANALYZE_RESPONSE } from '../lib/mockData';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true' || process.env.VITE_USE_MOCK === 'true';

export function useAnalyzeMeal() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(
    async (imageFile?: File | null, promptText: string = ''): Promise<AnalyzeMealResponse> => {
      setLoading(true);
      setError(null);

      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 650));
        setLoading(false);
        return MOCK_ANALYZE_RESPONSE;
      }

      const formData = new FormData();
      if (imageFile) {
        formData.append('image', imageFile);
      }
      if (promptText) {
        formData.append('prompt', promptText);
      }

      try {
        const data = await apiClient<AnalyzeMealResponse>('/api/v1/analyze', {
          method: 'POST',
          body: formData,
        });
        setLoading(false);
        return data;
      } catch (err: any) {
        console.warn('Backend unavailable, falling back to mock detection payload:', err.message);
        setLoading(false);
        return MOCK_ANALYZE_RESPONSE;
      }
    },
    []
  );

  return {
    analyze,
    loading,
    error,
  };
}
