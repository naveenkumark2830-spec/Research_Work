import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Send, Sparkles } from 'lucide-react';

interface Message {
  id: string;
  sender: 'user' | 'teddy';
  text: string;
  intent?: string;
  sources?: string[];
}

interface TeddyAssistantRailProps {
  onExecuteCommand?: (cmd: string) => void;
}

export const TeddyAssistantRail: React.FC<TeddyAssistantRailProps> = ({ onExecuteCommand }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'init-1',
      sender: 'teddy',
      text: 'TEDDY system online. I am observing the Hadoop cluster. What would you like to simulate or configure?',
    },
  ]);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState<'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING' | 'PAUSED'>('IDLE');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText) return;

    setInput('');
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: messageText,
    };

    setMessages((prev) => [...prev, userMsg]);
    setStatus('THINKING');

    if (onExecuteCommand) {
      onExecuteCommand(messageText);
    }

    setTimeout(() => {
      let responseText = `Processing command: "${messageText}". Cluster topology updated.`;
      let intentName = 'EXECUTE_SIMULATION';

      const lower = messageText.toLowerCase();
      if (lower.includes('stop') || lower.includes('pause')) {
        responseText = 'Pausing the simulation. Current execution state and event cursor are preserved.';
        intentName = 'STOP';
        setStatus('PAUSED');
      } else if (lower.includes('why') || lower.includes('block')) {
        responseText = 'The file currently contains 8 blocks because the 1024 MB input file is split into 128 MB blocks.';
        intentName = 'EXPLAIN';
        setStatus('SPEAKING');
      } else if (lower.includes('continue') || lower.includes('resume')) {
        responseText = 'Continuing execution from current simulation state.';
        intentName = 'RESUME';
        setStatus('IDLE');
      } else {
        setStatus('SPEAKING');
      }

      setMessages((prev) => [
        ...prev,
        {
          id: `teddy-${Date.now()}`,
          sender: 'teddy',
          text: responseText,
          intent: intentName,
        },
      ]);
    }, 600);
  };

  const handleStopBargeIn = () => {
    setStatus('PAUSED');
    setMessages((prev) => [
      ...prev,
      {
        id: `stop-${Date.now()}`,
        sender: 'teddy',
        text: 'Simulation speech audio stopped. Execution state paused.',
        intent: 'STOP',
      },
    ]);
  };

  return (
    <div style={{
      width: '320px',
      backgroundColor: '#0e1526',
      borderLeft: '1px solid #1e2942',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      flexShrink: 0
    }}>
      {/* Assistant Header */}
      <div style={{
        padding: '14px 16px',
        backgroundColor: '#131c31',
        borderBottom: '1px solid #1e2942',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={16} color="#00f0ff" />
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc', letterSpacing: '0.5px' }}>
              TEDDY
            </div>
            <div style={{ fontSize: '10px', color: '#94a3b8' }}>
              Simulation Assistant
            </div>
          </div>
        </div>

        {/* Status Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          backgroundColor: '#070a12',
          padding: '3px 8px',
          borderRadius: '12px',
          border: '1px solid #1e2942',
          fontSize: '10px',
          fontWeight: 700,
          color: status === 'SPEAKING' ? '#00f0ff' : status === 'PAUSED' ? '#ef4444' : '#22c55e'
        }}>
          <span style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: status === 'SPEAKING' ? '#00f0ff' : status === 'PAUSED' ? '#ef4444' : '#22c55e'
          }} />
          <span>{status}</span>
        </div>
      </div>

      {/* Suggestion Chips */}
      <div style={{
        padding: '8px 12px',
        backgroundColor: '#070a12',
        borderBottom: '1px solid #1e2942',
        display: 'flex',
        gap: '6px',
        overflowX: 'auto',
        whiteSpace: 'nowrap'
      }}>
        {[
          '1 GB file with 128 MB blocks',
          'Why are there 8 blocks?',
          'Kill DataNode 3',
          'Recover DataNode 3',
          'Teddy, stop',
          'Continue'
        ].map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(chip)}
            style={{
              backgroundColor: '#131c31',
              color: '#94a3b8',
              border: '1px solid #1e2942',
              borderRadius: '12px',
              padding: '3px 8px',
              fontSize: '11px',
              cursor: 'pointer',
              flexShrink: 0
            }}
          >
            {chip.length > 20 ? chip.substring(0, 20) + '...' : chip}
          </button>
        ))}
      </div>

      {/* Conversation Area */}
      <div style={{
        flex: 1,
        padding: '12px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
      }}>
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '90%',
              backgroundColor: m.sender === 'user' ? '#0284c7' : '#131c31',
              padding: '8px 12px',
              borderRadius: '8px',
              fontSize: '12px',
              lineHeight: '1.4',
              color: '#f8fafc',
              border: '1px solid',
              borderColor: m.sender === 'user' ? '#0369a1' : '#1e2942'
            }}
          >
            {m.intent && (
              <div style={{ marginBottom: '4px', display: 'flex', gap: '4px' }}>
                <span style={{
                  fontSize: '9px',
                  backgroundColor: '#070a12',
                  color: '#00f0ff',
                  padding: '1px 5px',
                  borderRadius: '3px',
                  fontFamily: "'JetBrains Mono', monospace",
                  fontWeight: 700
                }}>
                  {m.intent}
                </span>
              </div>
            )}
            <div>{m.text}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form & Barge-in Controls */}
      <div style={{ padding: '12px', backgroundColor: '#131c31', borderTop: '1px solid #1e2942' }}>
        {status === 'SPEAKING' && (
          <button
            onClick={handleStopBargeIn}
            style={{
              width: '100%',
              marginBottom: '8px',
              backgroundColor: '#ef4444',
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              padding: '6px 12px',
              fontSize: '11px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
          >
            <Square size={12} fill="#ffffff" />
            <span>STOP AUDIO (BARGE-IN)</span>
          </button>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          style={{ display: 'flex', gap: '6px', alignItems: 'center' }}
        >
          <button
            type="button"
            style={{
              backgroundColor: '#070a12',
              color: '#94a3b8',
              border: '1px solid #1e2942',
              borderRadius: '6px',
              width: '32px',
              height: '32px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title="Microphone Input"
          >
            <Mic size={14} />
          </button>

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Teddy..."
            style={{
              flex: 1,
              backgroundColor: '#070a12',
              border: '1px solid #1e2942',
              borderRadius: '6px',
              padding: '8px 10px',
              color: '#f8fafc',
              fontSize: '12px',
              outline: 'none'
            }}
          />

          <button
            type="submit"
            disabled={!input.trim()}
            style={{
              backgroundColor: '#00f0ff',
              color: '#070a12',
              border: 'none',
              borderRadius: '6px',
              width: '32px',
              height: '32px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              opacity: !input.trim() ? 0.5 : 1
            }}
          >
            <Send size={14} />
          </button>
        </form>
      </div>
    </div>
  );
};
