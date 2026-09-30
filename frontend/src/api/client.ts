import { HealthResponse } from '../types/health';

const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export async function checkBackendHealth(): Promise<HealthResponse> {
  const response = await fetch(`${BASE_URL}/api/v1/health`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}
