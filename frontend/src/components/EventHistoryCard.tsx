import React, { useState, useEffect, useCallback } from 'react';
import { SessionState, Event } from '../types/session';
import { sessionApi } from '../api/sessionClient';

interface EventHistoryCardProps {
  state: SessionState;
}

export const EventHistoryCard: React.FC<EventHistoryCardProps> = ({ state }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const { session, user } = state;

  const fetchEvents = useCallback(async () => {
    try {
      const list = await sessionApi.getEvents(session.session_id, user.user_id);
      setEvents(list);
    } catch {
      // ignore
    }
  }, [session.session_id, user.user_id]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents, state.state_version]);

  return (
    <div style={cardStyle}>
      <h3 style={{ margin: '0 0 1rem 0' }}>State Engine Event History (Audit Trail)</h3>

      <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
        {events.length === 0 ? (
          <p style={{ color: '#9ca3af', fontStyle: 'italic', fontSize: '0.875rem' }}>No events recorded.</p>
        ) : (
          events.map((evt) => (
            <div key={evt.event_id} style={evtItemStyle}>
              <div>
                <span style={{ fontWeight: 700, color: '#3b82f6', marginRight: '0.5rem' }}>
                  #{evt.sequence_number}
                </span>
                <span style={{ fontWeight: 600 }}>{evt.event_type}</span>
                <span style={{ fontSize: '0.75rem', color: '#6b7280', marginLeft: '0.5rem' }}>
                  (v{evt.state_version}) • {new Date(evt.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div style={{ fontSize: '0.75rem', color: '#4b5563', marginTop: '0.2rem', fontFamily: 'monospace' }}>
                {JSON.stringify(evt.payload)}
              </div>
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

const evtItemStyle: React.CSSProperties = {
  padding: '0.5rem 0.75rem',
  backgroundColor: '#f9fafb',
  borderRadius: '6px',
  border: '1px solid #f3f4f6',
  marginBottom: '0.4rem',
  fontSize: '0.85rem',
};
