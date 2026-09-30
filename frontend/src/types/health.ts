export type HealthStatus = 'pending' | 'connected' | 'unavailable';

export interface HealthResponse {
  status: string;
  service: string;
}
