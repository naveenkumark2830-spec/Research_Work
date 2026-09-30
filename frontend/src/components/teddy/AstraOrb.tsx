// ⚠️ DEPRECATED — not imported by SimulationStudioPage.tsx.
// Superseded by CosmicNebulaCanvas.tsx.
import React from 'react';

export type AstraOrbMode = 'idle' | 'listening' | 'speaking' | 'text';

interface AstraOrbProps {
  mode: AstraOrbMode;
  amplitude?: number; // 0 - 1 live mic volume or synthetic rhythm
  onClick?: () => void;
}

export const AstraOrb: React.FC<AstraOrbProps> = ({ mode, amplitude = 0, onClick }) => {
  const DOT_COUNT = 32;
  const RAY_COUNT = 36;
  const dots = Array.from({ length: DOT_COUNT });
  const rays = Array.from({ length: RAY_COUNT });

  const effectiveAmp = mode === 'idle'
    ? 0.15
    : mode === 'text'
    ? 0.05
    : amplitude;

  const coreGradient = mode === 'speaking'
    ? 'radial-gradient(circle at 35% 35%, #00f0ff 0%, #3b82f6 45%, #8b5cf6 75%, #1e1b4b 100%)'
    : mode === 'listening'
    ? 'radial-gradient(circle at 35% 35%, #38bdf8 0%, #a855f7 50%, #6366f1 75%, #0f172a 100%)'
    : 'radial-gradient(circle at 35% 35%, #00f0ff 0%, #0284c7 45%, #4c1d95 80%, #070a12 100%)';

  return (
    <div
      onClick={onClick}
      className={`astra-orb astra-orb--${mode}`}
      style={{
        position: 'relative',
        width: '200px',
        height: '200px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: onClick ? 'pointer' : 'default',
        margin: '0 auto'
      }}
      title={onClick ? 'Click to toggle Voice Mode' : undefined}
    >
      {/* 36 Radial Energy Ray Spikes (Bursting Outward behind Core) */}
      {rays.map((_, i) => {
        const angle = (360 / RAY_COUNT) * i;
        const length = 40 + (i % 3) * 20 + effectiveAmp * 30;
        return (
          <div
            key={`ray-${i}`}
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              width: '1.5px',
              height: `${length}px`,
              background: 'linear-gradient(to top, rgba(0, 240, 255, 0.9), rgba(168, 85, 247, 0))',
              transformOrigin: 'top center',
              transform: `rotate(${angle}deg) translateY(25px)`,
              opacity: mode === 'listening' || mode === 'speaking' ? 0.85 : 0.5,
              transition: 'all 0.2s ease-out'
            }}
          />
        );
      })}

      {/* Outer Glow Halo */}
      <div
        style={{
          position: 'absolute',
          inset: '30px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(0, 240, 255, 0.4) 0%, rgba(139, 92, 246, 0.2) 60%, transparent 100%)',
          filter: 'blur(16px)',
          transform: `scale(${1 + effectiveAmp * 0.3})`,
          transition: 'all 0.2s ease-out'
        }}
      />

      {/* Vibrant 3D Sphere Core */}
      <div
        className="astra-orb__core"
        style={{
          width: '76px',
          height: '76px',
          borderRadius: '50%',
          background: coreGradient,
          boxShadow: mode === 'listening' || mode === 'speaking'
            ? `0 0 ${30 + effectiveAmp * 25}px #00f0ff, 0 0 ${50 + effectiveAmp * 30}px #8b5cf6`
            : '0 0 20px rgba(0, 240, 255, 0.6), 0 0 40px rgba(139, 92, 246, 0.3)',
          transform: `scale(${1 + effectiveAmp * 0.25})`,
          transition: 'all 0.2s ease-out',
          zIndex: 5
        }}
      />

      {/* 32 Radial Particle Ring Dots */}
      {dots.map((_, i) => {
        const angle = (360 / DOT_COUNT) * i;
        const delay = (i / DOT_COUNT) * 2;

        return (
          <div
            key={`dot-${i}`}
            className="astra-orb__dot"
            style={{
              '--angle': `${angle}deg`,
              '--amp': effectiveAmp,
              animationDelay: `${delay}s`,
              backgroundColor: mode === 'speaking' ? '#00f0ff' : mode === 'listening' ? '#38e0e0' : '#0ea5e9',
              zIndex: 6
            } as React.CSSProperties}
          />
        );
      })}
    </div>
  );
};
