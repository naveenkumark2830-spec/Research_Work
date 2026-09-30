import React, { useState } from 'react';
import { SessionState } from '../types/session';
import { sessionApi } from '../api/sessionClient';

interface ConversationCardProps {
  state: SessionState;
  onStateUpdated: (newState: SessionState) => void;
  onError: (err: string) => void;
}

export const ConversationCard: React.FC<ConversationCardProps> = ({
  state,
  onStateUpdated,
  onError,
}) => {
  const [inputContent, setInputContent] = useState('');
  const { conversation, session, user } = state;

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputContent.trim()) return;
    try {
      const newState = await sessionApi.addMessage(session.session_id, user.user_id, inputContent.trim(), 'USER');
      onStateUpdated(newState);
      setInputContent('');
    } catch (err: any) {
      onError(err.message || 'Failed to send message');
    }
  };

  return (
    <div style={cardStyle}>
      <h3 style={{ margin: '0 0 1rem 0' }}>Stateful Conversation Log</h3>

      <div style={messageContainerStyle}>
        {conversation.recent_messages.length === 0 ? (
          <p style={{ color: '#9ca3af', fontStyle: 'italic', textAlign: 'center' }}>
            No messages in conversation yet.
          </p>
        ) : (
          conversation.recent_messages.map((msg) => (
            <div key={msg.message_id} style={{
              ...msgBubbleStyle,
              alignSelf: msg.role === 'USER' ? 'flex-end' : 'flex-start',
              backgroundColor: msg.role === 'USER' ? '#dbeafe' : '#f3f4f6',
              color: msg.role === 'USER' ? '#1e40af' : '#1f2937',
            }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, marginBottom: '0.2rem', color: '#6b7280' }}>
                {msg.role} • {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
              <div>{msg.content}</div>
            </div>
          ))
        )}
      </div>

      <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
        <input
          type="text"
          placeholder="Ask Hadoop question (e.g., Why 3 replicas?)..."
          value={inputContent}
          onChange={(e) => setInputContent(e.target.value)}
          style={{ flex: 1, padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #d1d5db' }}
        />
        <button type="submit" style={{ padding: '0.5rem 1rem', backgroundColor: '#2563eb', color: '#ffffff', border: 'none', borderRadius: '6px', fontWeight: 600 }}>
          Send
        </button>
      </form>
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

const messageContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '0.75rem',
  maxHeight: '220px',
  overflowY: 'auto',
  padding: '0.5rem',
  backgroundColor: '#f9fafb',
  borderRadius: '8px',
  border: '1px solid #f3f4f6',
};

const msgBubbleStyle: React.CSSProperties = {
  maxWidth: '80%',
  padding: '0.6rem 0.8rem',
  borderRadius: '8px',
  fontSize: '0.9rem',
};
