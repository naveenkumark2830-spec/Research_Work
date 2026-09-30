import React, { useEffect, useRef } from 'react';

interface WarpFieldBackgroundProps {
  active?: boolean; // True when simulation is active (subdues particle brightness)
}

export const WarpFieldBackground: React.FC<WarpFieldBackgroundProps> = ({ active = false }) => {
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
    let particles: Array<{
      angle: number;
      radius: number;
      speed: number;
      length: number;
      brightness: number;
    }> = [];
    let rafId: number;

    const resize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      cx = width / 2;
      cy = height / 2;
    };

    resize();
    window.addEventListener('resize', resize);

    const makeParticle = () => {
      const angle = Math.random() * Math.PI * 2;
      return {
        angle,
        radius: Math.random() * 20, // Start near core
        speed: 0.4 + Math.random() * 1.0, // Outward speed
        length: 8 + Math.random() * 20, // Trail length
        brightness: 0.3 + Math.random() * 0.7
      };
    };

    const particleCount = window.innerWidth < 768 ? 110 : 220;
    particles = Array.from({ length: particleCount }, makeParticle);

    const draw = () => {
      // Fade previous frame slightly to create trailing motion blur
      ctx.fillStyle = 'rgba(5, 8, 16, 0.25)';
      ctx.fillRect(0, 0, width, height);

      const maxRadius = Math.max(width, height) * 0.7;
      const opacityMultiplier = active ? 0.35 : 1.0;

      particles.forEach((p) => {
        const x1 = cx + Math.cos(p.angle) * p.radius;
        const y1 = cy + Math.sin(p.angle) * p.radius;
        const x2 = cx + Math.cos(p.angle) * (p.radius - p.length);
        const y2 = cy + Math.sin(p.angle) * (p.radius - p.length);

        const distFactor = 1 - p.radius / maxRadius;
        const alpha = Math.max(0, p.brightness * distFactor * opacityMultiplier);

        const gradient = ctx.createLinearGradient(x1, y1, x2, y2);
        gradient.addColorStop(0, `rgba(120, 200, 255, ${alpha})`);
        gradient.addColorStop(1, 'rgba(56, 224, 224, 0)');

        ctx.strokeStyle = gradient;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();

        // Advance particle outward with slight acceleration
        p.radius += p.speed * (1 + p.radius / maxRadius);

        // Respawn when particle exits field
        if (p.radius > maxRadius) {
          Object.assign(p, makeParticle());
        }
      });

      // Core nebula glow
      const coreGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, 100);
      const glowAlpha = active ? 0.2 : 0.45;
      coreGlow.addColorStop(0, `rgba(150, 220, 255, ${glowAlpha})`);
      coreGlow.addColorStop(0.5, `rgba(56, 224, 224, ${glowAlpha * 0.4})`);
      coreGlow.addColorStop(1, 'rgba(5, 8, 16, 0)');
      ctx.fillStyle = coreGlow;
      ctx.beginPath();
      ctx.arc(cx, cy, 100, 0, Math.PI * 2);
      ctx.fill();

      rafId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', resize);
    };
  }, [active]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        pointerEvents: 'none',
        transition: 'opacity 0.5s ease'
      }}
    />
  );
};
