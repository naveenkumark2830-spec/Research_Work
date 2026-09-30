import React, { useState } from 'react';
import { Mic, Send, Square, Volume2, Sparkles, Compass, ChevronUp, ChevronDown, MessageSquare } from 'lucide-react';

export type TeddyStatus = 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING' | 'PAUSED';

export interface ChatHistoryItem {
  role: 'USER' | 'TEDDY';
  content: string;
  time?: string;
}

interface FloatingCommandBarProps {
  onSendCommand: (cmd: string) => void;
  status: TeddyStatus;
  isVoiceMode: boolean;
  onToggleVoiceMode: () => void;
  onStopAudio?: () => void;
  liveTranscript?: string;
  chatHistory?: ChatHistoryItem[];
}

export const FloatingCommandBar: React.FC<FloatingCommandBarProps> = ({
  onSendCommand,
  status,
  isVoiceMode,
  onToggleVoiceMode,
  onStopAudio,
  liveTranscript = '',
  chatHistory = []
}) => {
  const [text, setText] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const presets = [
    'Write 1 GB file with 128 MB blocks',
    'Simulate DataNode 3 hardware crash',
    'Run MapReduce WordCount execution',
    'Add 3 DataNodes and rebalance'
  ];

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSendCommand(text.trim());
    setText('');
    setShowSuggestions(false);
  };

  const handleSelectPreset = (preset: string) => {
    onSendCommand(preset);
    setShowSuggestions(false);
  };

  const getStatusColor = () => {
    switch (status) {
      case 'SPEAKING': return '#00f0ff';
      case 'LISTENING': return '#0ea5e9';
      case 'THINKING': return '#8b5cf6';
      case 'PAUSED': return '#ef4444';
      default: return '#22c55e';
    }
  };

  const statusColor = getStatusColor();

  return (
    <div style={{
      position: 'absolute',
      bottom: '24px',
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 50,
      width: '90%',
      maxWidth: '680px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '10px'
    }}>
      {/* Collapsible Chat History Drawer */}
      {showHistory && (
        <div style={{
          width: '100%',
          maxHeight: '280px',
          backgroundColor: 'rgba(14, 21, 38, 0.96)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(0, 240, 255, 0.4)',
          borderRadius: '16px',
          padding: '16px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.7), 0 0 20px rgba(0, 240, 255, 0.15)',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          overflowY: 'auto'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, color: '#00f0ff', letterSpacing: '0.8px', fontFamily: "'Space Grotesk', sans-serif" }}>
              CONVERSATION CHAT HISTORY
            </span>
            <button
              onClick={() => setShowHistory(false)}
              style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '11px', cursor: 'pointer' }}
            >
              Close ✕
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {chatHistory.length === 0 ? (
              <span style={{ fontSize: '12px', color: '#64748b' }}>No chat history yet.</span>
            ) : (
              chatHistory.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: item.role === 'USER' ? 'flex-end' : 'flex-start',
                    gap: '2px'
                  }}
                >
                  <div style={{
                    maxWidth: '85%',
                    backgroundColor: item.role === 'USER' ? 'rgba(0, 240, 255, 0.15)' : 'rgba(30, 41, 66, 0.8)',
                    border: item.role === 'USER' ? '1px solid rgba(0, 240, 255, 0.3)' : '1px solid #1e2942',
                    borderRadius: item.role === 'USER' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                    padding: '8px 12px',
                    color: '#f8fafc',
                    fontSize: '12px',
                    lineHeight: '1.4'
                  }}>
                    <strong style={{ color: item.role === 'USER' ? '#00f0ff' : '#22c55e', fontSize: '10px' }}>
                      {item.role === 'USER' ? 'YOU' : 'TEDDY'}:
                    </strong>{' '}
                    {item.content}
                  </div>
                  {item.time && <span style={{ fontSize: '9px', color: '#64748b' }}>{item.time}</span>}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Collapsible Suggestions Popover Drawer */}
      {showSuggestions && (
        <div style={{
          width: '100%',
          backgroundColor: 'rgba(14, 21, 38, 0.94)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(0, 240, 255, 0.4)',
          borderRadius: '16px',
          padding: '16px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 240, 255, 0.15)',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, color: '#00f0ff', letterSpacing: '0.8px', fontFamily: "'Space Grotesk', sans-serif" }}>
              SUGGESTED SIMULATION SCENARIOS
            </span>
            <button
              onClick={() => setShowSuggestions(false)}
              style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '11px', cursor: 'pointer' }}
            >
              Close ✕
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            {presets.map((preset, idx) => (
              <button
                key={idx}
                onClick={() => handleSelectPreset(preset)}
                style={{
                  backgroundColor: 'rgba(7, 10, 18, 0.85)',
                  color: '#cbd5e1',
                  border: '1px solid #1e2942',
                  borderRadius: '10px',
                  padding: '10px 12px',
                  fontSize: '12px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  fontWeight: 500
                }}
              >
                {preset}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Barge-In Stop Audio Pill if Speaking */}
      {status === 'SPEAKING' && onStopAudio && (
        <button
          onClick={onStopAudio}
          style={{
            backgroundColor: 'rgba(239, 68, 68, 0.9)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '20px',
            padding: '6px 14px',
            fontSize: '11px',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            boxShadow: '0 0 15px rgba(239, 68, 68, 0.4)',
            backdropFilter: 'blur(8px)'
          }}
        >
          <Square size={10} fill="#ffffff" />
          <span>TEDDY SPEAKING — CLICK OR SAY "STOP" TO PAUSE</span>
        </button>
      )}

      {/* Main Glassmorphic Command Bar */}
      <div style={{
        width: '100%',
        backgroundColor: 'rgba(14, 21, 38, 0.88)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(0, 240, 255, 0.35)',
        borderRadius: '16px',
        padding: isVoiceMode ? '16px 20px' : '10px 14px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 240, 255, 0.15)',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
      }}>
        {/* Status Indicator & Controls */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={16} color="#00f0ff" />
            <span style={{ fontSize: '12px', fontWeight: 800, color: '#ffffff', fontFamily: "'Space Grotesk', sans-serif", letterSpacing: '0.5px' }}>
              TEDDY
            </span>
            <span style={{
              fontSize: '10px',
              fontWeight: 700,
              color: statusColor,
              backgroundColor: `${statusColor}18`,
              border: `1px solid ${statusColor}40`,
              padding: '2px 8px',
              borderRadius: '10px',
              fontFamily: "'JetBrains Mono', monospace"
            }}>
              ● {status}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {/* History Drawer Toggle */}
            <button
              onClick={() => setShowHistory(!showHistory)}
              style={{
                backgroundColor: showHistory ? 'rgba(0, 240, 255, 0.15)' : 'rgba(19, 28, 49, 0.8)',
                color: showHistory ? '#00f0ff' : '#94a3b8',
                border: '1px solid',
                borderColor: showHistory ? 'rgba(0, 240, 255, 0.4)' : '#1e2942',
                borderRadius: '12px',
                padding: '3px 10px',
                fontSize: '11px',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <MessageSquare size={12} color={showHistory ? '#00f0ff' : '#94a3b8'} />
              <span>History ({chatHistory.length})</span>
            </button>

            {/* Suggestions Drawer Toggle */}
            <button
              onClick={() => setShowSuggestions(!showSuggestions)}
              style={{
                backgroundColor: showSuggestions ? 'rgba(0, 240, 255, 0.15)' : 'rgba(19, 28, 49, 0.8)',
                color: showSuggestions ? '#00f0ff' : '#94a3b8',
                border: '1px solid',
                borderColor: showSuggestions ? 'rgba(0, 240, 255, 0.4)' : '#1e2942',
                borderRadius: '12px',
                padding: '3px 10px',
                fontSize: '11px',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <Compass size={12} color={showSuggestions ? '#00f0ff' : '#94a3b8'} />
              <span>Suggestions</span>
              {showSuggestions ? <ChevronDown size={12} /> : <ChevronUp size={12} />}
            </button>
          </div>
        </div>

        {/* Form Input / Live Voice STT Interface */}
        {!isVoiceMode ? (
          <form onSubmit={handleFormSubmit} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Ask Teddy anything or command simulation (e.g., 'Write 1 GB file with 128 MB blocks')..."
              style={{
                flex: 1,
                backgroundColor: '#070a12',
                border: '1px solid #1e2942',
                borderRadius: '10px',
                padding: '10px 14px',
                color: '#f8fafc',
                fontSize: '13px',
                outline: 'none',
                fontFamily: "'Inter', sans-serif"
              }}
            />

            <button
              type="button"
              onClick={onToggleVoiceMode}
              title="Activate Live Voice Mode"
              style={{
                backgroundColor: '#131c31',
                color: '#94a3b8',
                border: '1px solid #1e2942',
                borderRadius: '10px',
                width: '40px',
                height: '40px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer'
              }}
            >
              <Mic size={18} />
            </button>

            <button
              type="submit"
              disabled={!text.trim()}
              style={{
                backgroundColor: '#00f0ff',
                color: '#070a12',
                border: 'none',
                borderRadius: '10px',
                width: '40px',
                height: '40px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: text.trim() ? 'pointer' : 'not-allowed',
                opacity: text.trim() ? 1 : 0.4
              }}
            >
              <Send size={16} />
            </button>
          </form>
        ) : (
          /* Live Speech-to-Text Transcription State */
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#070a12', padding: '12px 16px', borderRadius: '10px', border: '1px solid rgba(0, 240, 255, 0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, overflow: 'hidden' }}>
              <Volume2 size={20} color="#00f0ff" className="animate-neon-pulse" />
              <span style={{ fontSize: '13px', color: liveTranscript ? '#00f0ff' : '#f8fafc', fontWeight: 600, fontFamily: "'Inter', sans-serif" }}>
                {liveTranscript ? `🎙️ "${liveTranscript}"` : 'Listening live... Speak naturally to Teddy...'}
              </span>
            </div>

            <button
              onClick={onToggleVoiceMode}
              style={{
                backgroundColor: '#131c31',
                color: '#00f0ff',
                border: '1px solid rgba(0, 240, 255, 0.4)',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '12px',
                fontWeight: 700,
                cursor: 'pointer',
                flexShrink: 0
              }}
            >
              Switch to Text Input
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
