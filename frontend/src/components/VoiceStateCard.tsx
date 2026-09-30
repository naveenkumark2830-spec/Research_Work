// ⚠️ DEPRECATED — not imported by SimulationStudioPage.tsx.
// Superseded by TeddyExplanationOverlay.tsx and FloatingCommandBar.tsx.
import React from 'react';
import { SessionState } from '../types/session';
import { sessionApi } from '../api/sessionClient';

interface VoiceStateCardProps {
  state: SessionState;
  onStateUpdated: (newState: SessionState) => void;
  onError: (err: string) => void;
}

export const VoiceStateCard: React.FC<VoiceStateCardProps> = ({
  state,
  onStateUpdated,
  onError,
}) => {
  const { voice, session, user, simulation } = state;

  const handleBargeIn = async () => {
    try {
      // "Jarvis, stop" triggers pause transition on simulation state and voice interruption
      if (simulation.status === 'RUNNING') {
        const newState = await sessionApi.pauseSimulation(session.session_id, user.user_id);
        onStateUpdated(newState);
      } else {
        onError('Barge-in test requires simulation to be in RUNNING status');
      }
    } catch (err: any) {
      onError(err.message || 'Failed to execute voice interruption');
    }
  };

  return (
    <div style={cardStyle}>
      <h3 style={{ margin: '0 0 1rem 0' }}>Voice Engine State</h3>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
        <div style={statBoxStyle}>
          <div style={labelStyle}>Voice Status</div>
          <div style={valueStyle}>{voice.status}</div>
        </div>
        <div style={statBoxStyle}>
          <div style={labelStyle}>Current Speaker</div>
          <div style={valueStyle}>{voice.current_speaker || 'None'}</div>
        </div>
      </div>

      <div style={{ marginBottom: '1rem', fontSize: '0.875rem' }}>
        <span><strong>Interruption Requested:</strong> {voice.interruption_requested ? 'YES (Barge-in active)' : 'NO'}</span>
      </div>

      <button
        onClick={handleBargeIn}
        disabled={simulation.status !== 'RUNNING'}
        style={{
          padding: '0.5rem 1rem',
          backgroundColor: '#dc2626',
          color: '#ffffff',
          border: 'none',
          borderRadius: '6px',
          fontWeight: 700,
          cursor: 'pointer',
          opacity: simulation.status !== 'RUNNING' ? 0.5 : 1
        }}
      >
        Simulate "Jarvis, Stop" (Voice Interruption)
      </button>
    </div>
  );
};

const cardStyle: React.CSSProperties = {
  backgroundColor: '#ffffff',
  padding: '1.25rem',
  borderRadius: '10px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.06)',
  border: '1px solid #e5e7eb',
  marginBottom: '1.25rem',
};

const statBoxStyle: React.CSSProperties = {
  backgroundColor: '#f9fafb',
  padding: '0.75rem',
  borderRadius: '6px',
  border: '1px solid #f3f4f6',
};

const labelStyle: React.CSSProperties = {
  fontSize: '0.75rem',
  color: '#6b7280',
  fontWeight: 600,
  textTransform: 'uppercase',
};

const valueStyle: React.CSSProperties = {
  fontSize: '1rem',
  fontWeight: 700,
  color: '#111827',
  marginTop: '0.2rem',
};
