import React from 'react';
import { Cpu } from 'lucide-react';

interface TeddyExplanationOverlayProps {
  explanationText: string | null;
  status: string;
  sources?: string[];
}

export const TeddyExplanationOverlay: React.FC<TeddyExplanationOverlayProps> = ({
  explanationText,
  status,
  sources
}) => {
  if (!explanationText) return null;

  return (
    <div style={{
      width: '100%',
      backgroundColor: 'rgba(14, 21, 38, 0.94)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid rgba(0, 240, 255, 0.3)',
      padding: '10px 20px',
      display: 'flex',
      alignItems: 'flex-start',
      gap: '12px',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
      zIndex: 25
    }}>
      {/* Icon & Status Tag */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0, marginTop: '2px' }}>
        <div style={{
          width: '28px',
          height: '28px',
          borderRadius: '50%',
          backgroundColor: 'rgba(0, 240, 255, 0.15)',
          border: '1px solid #00f0ff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Cpu size={14} color="#00f0ff" className="animate-neon-pulse" />
        </div>

        <span style={{
          fontSize: '11px',
          fontWeight: 800,
          color: '#00f0ff',
          letterSpacing: '0.8px',
          fontFamily: "'Space Grotesk', sans-serif"
        }}>
          TEDDY
        </span>

        <span style={{
          fontSize: '9px',
          fontWeight: 700,
          color: status === 'SPEAKING' ? '#00f0ff' : status === 'PAUSED' ? '#ef4444' : '#22c55e',
          backgroundColor: 'rgba(14, 21, 38, 0.9)',
          border: '1px solid rgba(0, 240, 255, 0.25)',
          padding: '1px 6px',
          borderRadius: '4px',
          fontFamily: "'JetBrains Mono', monospace"
        }}>
          ● {status}
        </span>
      </div>

      <span style={{ color: '#334155', marginTop: '2px' }}>|</span>

      {/* Multi-line Full Explanation Text & Citations */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <div style={{
          fontSize: '13px',
          color: '#f8fafc',
          fontWeight: 500,
          lineHeight: '1.4',
          fontFamily: "'Inter', sans-serif",
          maxHeight: '120px',
          overflowY: 'auto'
        }}>
          "{explanationText}"
        </div>

        {sources && sources.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
            <span style={{ fontSize: '10px', color: '#94a3b8', fontWeight: 600 }}>RAG Knowledge:</span>
            {sources.map((src, idx) => (
              <span
                key={idx}
                style={{
                  fontSize: '10px',
                  color: '#00f0ff',
                  backgroundColor: 'rgba(0, 240, 255, 0.1)',
                  border: '1px solid rgba(0, 240, 255, 0.3)',
                  padding: '1px 6px',
                  borderRadius: '10px',
                  fontFamily: "'JetBrains Mono', monospace"
                }}
              >
                📄 {src}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Equalizer Visualizer */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '3px', flexShrink: 0, marginTop: '6px' }}>
        {[0.6, 1.0, 0.4, 0.8, 0.5].map((h, i) => (
          <div
            key={i}
            style={{
              width: '3px',
              height: `${h * 12}px`,
              backgroundColor: status === 'SPEAKING' ? '#00f0ff' : '#475569',
              borderRadius: '1px',
              animation: status === 'SPEAKING' ? 'pulse-neon 0.8s infinite ease-in-out' : 'none',
              animationDelay: `${i * 0.1}s`
            }}
          />
        ))}
      </div>
    </div>
  );
};

