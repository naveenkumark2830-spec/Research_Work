const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export interface AIMessageResponse {
  session_id: string;
  intent: string;
  action_executed: boolean;
  response: string;
  action?: {
    type: string;
    parameters: Record<string, any>;
  };
  clarification_question?: string;
  error?: {
    code: string;
    message: string;
  };
  simulation_state?: any;
  visualization_state?: any;
  event?: any;
}

export interface JarvisResponse {
  session_id: string;
  intent: string;
  text: string;
  command?: {
    system?: string;
    operation?: string;
    file_size_mb?: number;
    block_size_mb?: number;
    replication_factor?: number;
    datanode_count?: number;
    node_id?: string;
  };
  visual_actions?: Array<{
    type: string;
    target?: string;
    text?: string;
    payload?: Record<string, any>;
  }>;
  should_speak?: boolean;
  should_pause?: boolean;
  should_resume?: boolean;
  simulation_result?: any;
  sources?: string[];
}

export interface VisualizationStep {
  type: string;
  title: string;
  description: string;
  data?: Record<string, any>;
  duration_ms?: number;
}

export interface SimulationAction {
  action: string;
  parameters?: Record<string, any>;
}

export interface TeddyPlan {
  intent: string;
  answer: string;
  voice_text: string;
  simulation_required: boolean;
  simulation_action: SimulationAction;
  visualization: VisualizationStep[];
  sources: string[];
}

export interface TeddyResponse {
  session_id: string;
  user_message: string;
  plan: TeddyPlan;
  simulation_state?: Record<string, any>;
  visualization_scene?: Record<string, any>;
}

export const aiApi = {
  sendTeddyChat: async (
    sessionId: string,
    userId: string,
    message: string
  ): Promise<TeddyResponse> => {
    const response = await fetch(`${BASE_URL}/api/v1/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userId,
      },
      body: JSON.stringify({
        session_id: sessionId,
        user_id: userId,
        message,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Teddy AI service error' }));
      throw new Error(errorData.detail || `HTTP error ${response.status}`);
    }

    return response.json();
  },

  sendMessage: async (
    sessionId: string,
    userId: string,
    message: string,
    visualizationContext?: Record<string, any>
  ): Promise<AIMessageResponse> => {
    const response = await fetch(`${BASE_URL}/api/v1/ai/sessions/${sessionId}/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userId,
      },
      body: JSON.stringify({
        user_id: userId,
        message,
        visualization_context: visualizationContext || {},
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to communicate with AI Orchestrator' }));
      throw new Error(errorData.detail || `HTTP error ${response.status}`);
    }

    return response.json();
  },

  sendJarvisMessage: async (
    sessionId: string,
    userId: string,
    message: string
  ): Promise<JarvisResponse> => {
    const response = await fetch(`${BASE_URL}/api/v1/jarvis/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': userId,
      },
      body: JSON.stringify({
        session_id: sessionId,
        user_id: userId,
        message,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'JARVIS service error' }));
      throw new Error(errorData.detail || `HTTP error ${response.status}`);
    }

    return response.json();
  },

  transcribeAudio: async (audioBlob: Blob): Promise<string> => {
    const formData = new FormData();
    formData.append('file', audioBlob, 'speech.webm');

    const response = await fetch(`${BASE_URL}/api/v1/jarvis/voice/transcribe`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`STT HTTP error ${response.status}`);
    }

    const data = await response.json();
    return data.text || '';
  },

  synthesizeSpeechUrl: (_text?: string): string => {
    return `${BASE_URL}/api/v1/jarvis/voice/speak`;
  },
};

