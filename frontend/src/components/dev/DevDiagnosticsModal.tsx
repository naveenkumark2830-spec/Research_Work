import React, { useState } from 'react';
import { X, Wrench } from 'lucide-react';
import { StateJsonViewer } from '../StateJsonViewer';
import { EventHistoryCard } from '../EventHistoryCard';

interface DevDiagnosticsModalProps {
  isOpen: boolean;
  onClose: () => void;
  state: any;
}

export const DevDiagnosticsModal: React.FC<DevDiagnosticsModalProps> = ({ isOpen, onClose, state }) => {
  const [activeTab, setActiveTab] = useState<'JSON' | 'EVENTS'>('JSON');

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(7, 10, 18, 0.85)',
      backdropFilter: 'blur(8px)',
      zIndex: 100,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px'
    }}>
      <div style={{
        width: '900px',
        maxHeight: '85vh',
        backgroundColor: '#0e1526',
        border: '1px solid rgba(0, 240, 255, 0.4)',
        borderRadius: '12px',
        boxShadow: '0 0 30px rgba(0, 240, 255, 0.2)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '16px 24px',
          backgroundColor: '#131c31',
          borderBottom: '1px solid #1e2942',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Wrench size={18} color="#00f0ff" />
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#ffffff', letterSpacing: '0.5px' }}>
              Developer Diagnostics & Audit Controls
            </h3>
          </div>

          <button
            onClick={onClose}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Tab Buttons */}
        <div style={{ padding: '8px 24px', backgroundColor: '#070a12', borderBottom: '1px solid #1e2942', display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setActiveTab('JSON')}
            style={{
              backgroundColor: activeTab === 'JSON' ? '#00f0ff' : 'transparent',
              color: activeTab === 'JSON' ? '#070a12' : '#94a3b8',
              border: 'none',
              borderRadius: '6px',
              padding: '6px 14px',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer'
            }}
          >
            Session State JSON
          </button>
          <button
            onClick={() => setActiveTab('EVENTS')}
            style={{
              backgroundColor: activeTab === 'EVENTS' ? '#00f0ff' : 'transparent',
              color: activeTab === 'EVENTS' ? '#070a12' : '#94a3b8',
              border: 'none',
              borderRadius: '6px',
              padding: '6px 14px',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer'
            }}
          >
            Event Stream Log
          </button>
        </div>

        {/* Tab Content */}
        <div style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>
          {activeTab === 'JSON' ? (
            <StateJsonViewer state={state} />
          ) : (
            <EventHistoryCard state={state} />
          )}
        </div>
      </div>
    </div>
  );
};
