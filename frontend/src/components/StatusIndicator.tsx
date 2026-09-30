import React from 'react';
import { HealthStatus } from '../types/health';

interface StatusIndicatorProps {
  status: HealthStatus;
  onRetry?: () => void;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, onRetry }) => {
  const getStatusDetails = () => {
    switch (status) {
      case 'connected':
        return {
          label: 'Connected',
          color: '#10B981', // green
          badgeBg: '#D1FAE5',
          textColor: '#065F46',
          dotColor: '#10B981',
        };
      case 'unavailable':
        return {
          label: 'Backend unavailable',
          color: '#EF4444', // red
          badgeBg: '#FEE2E2',
          textColor: '#991B1B',
          dotColor: '#EF4444',
        };
      case 'pending':
      default:
        return {
          label: 'Backend connection pending/checking...',
          color: '#F59E0B', // amber
          badgeBg: '#FEF3C7',
          textColor: '#92400E',
          dotColor: '#F59E0B',
        };
    }
  };

  const details = getStatusDetails();

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '1rem',
      padding: '2rem',
      borderRadius: '12px',
      backgroundColor: '#ffffff',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      border: '1px solid #E5E7EB',
      maxWidth: '480px',
      margin: '0 auto'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        backgroundColor: details.badgeBg,
        color: details.textColor,
        padding: '0.5rem 1rem',
        borderRadius: '9999px',
        fontWeight: 600,
        fontSize: '0.95rem'
      }}>
        <span style={{
          height: '10px',
          width: '10px',
          borderRadius: '50%',
          backgroundColor: details.dotColor,
          display: 'inline-block',
          boxShadow: status === 'connected' ? '0 0 8px #10B981' : 'none'
        }} />
        <span>Status: {details.label}</span>
      </div>

      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            marginTop: '0.5rem',
            padding: '0.5rem 1.25rem',
            borderRadius: '6px',
            backgroundColor: '#3B82F6',
            color: '#FFFFFF',
            border: 'none',
            fontWeight: 500,
            cursor: 'pointer',
            fontSize: '0.875rem',
            transition: 'background-color 0.2s'
          }}
          onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#2563EB')}
          onMouseOut={(e) => (e.currentTarget.style.backgroundColor = '#3B82F6')}
        >
          Check Connection Now
        </button>
      )}
    </div>
  );
};
