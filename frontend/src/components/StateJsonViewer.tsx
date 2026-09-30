import React, { useState } from 'react';
import { SessionState } from '../types/session';

interface StateJsonViewerProps {
  state: SessionState;
}

export const StateJsonViewer: React.FC<StateJsonViewerProps> = ({ state }) => {
  const [collapsed, setCollapsed] = useState(true);

  return (
    <div style={cardStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0 }}>Raw SessionState JSON Inspector</h3>
        <button
          onClick={() => setCollapsed(!collapsed)}
          style={{ padding: '0.3rem 0.8rem', backgroundColor: '#4b5563', color: '#ffffff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}
        >
          {collapsed ? 'Expand JSON' : 'Collapse JSON'}
        </button>
      </div>

      {!collapsed && (
        <pre style={{
          marginTop: '1rem',
          padding: '1rem',
          backgroundColor: '#1f2937',
          color: '#10b981',
          borderRadius: '8px',
          maxHeight: '300px',
          overflowY: 'auto',
          fontSize: '0.8rem',
          fontFamily: 'monospace'
        }}>
          {JSON.stringify(state, null, 2)}
        </pre>
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
