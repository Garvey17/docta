import { apiRequest } from './apiClient.js';

const USE_MOCK =
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_USE_MOCK === 'true') ||
  (typeof process !== 'undefined' && process.env?.VITE_USE_MOCK === 'true');

/**
 * Send a chat message to the Agentic Nutritionist AI.
 * Automatically sends JWT Bearer token in headers via apiRequest.
 * 
 * @param {string} message - User query text
 * @param {Array<{role: string, content: string}>} history - Previous conversation messages
 * @returns {Promise<{reply: string, status: string}>}
 */
export async function sendInsightChatMessage(message, history = []) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 600));
    return {
      reply:
        "Based on your logged meals today, your dietary intake and macronutrients are well balanced. Keep prioritizing lean proteins and rich dietary fiber!",
      status: "success",
    };
  }

  return await apiRequest('/api/v1/insights/chat', {
    method: 'POST',
    body: {
      message,
      history,
    },
  });
}
