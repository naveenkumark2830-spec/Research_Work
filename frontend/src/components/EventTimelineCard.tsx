import React, { useState, useEffect, useCallback } from 'react';
import { SessionState } from '../types/session';

interface EventTimelineCardProps {
  state: SessionState;
  onError: (err: string) => void;
}

interface TimelineEvent {
  event_id: string;
  sequence_number: number;
  category: string;
  event_type: string;
  logical_timestamp: number;
  state_version: number;
  payload: Record<string, any>;
}

interface TimelineData {
  session_id: string;
  total_events: number;
  current_sequence: number;
  current_logical_time: number;
  current_state_version: number;
  status: string;
  events: TimelineEvent[];
}

const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const EventTimelineCard: React.FC<EventTimelineCardProps> = ({ state, onError }) => {
  const [timeline, setTimeline] = useState<TimelineData | null>(null);
  const { session, user } = state;

  const fetchTimeline = useCallback(async () => {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/sessions/${session.session_id}/timeline`, {
        headers: { 'X-User-Id': user.user_id },
      });
      if (!res.ok) throw new Error('Failed to fetch timeline');
      const data = await res.json();
      setTimeline(data);
    } catch {
      // ignore
    }
  }, [session.session_id, user.user_id]);

  useEffect(() => {
    fetchTimeline();
  }, [fetchTimeline, state.state_version]);

  const handleCursorAction = async (action: 'pause' | 'resume' | 'restart') => {
    try {
      const res = await fetch(`${BASE_URL}/api/v1/sessions/${session.session_id}/cursor/${action}`, {
        method: 'POST',
        headers: { 'X-User-Id': user.user_id },
      });
      if (!res.ok) throw new Error(`Failed to ${action} timeline cursor`);
      fetchTimeline();
    } catch (err: any) {
      onError(err.message || `Failed to ${action} cursor`);
    }
  };

  if (!timeline) return null;

  const currentEvent = timeline.events.find((e) => e.sequence_number === timeline.current_sequence) || timeline.events[timeline.events.length - 1];
  const nextEvent = timeline.events.find((e) => e.sequence_number === timeline.current_sequence + 1);

  return (
    <div style={cardStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 style={{ margin: 0 }}>Development Event Timeline & Playback Cursor</h3>
        <span style={{
          padding: '0.3rem 0.8rem',
          borderRadius: '9999px',
          backgroundColor: timeline.status === 'PLAYING' ? '#d1fae5' : '#fef3c7',
          color: timeline.status === 'PLAYING' ? '#065f46' : '#92400e',
          fontWeight: 700,
          fontSize: '0.85rem'
        }}>
          Playback Status: {timeline.status}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
        <div style={statBoxStyle}>
          <div style={labelStyle}>Total Events</div>
          <div style={valueStyle}>{timeline.total_events}</div>
        </div>
        <div style={statBoxStyle}>
          <div style={labelStyle}>Current Sequence</div>
          <div style={valueStyle}>#{timeline.current_sequence}</div>
        </div>
        <div style={statBoxStyle}>
          <div style={labelStyle}>Logical Time</div>
          <div style={valueStyle}>{timeline.current_logical_time.toFixed(1)}s</div>
        </div>
        <div style={statBoxStyle}>
          <div style={labelStyle}>State Version</div>
          <div style={valueStyle}>v{timeline.current_state_version}</div>
        </div>
      </div>

      {/* Current vs Next Event Indicator */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
        <div style={{ ...highlightBoxStyle, borderLeft: '4px solid #10b981' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#065f46', textTransform: 'uppercase' }}>CURRENT EVENT</div>
          {currentEvent ? (
            <div style={{ fontSize: '0.9rem', marginTop: '0.2rem' }}>
              <strong>#{currentEvent.sequence_number}</strong> {currentEvent.event_type} <span style={{ color: '#6b7280' }}>({currentEvent.category})</span>
            </div>
          ) : (
            <div style={{ color: '#9ca3af', fontStyle: 'italic', fontSize: '0.85rem' }}>No current event</div>
          )}
        </div>

        <div style={{ ...highlightBoxStyle, borderLeft: '4px solid #3b82f6' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#1e40af', textTransform: 'uppercase' }}>NEXT EVENT</div>
          {nextEvent ? (
            <div style={{ fontSize: '0.9rem', marginTop: '0.2rem' }}>
              <strong>#{nextEvent.sequence_number}</strong> {nextEvent.event_type} <span style={{ color: '#6b7280' }}>({nextEvent.category})</span>
            </div>
          ) : (
            <div style={{ color: '#9ca3af', fontStyle: 'italic', fontSize: '0.85rem' }}>End of timeline</div>
          )}
        </div>
      </div>

      {/* Cursor Controls */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
        <button onClick={() => handleCursorAction('resume')} style={{ ...btnStyle, backgroundColor: '#10b981' }}>
          Resume Playback
        </button>
        <button onClick={() => handleCursorAction('pause')} style={{ ...btnStyle, backgroundColor: '#f59e0b' }}>
          Pause Cursor
        </button>
        <button onClick={() => handleCursorAction('restart')} style={{ ...btnStyle, backgroundColor: '#6b7280' }}>
          Restart Timeline
        </button>
      </div>

      {/* Ordered Timeline Stream */}
      <div style={{ maxHeight: '220px', overflowY: 'auto' }}>
        {timeline.events.map((evt) => (
          <div
            key={evt.event_id}
            style={{
              ...evtRowStyle,
              backgroundColor: evt.sequence_number === timeline.current_sequence ? '#ecfdf5' : '#f9fafb',
              borderLeft: evt.sequence_number === timeline.current_sequence ? '4px solid #10b981' : '1px solid #f3f4f6',
            }}
          >
            <div>
              <span style={{ fontWeight: 700, color: '#2563eb', marginRight: '0.5rem' }}>
                #{evt.sequence_number}
              </span>
              <span style={{ fontWeight: 600 }}>{evt.event_type}</span>
              <span style={{ fontSize: '0.75rem', color: '#6b7280', marginLeft: '0.5rem' }}>
                [{evt.category}] • time: {evt.logical_timestamp}s • v{evt.state_version}
              </span>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#4b5563', marginTop: '0.2rem', fontFamily: 'monospace' }}>
              {JSON.stringify(evt.payload)}
            </div>
          </div>
        ))}
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
  padding: '0.6rem',
  borderRadius: '6px',
  border: '1px solid #f3f4f6',
};

const highlightBoxStyle: React.CSSProperties = {
  backgroundColor: '#f9fafb',
  padding: '0.75rem',
  borderRadius: '6px',
  border: '1px solid #e5e7eb',
};

const labelStyle: React.CSSProperties = {
  fontSize: '0.7rem',
  color: '#6b7280',
  fontWeight: 600,
  textTransform: 'uppercase',
};

const valueStyle: React.CSSProperties = {
  fontSize: '1rem',
  fontWeight: 700,
  color: '#111827',
  marginTop: '0.1rem',
};

const btnStyle: React.CSSProperties = {
  padding: '0.45rem 0.9rem',
  color: '#ffffff',
  border: 'none',
  borderRadius: '6px',
  fontWeight: 600,
  fontSize: '0.85rem',
  cursor: 'pointer',
};

const evtRowStyle: React.CSSProperties = {
  padding: '0.5rem 0.75rem',
  borderRadius: '6px',
  marginBottom: '0.4rem',
};
