import React, { useEffect, useRef } from 'react';
import { TeddyOrbMode } from './TeddyOrb';

interface CosmicNebulaCanvasProps {
  mode: TeddyOrbMode;
  amplitude?: number;
  activeSimulation?: boolean;
  onClick?: () => void;
}

export const CosmicNebulaCanvas: React.FC<CosmicNebulaCanvasProps> = ({
  mode,
  amplitude = 0,
  activeSimulation = false,
  onClick
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let cx = 0;
    let cy = 0;
    let animId: number;

    const resize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      cx = width / 2;
      cy = height / 2;
    };

    resize();
    window.addEventListener('resize', resize);

    // Create 350 organic cosmic dust particles flowing in smooth spiral paths
    const PARTICLE_COUNT = window.innerWidth < 768 ? 160 : 320;
    const particles = Array.from({ length: PARTICLE_COUNT }, () => ({
      angle: Math.random() * Math.PI * 2,
      distance: Math.random() * Math.max(window.innerWidth, window.innerHeight) * 0.6 + 20,
      speed: 0.15 + Math.random() * 0.4,
      orbitSpeed: (Math.random() - 0.5) * 0.004,
      size: 0.8 + Math.random() * 1.8,
      baseAlpha: 0.2 + Math.random() * 0.7,
      hue: Math.random() > 0.3 ? 'blue' : 'cyan' // Deep blue & soft cyan cosmic palette
    }));

    let pulsePhase = 0;

    const draw = () => {
      // Soft background clear for organic motion trails
      ctx.fillStyle = 'rgba(2, 4, 10, 0.22)';
      ctx.fillRect(0, 0, width, height);

      pulsePhase += 0.02;
      const synthAmp = mode === 'speaking' ? 0.35 + Math.sin(pulsePhase * 4) * 0.2 : mode === 'listening' ? amplitude : 0.15;
      const currentAmp = Math.max(0.12, synthAmp);

      const maxDist = Math.max(width, height) * 0.65;
      const activeFactor = activeSimulation ? 0.35 : 1.0;

      // Draw 320 Cosmic Flow Particles
      particles.forEach((p) => {
        // Orbit and drift smoothly
        p.angle += p.orbitSpeed;
        p.distance += p.speed * (1 + (p.distance / maxDist) * 0.5);

        // Respawn smoothly near center when reaching outer boundary
        if (p.distance > maxDist) {
          p.distance = 15 + Math.random() * 30;
          p.angle = Math.random() * Math.PI * 2;
        }

        const x = cx + Math.cos(p.angle) * p.distance;
        const y = cy + Math.sin(p.angle) * p.distance;

        // Tail position for motion trail
        const trailDist = p.distance - (4 + p.speed * 8);
        const tx = cx + Math.cos(p.angle - p.orbitSpeed * 2) * trailDist;
        const ty = cy + Math.sin(p.angle - p.orbitSpeed * 2) * trailDist;

        const distRatio = p.distance / maxDist;
        const falloff = 1 - Math.pow(distRatio, 1.5);
        const alpha = Math.max(0, p.baseAlpha * falloff * activeFactor * (0.6 + currentAmp * 0.8));

        const colorStr = p.hue === 'blue'
          ? `rgba(96, 165, 250, ${alpha})`
          : `rgba(56, 189, 248, ${alpha})`;

        const grad = ctx.createLinearGradient(x, y, tx, ty);
        grad.addColorStop(0, colorStr);
        grad.addColorStop(1, 'rgba(2, 4, 10, 0)');

        ctx.strokeStyle = grad;
        ctx.lineWidth = p.size;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(tx, ty);
        ctx.stroke();
      });

      // Central Deep Blue Nebula Core Glow (Exactly matching user reference image)
      const coreRadius = (80 + currentAmp * 40) * (activeSimulation ? 0.7 : 1.0);
      const nebulaGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreRadius * 2.5);
      const coreAlpha = (mode === 'listening' || mode === 'speaking' ? 0.65 : 0.4) * activeFactor;

      nebulaGlow.addColorStop(0, `rgba(59, 130, 246, ${coreAlpha})`); // Royal blue center
      nebulaGlow.addColorStop(0.35, `rgba(29, 78, 216, ${coreAlpha * 0.6})`); // Deep blue halo
      nebulaGlow.addColorStop(0.7, `rgba(30, 58, 138, ${coreAlpha * 0.25})`);
      nebulaGlow.addColorStop(1, 'rgba(2, 4, 10, 0)');

      ctx.fillStyle = nebulaGlow;
      ctx.beginPath();
      ctx.arc(cx, cy, coreRadius * 2.5, 0, Math.PI * 2);
      ctx.fill();

      animId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, [mode, amplitude, activeSimulation]);

  return (
    <div
      onClick={onClick}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        cursor: onClick ? 'pointer' : 'default'
      }}
    >
      {/* 60fps Canvas Cosmic Nebula & Particle Stream */}
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          zIndex: 0,
          pointerEvents: 'none'
        }}
      />

      {/* Sleek Central Lens Core (Minimal & Non-Dominating) */}
      {!activeSimulation && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 10,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            pointerEvents: 'auto'
          }}
        >
          <div
            style={{
              width: '80px',
              height: '80px',
              borderRadius: '50%',
              background: mode === 'speaking'
                ? 'radial-gradient(circle, #60a5fa 0%, #2563eb 60%, #1e1b4b 100%)'
                : mode === 'listening'
                ? 'radial-gradient(circle, #38bdf8 0%, #3b82f6 60%, #0f172a 100%)'
                : 'radial-gradient(circle, rgba(96, 165, 250, 0.9) 0%, rgba(37, 99, 235, 0.5) 60%, transparent 100%)',
              boxShadow: mode === 'listening' || mode === 'speaking'
                ? `0 0 ${25 + amplitude * 20}px #3b82f6, inset 0 0 15px rgba(255, 255, 255, 0.4)`
                : '0 0 20px rgba(59, 130, 246, 0.5)',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid rgba(147, 197, 253, 0.4)'
            }}
          >
            {/* Minimal Concentric Inner Ring */}
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                border: '1.5px solid rgba(255, 255, 255, 0.6)',
                borderTopColor: '#38bdf8',
                animation: mode === 'speaking' ? 'spin 2s linear infinite' : mode === 'listening' ? 'spin 4s linear infinite' : 'spin 12s linear infinite'
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};
