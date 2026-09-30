import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ChevronRight, Play } from 'lucide-react';

export const AcademyPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTopic, setActiveTopic] = useState('HDFS');

  const topics = [
    {
      module: 'HDFS',
      lessons: [
        { title: 'Filesystem Architecture', desc: 'Master/Worker topology, namespace management, and Metadata.' },
        { title: 'Block Storage Mechanics', desc: 'Why HDFS splits files into 128 MB blocks.' },
        { title: 'Replication & Fault Tolerance', desc: 'Rack awareness, block placement policy, and replica health.' },
        { title: 'NameNode & DataNode Roles', desc: 'Block reports, heartbeats, and EditLog/FSImage checkpoints.' }
      ]
    },
    {
      module: 'MapReduce',
      lessons: [
        { title: 'Mapper & InputSplits', desc: 'RecordReader processing records into Key-Value pairs.' },
        { title: 'Shuffle & Sort Phase', desc: 'Partitioning, sorting, and spilling map output to disk.' },
        { title: 'Reducer Aggregation', desc: 'Grouping by key and writing final HDFS output.' }
      ]
    },
    {
      module: 'YARN',
      lessons: [
        { title: 'ResourceManager & NodeManager', desc: 'Decoupling resource management from execution.' },
        { title: 'ApplicationMaster & Containers', desc: 'Per-job container negotiation and resource isolation.' }
      ]
    }
  ];

  const currentModule = topics.find(t => t.module === activeTopic) || topics[0];

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Page Header */}
      <div>
        <div style={{ fontSize: '22px', fontWeight: 800, color: '#ffffff', marginBottom: '6px' }}>
          Hadoop Academy
        </div>
        <div style={{ fontSize: '14px', color: '#94a3b8' }}>
          Interactive structured curriculum explaining distributed storage, MapReduce execution, and YARN resource management.
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '24px' }}>
        {/* Module Sidebar */}
        <div style={{ backgroundColor: '#0e1526', border: '1px solid #1e2942', borderRadius: '10px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#00f0ff', letterSpacing: '0.5px', marginBottom: '8px' }}>
            LEARNING MODULES
          </div>

          {topics.map((t) => (
            <button
              key={t.module}
              onClick={() => setActiveTopic(t.module)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 14px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: activeTopic === t.module ? 700 : 500,
                color: activeTopic === t.module ? '#00f0ff' : '#94a3b8',
                backgroundColor: activeTopic === t.module ? 'rgba(0, 240, 255, 0.08)' : 'transparent',
                border: '1px solid',
                borderColor: activeTopic === t.module ? 'rgba(0, 240, 255, 0.3)' : 'transparent',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              <span>{t.module} Architecture</span>
              <ChevronRight size={16} />
            </button>
          ))}
        </div>

        {/* Lessons List & TEDDY Explanation Callout */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* TEDDY Explanation Assistant Banner */}
          <div style={{
            backgroundColor: '#131c31',
            border: '1px solid rgba(0, 240, 255, 0.3)',
            borderRadius: '10px',
            padding: '20px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '16px'
          }}>
            <Sparkles size={24} color="#00f0ff" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#00f0ff', marginBottom: '4px' }}>
                TEDDY Interactive Learning Integration
              </div>
              <div style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: '1.5' }}>
                TEDDY can explain any concept from this module while running live in the Simulation Studio. Simply ask TEDDY: <em style={{ color: '#00f0ff' }}>"Explain NameNode block reports"</em> or <em style={{ color: '#00f0ff' }}>"Why are 128 MB blocks used?"</em>.
              </div>
            </div>
          </div>

          {/* Lessons Cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {currentModule.lessons.map((lesson, idx) => (
              <div
                key={idx}
                style={{
                  backgroundColor: '#0e1526',
                  border: '1px solid #1e2942',
                  borderRadius: '10px',
                  padding: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <div>
                  <div style={{ fontSize: '11px', color: '#00f0ff', fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, marginBottom: '4px' }}>
                    LESSON 0{idx + 1}
                  </div>
                  <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#ffffff', marginBottom: '4px' }}>
                    {lesson.title}
                  </h4>
                  <p style={{ fontSize: '12px', color: '#94a3b8' }}>
                    {lesson.desc}
                  </p>
                </div>

                <button
                  onClick={() => navigate('/simulation')}
                  style={{
                    backgroundColor: '#00f0ff',
                    color: '#070a12',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 14px',
                    fontSize: '12px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    boxShadow: '0 0 10px rgba(0, 240, 255, 0.2)'
                  }}
                >
                  <Play size={14} fill="#070a12" />
                  <span>Simulate Lesson</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
