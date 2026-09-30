import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Search,
  Play,
  GraduationCap,
  ArrowRight,
  Database,
  Activity,
  Sparkles
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  const typewriterPrompts = [
    'Ask Teddy about HDFS block replication...',
    'Run a DataNode crash & recovery experiment...',
    'Explain MapReduce shuffle & sort phase...',
    'Quiz me on YARN container resource scheduling...'
  ];

  // Animated placeholder typewriter rotation
  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % typewriterPrompts.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const recentSimulations = [
    {
      id: 'hdfs-write',
      title: 'HDFS Write Simulation',
      desc: '1 GB file • 128 MB blocks • RF 3',
      system: 'HDFS',
      stage: 'Block Distribution',
      path: '/simulation'
    },
    {
      id: 'mapreduce-wordcount',
      title: 'MapReduce Word Count',
      desc: '5 GB corpus • 5 Mappers • 2 Reducers',
      system: 'MapReduce',
      stage: 'Shuffle & Sort',
      path: '/simulation'
    },
    {
      id: 'failure-lab',
      title: 'DataNode Failure Lab',
      desc: 'Hardware crash • Auto-healing re-replication',
      system: 'HDFS',
      stage: 'Recovery Phase',
      path: '/simulation'
    }
  ];

  const suggestedCommands = [
    'Explain HDFS block replication',
    'Run a DataNode failure experiment',
    'Compare Hadoop 1 and Hadoop 2',
    'Quiz me on HDFS architecture'
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Domain Network Mesh Grid Greeting Banner */}
      <div className="network-grid-bg glass-panel" style={{
        borderRadius: '16px',
        padding: '36px',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 240, 255, 0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <Sparkles size={18} color="#00f0ff" className="animate-neon-pulse" />
          <span style={{ fontSize: '12px', fontWeight: 800, color: '#00f0ff', letterSpacing: '1px', textTransform: 'uppercase', fontFamily: "'Space Grotesk', sans-serif" }}>
            TEDDY COMMAND CENTER
          </span>
        </div>

        <h1 style={{ fontSize: '26px', fontWeight: 800, color: '#ffffff', marginBottom: '6px', fontFamily: "'Space Grotesk', sans-serif" }}>
          Good evening, Evaluator
        </h1>
        <p style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '24px' }}>
          What distributed systems workflow or simulation experiment would you like to command today?
        </p>

        {/* Search Command Input with Typewriter Placeholder */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          backgroundColor: '#070a12',
          border: '1px solid rgba(0, 240, 255, 0.4)',
          borderRadius: '12px',
          padding: '4px 16px',
          boxShadow: '0 0 20px rgba(0, 240, 255, 0.2)'
        }}>
          <Search size={20} color="#00f0ff" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') navigate('/simulation');
            }}
            placeholder={typewriterPrompts[placeholderIndex]}
            style={{
              flex: 1,
              backgroundColor: 'transparent',
              border: 'none',
              padding: '14px 16px',
              color: '#f8fafc',
              fontSize: '14px',
              outline: 'none',
              fontFamily: "'Inter', sans-serif"
            }}
          />
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={() => navigate('/simulation')}
            style={{
              backgroundColor: '#00f0ff',
              color: '#070a12',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 18px',
              fontSize: '13px',
              fontWeight: 800,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              boxShadow: '0 0 15px rgba(0, 240, 255, 0.4)'
            }}
          >
            <span>Execute</span>
            <ArrowRight size={14} />
          </motion.button>
        </div>

        {/* Suggested Command Chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '16px' }}>
          {suggestedCommands.map((cmd, idx) => (
            <motion.button
              key={idx}
              whileHover={{ scale: 1.03, backgroundColor: 'rgba(0, 240, 255, 0.15)' }}
              whileTap={{ scale: 0.97 }}
              onClick={() => {
                setQuery(cmd);
                navigate('/simulation');
              }}
              style={{
                backgroundColor: '#131c31',
                color: '#cbd5e1',
                border: '1px solid #1e2942',
                borderRadius: '20px',
                padding: '6px 14px',
                fontSize: '12px',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {cmd}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Domain Data Visualization Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
        {/* Total Simulations + Sparkline */}
        <div className="card-hover-depth" style={{ backgroundColor: '#0e1526', border: '1px solid #1e2942', borderRadius: '12px', padding: '20px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 600 }}>Total Simulations</span>
            <Database size={18} color="#00f0ff" />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginBottom: '8px' }}>
            <div style={{ fontSize: '32px', fontWeight: 800, color: '#ffffff', fontFamily: "'JetBrains Mono', monospace" }}>
              24
            </div>
            <span style={{ fontSize: '11px', color: '#22c55e', fontWeight: 700 }}>+4 today</span>
          </div>

          {/* Embedded Session History Sparkline Chart */}
          <svg width="100%" height="24" viewBox="0 0 120 24" style={{ overflow: 'visible' }}>
            <path
              d="M 0 20 L 20 16 L 40 18 L 60 8 L 80 12 L 100 4 L 120 6"
              fill="none"
              stroke="#00f0ff"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>

        {/* Academy Progress */}
        <div className="card-hover-depth" style={{ backgroundColor: '#0e1526', border: '1px solid #1e2942', borderRadius: '12px', padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 600 }}>Academy Progress</span>
            <GraduationCap size={18} color="#0ea5e9" />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#ffffff', fontFamily: "'JetBrains Mono', monospace", marginBottom: '8px' }}>
            82%
          </div>
          <div style={{ width: '100%', height: '6px', backgroundColor: '#070a12', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{ width: '82%', height: '100%', background: 'linear-gradient(90deg, #0284c7 0%, #00f0ff 100%)' }} />
          </div>
        </div>

        {/* Assessment Accuracy + Radial Progress Ring */}
        <div className="card-hover-depth" style={{ backgroundColor: '#0e1526', border: '1px solid #1e2942', borderRadius: '12px', padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <Activity size={18} color="#8b5cf6" />
              <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 600 }}>Assessment Accuracy</span>
            </div>
            <div style={{ fontSize: '28px', fontWeight: 800, color: '#ffffff', fontFamily: "'JetBrains Mono', monospace" }}>
              10 / 12
            </div>
            <div style={{ fontSize: '11px', color: '#8b5cf6', marginTop: '2px', fontWeight: 600 }}>83.3% Mastery</div>
          </div>

          {/* SVG Radial Progress Ring */}
          <div style={{ position: 'relative', width: '54px', height: '54px' }}>
            <svg width="54" height="54" viewBox="0 0 54 54">
              <circle cx="27" cy="27" r="22" fill="none" stroke="#070a12" strokeWidth="5" />
              <circle
                cx="27"
                cy="27"
                r="22"
                fill="none"
                stroke="#8b5cf6"
                strokeWidth="5"
                strokeDasharray="138"
                strokeDashoffset="23"
                strokeLinecap="round"
                transform="rotate(-90 27 27)"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Recent Simulations Section */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '800', color: '#f8fafc', fontFamily: "'Space Grotesk', sans-serif" }}>
            Recent Simulations
          </h3>
          <button
            onClick={() => navigate('/simulation')}
            style={{ backgroundColor: 'transparent', border: 'none', color: '#00f0ff', fontSize: '13px', fontWeight: '700', cursor: 'pointer' }}
          >
            Launch Studio →
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          {recentSimulations.map((sim) => (
            <motion.div
              key={sim.id}
              whileHover={{ y: -4, scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              className="card-hover-depth"
              style={{
                backgroundColor: '#0e1526',
                border: '1px solid #1e2942',
                borderRadius: '12px',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                height: '165px'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '10px', fontWeight: 800, color: '#00f0ff', backgroundColor: 'rgba(0, 240, 255, 0.1)', padding: '2px 8px', borderRadius: '4px', fontFamily: "'JetBrains Mono', monospace" }}>
                    {sim.system}
                  </span>
                  <span style={{ fontSize: '11px', color: '#64748b', fontFamily: "'JetBrains Mono', monospace" }}>
                    {sim.stage}
                  </span>
                </div>
                <h4 style={{ fontSize: '15px', fontWeight: '700', color: '#ffffff', marginBottom: '4px', fontFamily: "'Space Grotesk', sans-serif" }}>
                  {sim.title}
                </h4>
                <p style={{ fontSize: '12px', color: '#94a3b8' }}>
                  {sim.desc}
                </p>
              </div>

              <button
                onClick={() => navigate(sim.path)}
                style={{
                  backgroundColor: '#131c31',
                  color: '#00f0ff',
                  border: '1px solid rgba(0, 240, 255, 0.3)',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  fontSize: '12px',
                  fontWeight: '700',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}
              >
                <Play size={14} fill="#00f0ff" />
                <span>Open Simulation</span>
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};
