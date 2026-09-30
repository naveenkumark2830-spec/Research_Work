import React from 'react';
import { Activity, MessageSquare, ShieldAlert, Award, Clock } from 'lucide-react';

export const HistoryPage: React.FC = () => {
  const metrics = [
    { label: 'Simulation Sessions', value: '24', icon: Activity, color: '#00f0ff' },
    { label: 'Questions Asked', value: '87', icon: MessageSquare, color: '#0ea5e9' },
    { label: 'Interruptions (Barge-in)', value: '13', icon: ShieldAlert, color: '#ef4444' },
    { label: 'Quiz Accuracy', value: '82%', icon: Award, color: '#22c55e' },
  ];

  const recentSessions = [
    { title: 'HDFS Replication & Fault Tolerance Lab', date: 'Today • 18 min', status: 'COMPLETED' },
    { title: 'DataNode Failure & Under-Replication', date: 'Yesterday • 24 min', status: 'COMPLETED' },
    { title: 'MapReduce Word Count Execution Trace', date: 'Yesterday • 11 min', status: 'COMPLETED' }
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Page Header */}
      <div>
        <div style={{ fontSize: '22px', fontWeight: 800, color: '#ffffff', marginBottom: '6px' }}>
          History & Insights
        </div>
        <div style={{ fontSize: '14px', color: '#94a3b8' }}>
          Research analytics and session interaction logs across simulation experiments.
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div key={idx} style={{ backgroundColor: '#0e1526', border: '1px solid #1e2942', borderRadius: '10px', padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>{m.label}</span>
                <Icon size={18} color={m.color} />
              </div>
              <div style={{ fontSize: '28px', fontWeight: 800, color: '#ffffff', fontFamily: "'JetBrains Mono', monospace" }}>
                {m.value}
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Sessions List */}
      <div style={{ backgroundColor: '#0e1526', border: '1px solid #1e2942', borderRadius: '10px', padding: '24px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#ffffff', marginBottom: '16px' }}>
          Recent Simulation Sessions
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {recentSessions.map((s, idx) => (
            <div
              key={idx}
              style={{
                backgroundColor: '#131c31',
                border: '1px solid #1e2942',
                borderRadius: '8px',
                padding: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Clock size={16} color="#00f0ff" />
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#ffffff', marginBottom: '2px' }}>
                    {s.title}
                  </div>
                  <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                    {s.date}
                  </div>
                </div>
              </div>

              <span style={{
                fontSize: '11px',
                fontWeight: 700,
                color: '#22c55e',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                padding: '3px 8px',
                borderRadius: '4px',
                fontFamily: "'JetBrains Mono', monospace"
              }}>
                {s.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
