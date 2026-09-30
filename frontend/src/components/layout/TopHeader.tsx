import React, { useState, useEffect } from 'react';
import { User, Wrench, Maximize2, Minimize2 } from 'lucide-react';

interface TopHeaderProps {
  title: string;
  onOpenDebugModal?: () => void;
}

export const TopHeader: React.FC<TopHeaderProps> = ({ title, onOpenDebugModal }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  const toggleFullscreen = async () => {
    if (!document.fullscreenElement) {
      await document.documentElement.requestFullscreen().catch(() => {});
    } else {
      if (document.exitFullscreen) {
        await document.exitFullscreen().catch(() => {});
      }
    }
  };

  return (
    <header style={{
      height: '60px',
      backgroundColor: '#0e1526',
      borderBottom: '1px solid #1e2942',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      position: 'sticky',
      top: 0,
      zIndex: 30
    }}>
      {/* Route Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc', letterSpacing: '0.5px' }}>
          {title}
        </h2>
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          backgroundColor: 'rgba(34, 197, 94, 0.12)',
          color: '#22c55e',
          border: '1px solid rgba(34, 197, 94, 0.35)',
          padding: '3px 10px',
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: 700,
          fontFamily: "'JetBrains Mono', monospace"
        }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#22c55e', animation: 'pulse-neon 1.5s infinite ease-in-out' }} />
          {/* Animated Mini Live Telemetry Sparkline */}
          <svg width="24" height="10" viewBox="0 0 24 10" style={{ overflow: 'visible' }}>
            <path
              d="M 0 5 L 4 5 L 7 1 L 10 9 L 14 3 L 18 6 L 24 5"
              fill="none"
              stroke="#22c55e"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          SYSTEM LIVE
        </span>
      </div>

      {/* Actions & User Info */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Native Fullscreen Kiosk Mode Toggle */}
        <button
          onClick={toggleFullscreen}
          title={isFullscreen ? 'Exit Fullscreen (ESC)' : 'Enter Fullscreen Kiosk Mode'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: isFullscreen ? 'rgba(0, 240, 255, 0.12)' : '#131c31',
            color: isFullscreen ? '#00f0ff' : '#94a3b8',
            border: isFullscreen ? '1px solid rgba(0, 240, 255, 0.4)' : '1px solid #1e2942',
            padding: '6px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            cursor: 'pointer',
            fontWeight: 600,
            transition: 'all 0.15s ease'
          }}
        >
          {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          <span>{isFullscreen ? 'Exit Kiosk' : 'Kiosk Mode'}</span>
        </button>

        {onOpenDebugModal && (
          <button
            onClick={onOpenDebugModal}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: '#131c31',
              color: '#94a3b8',
              border: '1px solid #1e2942',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '12px',
              cursor: 'pointer',
              fontWeight: 500
            }}
          >
            <Wrench size={14} />
            <span>Dev Diagnostics</span>
          </button>
        )}

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          backgroundColor: '#131c31',
          padding: '6px 12px',
          borderRadius: '20px',
          border: '1px solid #1e2942'
        }}>
          <User size={14} color="#00f0ff" />
          <span style={{ fontSize: '12px', color: '#f8fafc', fontWeight: 600 }}>Evaluator Account</span>
        </div>
      </div>
    </header>
  );
};
