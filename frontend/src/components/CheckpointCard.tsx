import React, { useState, useEffect, useCallback } from 'react';
import { SessionState, Checkpoint } from '../types/session';
import { sessionApi } from '../api/sessionClient';

interface CheckpointCardProps {
  state: SessionState;
  onStateUpdated: (newState: SessionState) => void;
  onError: (err: string) => void;
}

export const CheckpointCard: React.FC<CheckpointCardProps> = ({
  state,
  onStateUpdated,
  onError,
}) => {
  const [descriptionInput, setDescriptionInput] = useState('');
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const { session, user } = state;

  const fetchCheckpoints = useCallback(async () => {
    try {
      const list = await sessionApi.getCheckpoints(session.session_id, user.user_id);
      setCheckpoints(list);
    } catch {
      // ignore
    }
  }, [session.session_id, user.user_id]);

  useEffect(() => {
    fetchCheckpoints();
  }, [fetchCheckpoints, state.state_version]);

  const handleCreateCheckpoint = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await sessionApi.createCheckpoint(session.session_id, user.user_id, descriptionInput.trim() || 'Manual Checkpoint');
      setDescriptionInput('');
      fetchCheckpoints();
    } catch (err: any) {
      onError(err.message || 'Failed to create checkpoint');
    }
  };

  const handleRestoreCheckpoint = async (checkpointId: string) => {
    try {
      const restoredState = await sessionApi.restoreCheckpoint(session.session_id, checkpointId, user.user_id);
      onStateUpdated(restoredState);
      fetchCheckpoints();
    } catch (err: any) {
      onError(err.message || 'Failed to restore checkpoint');
    }
  };

  return (
    <div style={cardStyle}>
      <h3 style={{ margin: '0 0 1rem 0' }}>State Checkpoints & Restoration</h3>

      <form onSubmit={handleCreateCheckpoint} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Checkpoint Description (e.g. Replication 62%)..."
          value={descriptionInput}
          onChange={(e) => setDescriptionInput(e.target.value)}
          style={{ flex: 1, padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #d1d5db' }}
        />
        <button type="submit" style={{ padding: '0.5rem 1rem', backgroundColor: '#059669', color: '#ffffff', border: 'none', borderRadius: '6px', fontWeight: 600 }}>
          + Save Checkpoint
        </button>
      </form>

      <div style={{ maxHeight: '180px', overflowY: 'auto' }}>
        {checkpoints.length === 0 ? (
          <p style={{ color: '#9ca3af', fontStyle: 'italic', fontSize: '0.875rem' }}>No checkpoints saved yet.</p>
        ) : (
          checkpoints.map((chk) => (
            <div key={chk.checkpoint_id} style={chkItemStyle}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{chk.description}</div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                  Seq #{chk.sequence_number} • {new Date(chk.created_at).toLocaleTimeString()}
                </div>
              </div>
              <button
                onClick={() => handleRestoreCheckpoint(chk.checkpoint_id)}
                style={{ padding: '0.3rem 0.7rem', backgroundColor: '#4f46e5', color: '#ffffff', border: 'none', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' }}
              >
                Restore Snapshot
              </button>
            </div>
          ))
        )}
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

const chkItemStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '0.6rem 0.8rem',
  backgroundColor: '#f9fafb',
  borderRadius: '6px',
  border: '1px solid #f3f4f6',
  marginBottom: '0.5rem',
};
