import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, ArrowRight, Sparkles, Server } from 'lucide-react';

export const WelcomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#070a12',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background Neon Grid Decoration */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: 'radial-gradient(circle at 50% 30%, rgba(0, 240, 255, 0.08) 0%, transparent 60%), linear-gradient(rgba(30, 41, 66, 0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(30, 41, 66, 0.2) 1px, transparent 1px)',
        backgroundSize: '100% 100%, 40px 40px, 40px 40px',
        pointerEvents: 'none'
      }} />

      {/* Main Content Box */}
      <div style={{
        maxWidth: '540px',
        width: '100%',
        backgroundColor: '#0e1526',
        borderRadius: '16px',
        border: '1px solid rgba(0, 240, 255, 0.3)',
        padding: '3rem 2.5rem',
        boxShadow: '0 0 40px rgba(0, 240, 255, 0.15)',
        textAlign: 'center',
        position: 'relative',
        zIndex: 10
      }}>
        {/* TEDDY Symbol */}
        <div style={{
          width: '72px',
          height: '72px',
          margin: '0 auto 1.5rem',
          borderRadius: '16px',
          background: 'linear-gradient(135deg, #00f0ff 0%, #0284c7 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 25px rgba(0, 240, 255, 0.4)'
        }}>
          <Cpu size={40} color="#070a12" strokeWidth={2.5} />
        </div>

        <h1 style={{
          fontSize: '32px',
          fontWeight: 800,
          letterSpacing: '2px',
          color: '#ffffff',
          marginBottom: '6px',
          fontFamily: "'JetBrains Mono', monospace"
        }}>
          TEDDY
        </h1>

        <div style={{
          fontSize: '13px',
          fontWeight: 600,
          color: '#00f0ff',
          letterSpacing: '1px',
          marginBottom: '1.5rem',
          textTransform: 'uppercase'
        }}>
          Interactive Hadoop Intelligence
        </div>

        <p style={{
          fontSize: '14px',
          color: '#94a3b8',
          lineHeight: '1.6',
          marginBottom: '2rem'
        }}>
          An interactive AI-powered laboratory for exploring distributed systems execution, HDFS block replication, failure recovery, and MapReduce workloads.
        </p>

        {/* Feature Highlights */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '10px',
          marginBottom: '2.5rem',
          textAlign: 'left'
        }}>
          <div style={{
            backgroundColor: '#131c31',
            padding: '12px',
            borderRadius: '8px',
            border: '1px solid #1e2942',
            fontSize: '12px',
            color: '#cbd5e1',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Server size={16} color="#00f0ff" />
            <span>Authoritative Simulation</span>
          </div>

          <div style={{
            backgroundColor: '#131c31',
            padding: '12px',
            borderRadius: '8px',
            border: '1px solid #1e2942',
            fontSize: '12px',
            color: '#cbd5e1',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Sparkles size={16} color="#00f0ff" />
            <span>Intelligent Assistant</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button
            onClick={async () => {
              try {
                if (!document.fullscreenElement) {
                  await document.documentElement.requestFullscreen();
                }
              } catch (_) {}
              navigate('/dashboard');
            }}
            style={{
              width: '100%',
              padding: '14px 24px',
              backgroundColor: '#00f0ff',
              color: '#070a12',
              border: 'none',
              borderRadius: '8px',
              fontSize: '15px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '10px',
              boxShadow: '0 0 20px rgba(0, 240, 255, 0.35)',
              transition: 'all 0.2s ease'
            }}
          >
            <span>Enter TEDDY (Fullscreen Kiosk)</span>
            <ArrowRight size={18} />
          </button>

          <button
            onClick={() => navigate('/dashboard')}
            style={{
              width: '100%',
              padding: '10px 24px',
              backgroundColor: '#131c31',
              color: '#94a3b8',
              border: '1px solid #1e2942',
              borderRadius: '8px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            Continue in Standard Window
          </button>
        </div>

        <div style={{ marginTop: '1.5rem', fontSize: '11px', color: '#64748b' }}>
          Press <kbd style={{ padding: '2px 4px', backgroundColor: '#1e2942', borderRadius: '3px', color: '#cbd5e1' }}>ESC</kbd> anytime to exit Fullscreen Kiosk Mode
        </div>
      </div>
    </div>
  );
};
