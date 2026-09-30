import React from 'react';
import { SessionState } from '../types/session';
import { sessionApi } from '../api/sessionClient';

interface SimulationStateCardProps {
  state: SessionState;
  onStateUpdated: (newState: SessionState) => void;
  onError: (err: string) => void;
}

export const SimulationStateCard: React.FC<SimulationStateCardProps> = ({
  state,
  onStateUpdated,
  onError,
}) => {
  const { session, simulation, user } = state;

  const handleAction = async (action: 'start' | 'pause' | 'resume' | 'restart') => {
    try {
      let newState: SessionState;
      if (action === 'start') {
        newState = await sessionApi.startSimulation(session.session_id, user.user_id);
      } else if (action === 'pause') {
        newState = await sessionApi.pauseSimulation(session.session_id, user.user_id);
      } else if (action === 'resume') {
        newState = await sessionApi.resumeSimulation(session.session_id, user.user_id);
      } else {
        newState = await sessionApi.restartSimulation(session.session_id, user.user_id);
      }
      onStateUpdated(newState);
    } catch (err: any) {
      onError(err.message || `Failed to ${action} simulation`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'RUNNING':
        return '#10b981'; // green
      case 'PAUSED':
        return '#f59e0b'; // amber
      case 'COMPLETED':
        return '#3b82f6'; // blue
      case 'FAILED':
        return '#ef4444'; // red
      case 'IDLE':
      default:
        return '#6b7280'; // gray
    }
  };

  return (
    <div style={cardStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0 }}>Hadoop Simulation Engine State</h3>
        <span style={{
          padding: '0.3rem 0.8rem',
          borderRadius: '9999px',
          backgroundColor: getStatusColor(simulation.status) + '22',
          color: getStatusColor(simulation.status),
          fontWeight: 700,
          fontSize: '0.875rem'
        }}>
          {simulation.status}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
        <div style={statBoxStyle}>
          <div style={labelStyle}>Target System</div>
          <div style={valueStyle}>{simulation.system}</div>
        </div>
        <div style={statBoxStyle}>
          <div style={labelStyle}>Current Stage</div>
          <div style={valueStyle}>{simulation.current_stage}</div>
        </div>
        <div style={statBoxStyle}>
          <div style={labelStyle}>Progress</div>
          <div style={valueStyle}>{(simulation.progress * 100).toFixed(0)}%</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{ backgroundColor: '#e5e7eb', height: '8px', borderRadius: '4px', overflow: 'hidden', marginBottom: '1.25rem' }}>
        <div style={{
          backgroundColor: getStatusColor(simulation.status),
          height: '100%',
          width: `${Math.min(100, Math.max(0, simulation.progress * 100))}%`,
          transition: 'width 0.3s ease'
        }} />
      </div>

      {/* Control Actions */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        <button
          onClick={() => handleAction('start')}
          disabled={simulation.status === 'RUNNING'}
          style={{ ...btnStyle, backgroundColor: '#10b981', opacity: simulation.status === 'RUNNING' ? 0.5 : 1 }}
        >
          Start Simulation
        </button>
        <button
          onClick={() => handleAction('pause')}
          disabled={simulation.status !== 'RUNNING'}
          style={{ ...btnStyle, backgroundColor: '#f59e0b', opacity: simulation.status !== 'RUNNING' ? 0.5 : 1 }}
        >
          Pause
        </button>
        <button
          onClick={() => handleAction('resume')}
          disabled={simulation.status !== 'PAUSED'}
          style={{ ...btnStyle, backgroundColor: '#2563eb', opacity: simulation.status !== 'PAUSED' ? 0.5 : 1 }}
        >
          Resume
        </button>
        <button
          onClick={() => handleAction('restart')}
          style={{ ...btnStyle, backgroundColor: '#6b7280' }}
        >
          Restart
        </button>
      </div>
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
  fontSize: '1.1rem',
  fontWeight: 700,
  color: '#111827',
  marginTop: '0.2rem',
};

const btnStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  color: '#ffffff',
  border: 'none',
  borderRadius: '6px',
  fontWeight: 600,
  fontSize: '0.875rem',
  cursor: 'pointer',
};
