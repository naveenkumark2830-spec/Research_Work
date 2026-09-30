import { SessionState } from '../types/session';

const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

async function request<T>(path: string, options: RequestInit = {}, userId?: string): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (userId) {
    headers['X-User-Id'] = userId;
  }

  const response = await fetch(`${BASE_URL}/api/v1/simulation/hdfs${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(errorData.detail || `HTTP error ${response.status}`);
  }

  return response.json();
}

export interface HDFSClusterConfigPayload {
  file_size_mb: number;
  block_size_mb: number;
  replication_factor: number;
  data_node_count: number;
  reducer_count: number;
  simulation_speed: number;
}

export const hdfsApi = {
  updateConfig: (sessionId: string, userId: string, config: HDFSClusterConfigPayload): Promise<SessionState> =>
    request(`/sessions/${sessionId}/config`, {
      method: 'PUT',
      body: JSON.stringify({ user_id: userId, config }),
    }, userId),

  setSpeed: (sessionId: string, userId: string, speed: number): Promise<SessionState> =>
    request(`/sessions/${sessionId}/speed`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, speed }),
    }, userId),

  writeFile: (sessionId: string, userId: string, path: string, sizeMb: number): Promise<SessionState> =>
    request(`/sessions/${sessionId}/write`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, path, size_bytes: sizeMb * 1024 * 1024 }),
    }, userId),

  addDatanode: (sessionId: string, userId: string): Promise<SessionState> =>
    request(`/sessions/${sessionId}/datanodes`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    }, userId),

  removeDatanode: (sessionId: string, userId: string, nodeId: string): Promise<SessionState> =>
    request(`/sessions/${sessionId}/datanodes/${nodeId}`, {
      method: 'DELETE',
    }, userId),

  killDatanode: (sessionId: string, userId: string, nodeId: string): Promise<SessionState> =>
    request(`/sessions/${sessionId}/datanodes/${nodeId}/kill`, {
      method: 'POST',
    }, userId),

  recoverDatanode: (sessionId: string, userId: string, nodeId: string): Promise<SessionState> =>
    request(`/sessions/${sessionId}/datanodes/${nodeId}/recover`, {
      method: 'POST',
    }, userId),

  restartSimulation: (sessionId: string, userId: string): Promise<SessionState> =>
    request(`/sessions/${sessionId}/restart`, {
      method: 'POST',
    }, userId),
};
