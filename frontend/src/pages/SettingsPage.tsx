import React, { useState } from 'react';
import { Volume2, Sliders, User } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [uiSoundsEnabled, setUiSoundsEnabled] = useState(false);
  const [voiceSpeed, setVoiceSpeed] = useState(1.0);
  const [voiceGender, setVoiceGender] = useState<string>(() => localStorage.getItem('teddy_voice_gender') || 'female');
  const [defaultBlockSize, setDefaultBlockSize] = useState(128);
  const [defaultReplication, setDefaultReplication] = useState(3);

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Page Header */}
      <div>
        <div style={{ fontSize: '22px', fontWeight: 800, color: '#ffffff', marginBottom: '6px' }}>
          Settings
        </div>
        <div style={{ fontSize: '14px', color: '#94a3b8' }}>
          Configure TEDDY assistant behavior, audio synthesis, and default simulation parameters.
        </div>
      </div>

      {/* Settings Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Account Profile */}
        <div style={{ backgroundColor: '#0e1526', border: '1px solid #1e2942', borderRadius: '10px', padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <User size={18} color="#00f0ff" />
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#ffffff' }}>Account & Profile</h3>
          </div>

          <div style={{ fontSize: '13px', color: '#cbd5e1' }}>
            Active Profile: <strong style={{ color: '#00f0ff' }}>Evaluator Account</strong>
          </div>
        </div>

        {/* TEDDY Voice Settings */}
        <div style={{ backgroundColor: '#0e1526', border: '1px solid #1e2942', borderRadius: '10px', padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Volume2 size={18} color="#0ea5e9" />
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#ffffff' }}>TEDDY Voice & Audio</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '13px', color: '#cbd5e1' }}>Enable Speech Audio Synthesis</span>
              <input
                type="checkbox"
                checked={voiceEnabled}
                onChange={(e) => setVoiceEnabled(e.target.checked)}
                style={{ width: '18px', height: '18px', cursor: 'pointer' }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '13px', color: '#cbd5e1' }}>Voice Gender</span>
              <select
                value={voiceGender}
                onChange={(e) => {
                  setVoiceGender(e.target.value);
                  localStorage.setItem('teddy_voice_gender', e.target.value);
                }}
                style={{
                  backgroundColor: '#070a12',
                  border: '1px solid #1e2942',
                  borderRadius: '6px',
                  padding: '4px 8px',
                  color: '#00f0ff',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                <option value="female">Female (Default)</option>
                <option value="male">Male</option>
              </select>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '13px', color: '#cbd5e1', display: 'block' }}>Tactile UI Sound Layer</span>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Soft audio feedback on button clicks & route transitions</span>
              </div>
              <input
                type="checkbox"
                checked={uiSoundsEnabled}
                onChange={(e) => setUiSoundsEnabled(e.target.checked)}
                style={{ width: '18px', height: '18px', cursor: 'pointer' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Voice Speed ({voiceSpeed}x)</label>
              <input
                type="range"
                min="0.75"
                max="1.5"
                step="0.25"
                value={voiceSpeed}
                onChange={(e) => setVoiceSpeed(Number(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>
          </div>
        </div>

        {/* Simulation Defaults */}
        <div style={{ backgroundColor: '#0e1526', border: '1px solid #1e2942', borderRadius: '10px', padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Sliders size={18} color="#8b5cf6" />
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#ffffff' }}>Simulation Defaults</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Default Block Size (MB)</label>
              <input
                type="number"
                value={defaultBlockSize}
                onChange={(e) => setDefaultBlockSize(Number(e.target.value))}
                style={{
                  width: '100%',
                  backgroundColor: '#070a12',
                  border: '1px solid #1e2942',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: '13px',
                  fontFamily: "'JetBrains Mono', monospace"
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '12px', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Default Replication Factor</label>
              <input
                type="number"
                value={defaultReplication}
                onChange={(e) => setDefaultReplication(Number(e.target.value))}
                style={{
                  width: '100%',
                  backgroundColor: '#070a12',
                  border: '1px solid #1e2942',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: '13px',
                  fontFamily: "'JetBrains Mono', monospace"
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
