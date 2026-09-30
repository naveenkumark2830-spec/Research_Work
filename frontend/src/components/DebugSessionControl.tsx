import React, { useState } from 'react';
import { sessionApi } from '../api/sessionClient';
import { SessionState } from '../types/session';

interface DebugSessionControlProps {
  onSessionLoaded: (state: SessionState) => void;
  activeSessionState: SessionState | null;
}

export const DebugSessionControl: React.FC<DebugSessionControlProps> = ({
  onSessionLoaded,
  activeSessionState,
}) => {
  const [displayName, setDisplayName] = useState('');
  const [userIdInput, setUserIdInput] = useState('');
  const [sessionIdInput, setSessionIdInput] = useState('');
  const [topicInput, setTopicInput] = useState('HDFS Architecture & Data Replication');
  const [error, setError] = useState<string | null>(null);

  const handleQuickLaunch = async () => {
    setError(null);
    try {
      let uid = userIdInput.trim();
      if (!uid) {
        const userRes = await sessionApi.createUser(displayName.trim() || 'Hadoop Student');
        uid = userRes.user.user_id;
        setUserIdInput(uid);
      }
      const state = await sessionApi.createSession(uid, topicInput.trim());
      setSessionIdInput(state.session.session_id);
      onSessionLoaded(state);
    } catch (err: any) {
      setError(err.message || 'Failed to quick launch session');
    }
  };

  const handleCreateUser = async () => {
    if (!displayName.trim()) return;
    setError(null);
    try {
      const res = await sessionApi.createUser(displayName.trim());
      setUserIdInput(res.user.user_id);
      setDisplayName('');
    } catch (err: any) {
      setError(err.message || 'Failed to create user');
    }
  };

  const handleCreateSession = async () => {
    setError(null);
    try {
      let uid = userIdInput.trim();
      if (!uid) {
        const userRes = await sessionApi.createUser('Hadoop Student');
        uid = userRes.user.user_id;
        setUserIdInput(uid);
      }
      const state = await sessionApi.createSession(uid, topicInput.trim());
      setSessionIdInput(state.session.session_id);
      onSessionLoaded(state);
    } catch (err: any) {
      setError(err.message || 'Failed to create session');
    }
  };

  const handleLoadSession = async () => {
    if (!sessionIdInput.trim() || !userIdInput.trim()) {
      setError('To load an EXISTING session, both Session ID and User ID are required. To start a NEW session, click "1-Click Launch Demo Session" above.');
      return;
    }
    setError(null);
    try {
      const state = await sessionApi.getSessionState(sessionIdInput.trim(), userIdInput.trim());
      onSessionLoaded(state);
    } catch (err: any) {
      setError(err.message || 'Failed to load session');
    }
  };

  return (
    <div className="card" style={cardStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0 }}>Session & User Setup (Development/Debug)</h3>
        <button onClick={handleQuickLaunch} style={quickLaunchBtnStyle}>
          ⚡ 1-Click Launch Demo Session
        </button>
      </div>

      {error && <div style={errorStyle}>{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        {/* User Creation / Selection */}
        <div style={boxStyle}>
          <h4>1. User Management</h4>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <input
              type="text"
              placeholder="Display Name (e.g. Alice)"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              style={inputStyle}
            />
            <button onClick={handleCreateUser} style={buttonStyle}>Create User</button>
          </div>
          <div>
            <label style={labelStyle}>Active User ID:</label>
            <input
              type="text"
              placeholder="usr_..."
              value={userIdInput}
              onChange={(e) => setUserIdInput(e.target.value)}
              style={inputStyle}
            />
          </div>
        </div>

        {/* Session Management */}
        <div style={boxStyle}>
          <h4>2. Session Management</h4>
          <div style={{ marginBottom: '0.75rem' }}>
            <label style={labelStyle}>Topic:</label>
            <input
              type="text"
              value={topicInput}
              onChange={(e) => setTopicInput(e.target.value)}
              style={inputStyle}
            />
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <input
              type="text"
              placeholder="Session ID (ses_...)"
              value={sessionIdInput}
              onChange={(e) => setSessionIdInput(e.target.value)}
              style={inputStyle}
            />
            <button onClick={handleLoadSession} style={buttonSecondaryStyle}>Load Existing</button>
          </div>
          <button onClick={handleCreateSession} style={{ ...buttonStyle, width: '100%' }}>
            + Create & Start New Session
          </button>
        </div>
      </div>

      {activeSessionState && (
        <div style={sessionInfoBadgeStyle}>
          <span><strong>Active User:</strong> {activeSessionState.user.display_name} ({activeSessionState.user.user_id})</span>
          <span><strong>Session ID:</strong> {activeSessionState.session.session_id}</span>
          <span><strong>State Version:</strong> v{activeSessionState.state_version}</span>
        </div>
      )}
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

const boxStyle: React.CSSProperties = {
  backgroundColor: '#f9fafb',
  padding: '1rem',
  borderRadius: '8px',
  border: '1px solid #f3f4f6',
};

const inputStyle: React.CSSProperties = {
  flex: 1,
  padding: '0.4rem 0.6rem',
  borderRadius: '6px',
  border: '1px solid #d1d5db',
  fontSize: '0.9rem',
  width: '100%',
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '0.8rem',
  color: '#4b5563',
  marginBottom: '0.2rem',
  fontWeight: 600,
};

const buttonStyle: React.CSSProperties = {
  padding: '0.4rem 0.8rem',
  backgroundColor: '#2563eb',
  color: '#ffffff',
  border: 'none',
  borderRadius: '6px',
  cursor: 'pointer',
  fontWeight: 600,
  fontSize: '0.85rem',
};

const quickLaunchBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  backgroundColor: '#10b981',
  color: '#ffffff',
  border: 'none',
  borderRadius: '6px',
  cursor: 'pointer',
  fontWeight: 700,
  fontSize: '0.875rem',
  boxShadow: '0 2px 4px rgba(16,185,129,0.2)',
};

const buttonSecondaryStyle: React.CSSProperties = {
  ...buttonStyle,
  backgroundColor: '#4b5563',
};

const errorStyle: React.CSSProperties = {
  padding: '0.5rem',
  backgroundColor: '#fee2e2',
  color: '#991b1b',
  borderRadius: '6px',
  marginBottom: '1rem',
  fontSize: '0.875rem',
};

const sessionInfoBadgeStyle: React.CSSProperties = {
  marginTop: '1rem',
  padding: '0.6rem 1rem',
  backgroundColor: '#eff6ff',
  color: '#1e40af',
  borderRadius: '6px',
  display: 'flex',
  justifyContent: 'space-between',
  fontSize: '0.875rem',
  flexWrap: 'wrap',
  gap: '1rem',
};
