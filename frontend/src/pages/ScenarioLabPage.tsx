import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play } from 'lucide-react';

export const ScenarioLabPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = useState('ALL');

  const categories = ['ALL', 'HDFS', 'MapReduce', 'YARN', 'Failure', 'Scaling', 'Replication'];

  const scenarios = [
    {
      id: 'SC01',
      title: 'HDFS Write Pipeline & Replication',
      desc: 'Simulate writing a 1 GB dataset across 5 DataNodes with replication factor 3.',
      category: 'HDFS',
      specs: '1 GB • 128 MB blocks • RF 3',
      difficulty: 'Easy'
    },
    {
      id: 'SC02',
      title: 'DataNode Hardware Failure during Write',
      desc: 'Inject a node failure during block transfer phase and observe under-replication detection.',
      category: 'Failure',
      specs: '500 MB • Node crash at t=4s',
      difficulty: 'Medium'
    },
    {
      id: 'SC03',
      title: 'MapReduce Word Count Execution',
      desc: 'Trace InputSplits, Mapper record processing, Shuffle & Sort, and Reducer output aggregation.',
      category: 'MapReduce',
      specs: '5 GB corpus • 5 Mappers • 2 Reducers',
      difficulty: 'Medium'
    },
    {
      id: 'SC04',
      title: 'YARN Resource Allocation & Containers',
      desc: 'Observe ApplicationMaster container allocation across NodeManagers via ResourceManager.',
      category: 'YARN',
      specs: '8 Containers • 16 GB vRAM',
      difficulty: 'Hard'
    },
    {
      id: 'SC05',
      title: 'Block Corruption & Automatic Recovery',
      desc: 'Inject checksum corruption into a block replica and verify NameNode background repair.',
      category: 'Replication',
      specs: 'Corrupt replica • Auto repair',
      difficulty: 'Hard'
    },
    {
      id: 'SC06',
      title: 'Horizontal Cluster Scaling',
      desc: 'Add 3 DataNodes dynamically and observe rebalancing of block storage across nodes.',
      category: 'Scaling',
      specs: '+3 DataNodes • Balancer job',
      difficulty: 'Easy'
    }
  ];

  const filtered = activeCategory === 'ALL' ? scenarios : scenarios.filter(s => s.category === activeCategory);

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Page Header */}
      <div>
        <div style={{ fontSize: '22px', fontWeight: 800, color: '#ffffff', marginBottom: '6px' }}>
          Scenario Lab
        </div>
        <div style={{ fontSize: '14px', color: '#94a3b8' }}>
          Explore pre-configured distributed systems experiments under complex network and failure conditions.
        </div>
      </div>

      {/* Category Tabs */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '4px' }}>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            style={{
              backgroundColor: activeCategory === cat ? '#00f0ff' : '#0e1526',
              color: activeCategory === cat ? '#070a12' : '#94a3b8',
              border: '1px solid',
              borderColor: activeCategory === cat ? '#00f0ff' : '#1e2942',
              borderRadius: '20px',
              padding: '6px 16px',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Scenarios Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
        {filtered.map((sc) => (
          <div
            key={sc.id}
            className="card-hover-depth"
            style={{
              backgroundColor: '#0e1526',
              border: '1px solid #1e2942',
              borderRadius: '10px',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              height: '210px'
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <span style={{
                  fontSize: '10px',
                  fontWeight: 700,
                  color: '#00f0ff',
                  backgroundColor: 'rgba(0, 240, 255, 0.1)',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  fontFamily: "'JetBrains Mono', monospace"
                }}>
                  {sc.id} • {sc.category}
                </span>
                <span style={{ fontSize: '11px', color: '#8b5cf6', fontWeight: 600 }}>
                  {sc.difficulty}
                </span>
              </div>

              <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#ffffff', marginBottom: '6px' }}>
                {sc.title}
              </h4>
              <p style={{ fontSize: '12px', color: '#94a3b8', lineHeight: '1.4' }}>
                {sc.desc}
              </p>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '12px', fontFamily: "'JetBrains Mono', monospace" }}>
                {sc.specs}
              </div>

              <button
                onClick={() => navigate(`/simulation?scenario=${sc.id}`)}
                style={{
                  width: '100%',
                  backgroundColor: '#131c31',
                  color: '#00f0ff',
                  border: '1px solid rgba(0, 240, 255, 0.3)',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  fontSize: '12px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px'
                }}
              >
                <Play size={14} />
                <span>Open Simulation</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
