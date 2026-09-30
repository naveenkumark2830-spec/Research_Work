export type SessionStatus = 'ACTIVE' | 'PAUSED' | 'COMPLETED' | 'TERMINATED';
export type SimulationStatus = 'IDLE' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'FAILED';
export type SimulationSystem = 'HDFS' | 'MAPREDUCE' | 'YARN' | 'HADOOP_1' | 'HADOOP_2';
export type SimulationStage = 'INITIALIZATION' | 'INPUT' | 'BLOCK_CREATION' | 'REPLICATION' | 'MAP' | 'SHUFFLE' | 'REDUCE' | 'OUTPUT' | 'FAILURE' | 'RECOVERY';
export type VisualizationStatus = 'IDLE' | 'PLAYING' | 'PAUSED';
export type VoiceStatus = 'IDLE' | 'LISTENING' | 'PROCESSING' | 'SPEAKING' | 'INTERRUPTED';
export type LearningMode = 'LEARN' | 'PRACTICE' | 'QUIZ' | 'INTERVIEW' | 'CHALLENGE';
export type MessageRole = 'USER' | 'ASSISTANT' | 'SYSTEM';

export interface User {
  user_id: string;
  display_name: string;
  created_at: string;
  updated_at: string;
  preferences: Record<string, any>;
}

export interface Session {
  session_id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  last_activity_at: string;
  status: SessionStatus;
  current_topic: string;
}

export interface Message {
  message_id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
}

export interface ConversationState {
  current_topic: string;
  current_intent: string | null;
  last_user_message: string | null;
  last_assistant_message: string | null;
  last_question: string | null;
  conversation_turn_count: number;
  recent_messages: Message[];
}

export interface SimulationConfig {
  file_size?: number;
  file_size_mb?: number;
  block_size?: number;
  block_size_mb?: number;
  replication_factor?: number;
  data_node_count?: number;
  datanode_count?: number;
  reducer_count?: number;
  simulation_speed?: number;
  input_size?: number;
  custom_parameters: Record<string, any>;
}

export interface SimulationState {
  system: SimulationSystem;
  scenario_id: string | null;
  status: SimulationStatus;
  current_stage: SimulationStage;
  progress: number;
  started_at: string | null;
  updated_at: string;
  simulation_time: number;
  configuration: SimulationConfig;
}

export interface VisualizationState {
  status: VisualizationStatus;
  active_component: string | null;
  selected_component: string | null;
  selected_block: string | null;
  active_nodes: string[];
  highlighted_nodes: string[];
  current_animation: string | null;
  animation_progress: number;
  camera_state: Record<string, any>;
  viewport_state: Record<string, any>;
}

export interface VoiceState {
  status: VoiceStatus;
  current_speaker: string | null;
  is_listening: boolean;
  is_speaking: boolean;
  interruption_requested: boolean;
  last_transcript: string | null;
}

export interface LearningState {
  current_mode: LearningMode;
  current_topic: string;
  questions_answered: number;
  correct_answers: number;
  incorrect_answers: number;
  mastery: number;
  weak_topics: string[];
  last_assessment_id: string | null;
}

export interface Event {
  event_id: string;
  session_id: string;
  event_type: string;
  timestamp: string;
  sequence_number: number;
  payload: Record<string, any>;
  state_version: number;
}

export interface Checkpoint {
  checkpoint_id: string;
  session_id: string;
  created_at: string;
  sequence_number: number;
  state_snapshot: Record<string, any>;
  description: string;
}

export interface SessionState {
  user: User;
  session: Session;
  conversation: ConversationState;
  simulation: SimulationState;
  visualization: VisualizationState;
  voice: VoiceState;
  learning: LearningState;
  state_version: number;
}
