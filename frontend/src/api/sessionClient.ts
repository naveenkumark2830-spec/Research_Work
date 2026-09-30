import { User, SessionState, Checkpoint, Event } from '../types/session';

const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

async function request<T>(path: string, options: RequestInit = {}, userId?: string): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (userId) {
    headers['X-User-Id'] = userId;
  }

  const response = await fetch(`${BASE_URL}/api/v1${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(errorData.detail || `HTTP error ${response.status}`);
  }

  return response.json();
}

export const sessionApi = {
  createUser: (displayName: string): Promise<{ user: User }> =>
    request('/users', {
      method: 'POST',
      body: JSON.stringify({ display_name: displayName }),
    }),

  createSession: (userId: string, currentTopic?: string): Promise<SessionState> =>
    request('/sessions', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, current_topic: currentTopic }),
    }),

  getSessionState: (sessionId: string, userId: string): Promise<SessionState> =>
    request(`/sessions/${sessionId}/state`, { method: 'GET' }, userId),

  startSimulation: (sessionId: string, userId: string): Promise<SessionState> =>
    request(`/sessions/${sessionId}/start`, { method: 'POST' }, userId),

  pauseSimulation: (sessionId: string, userId: string): Promise<SessionState> =>
    request(`/sessions/${sessionId}/pause`, { method: 'POST' }, userId),

  resumeSimulation: (sessionId: string, userId: string): Promise<SessionState> =>
    request(`/sessions/${sessionId}/resume`, { method: 'POST' }, userId),

  restartSimulation: (sessionId: string, userId: string): Promise<SessionState> =>
    request(`/sessions/${sessionId}/restart`, { method: 'POST' }, userId),

  createCheckpoint: (sessionId: string, userId: string, description?: string): Promise<Checkpoint> =>
    request(`/sessions/${sessionId}/checkpoint`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, description: description || 'User state checkpoint' }),
    }, userId),

  getCheckpoints: (sessionId: string, userId: string): Promise<Checkpoint[]> =>
    request(`/sessions/${sessionId}/checkpoints`, { method: 'GET' }, userId),

  restoreCheckpoint: (sessionId: string, checkpointId: string, userId: string): Promise<SessionState> =>
    request(`/sessions/${sessionId}/restore/${checkpointId}`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    }, userId),

  getEvents: (sessionId: string, userId: string): Promise<Event[]> =>
    request(`/sessions/${sessionId}/events`, { method: 'GET' }, userId),

  addMessage: (sessionId: string, userId: string, content: string, role: string = 'USER'): Promise<SessionState> =>
    request(`/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, role, content }),
    }, userId),
};
