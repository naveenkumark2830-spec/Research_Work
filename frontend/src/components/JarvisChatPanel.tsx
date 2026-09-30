import React, { useState, useRef, useEffect } from 'react';
import { aiApi, JarvisResponse } from '../api/aiApi';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  intent?: string;
  visualActions?: Array<{ type: string; target?: string; text?: string }>;
  sources?: string[];
  error?: string;
}

interface JarvisChatPanelProps {
  sessionId: string;
  userId: string;
  selectedComponent?: string | null;
  selectedComponentType?: string | null;
  onActionExecuted: () => void;
}

export const JarvisChatPanel: React.FC<JarvisChatPanelProps> = ({
  sessionId,
  userId,
  selectedComponent: _selectedComponent,
  selectedComponentType: _selectedComponentType,
  onActionExecuted,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'assistant',
      text: 'Greetings! I am JARVIS, powered by Gemini. You can control the Hadoop simulation naturally using speech or text.',
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Audio Barge-in / Immediate Stop function
  const stopSpeechAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsSpeaking(false);
  };

  const handleBargeIn = async () => {
    stopSpeechAudio();
    // Send STOP / PAUSE intent to backend to pause simulation state
    try {
      const resp = await aiApi.sendJarvisMessage(sessionId, userId, 'Jarvis, stop');
      setMessages((prev) => [
        ...prev,
        {
          id: `user-stop-${Date.now()}`,
          sender: 'user',
          text: 'Jarvis, stop',
        },
        {
          id: `ai-stop-${Date.now()}`,
          sender: 'assistant',
          text: resp.text,
          intent: resp.intent,
          visualActions: resp.visual_actions,
        },
      ]);
      onActionExecuted();
    } catch (e) {
      // Ignore
    }
  };

  const playSpeechSynthesis = (text: string) => {
    stopSpeechAudio();
    const url = aiApi.synthesizeSpeechUrl(text);
    const audio = new Audio();
    audioRef.current = audio;
    audio.src = `${url}?text=${encodeURIComponent(text.substring(0, 200))}`;

    audio.onplay = () => setIsSpeaking(true);
    audio.onended = () => setIsSpeaking(false);
    audio.onerror = () => setIsSpeaking(false);

    audio.play().catch(() => setIsSpeaking(false));
  };

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || inputMessage.trim();
    if (!textToSend || loading) return;

    setInputMessage('');
    stopSpeechAudio();

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: textToSend,
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response: JarvisResponse = await aiApi.sendJarvisMessage(
        sessionId,
        userId,
        textToSend
      );

      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        sender: 'assistant',
        text: response.text,
        intent: response.intent,
        visualActions: response.visual_actions,
        sources: response.sources,
      };

      setMessages((prev) => [...prev, aiMsg]);

      // Trigger speech synthesis if enabled
      if (response.text) {
        playSpeechSynthesis(response.text);
      }

      onActionExecuted();
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'assistant',
          text: `JARVIS Error: ${err.message || 'Unable to connect to backend'}`,
          error: err.message,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Microphone Speech Capture (STT)
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        try {
          const transcribedText = await aiApi.transcribeAudio(audioBlob);
          if (transcribedText) {
            handleSend(transcribedText);
          }
        } catch (err) {
          console.error('Transcription error:', err);
        } finally {
          stream.getTracks().forEach((track) => track.stop());
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      alert('Microphone access denied or unavailable.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '420px',
      backgroundColor: '#0f172a',
      borderRadius: '10px',
      border: '1px solid #334155',
      color: '#f8fafc',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)',
      overflow: 'hidden'
    }}>
      {/* Panel Header */}
      <div style={{
        padding: '10px 16px',
        backgroundColor: '#1e293b',
        borderBottom: '1px solid #334155',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '18px' }}>⚡</span>
          <div>
            <strong style={{ fontSize: '14px', letterSpacing: '0.5px', color: '#38bdf8' }}>JARVIS AI Orchestrator</strong>
            <span style={{ fontSize: '10px', color: '#94a3b8', display: 'block' }}>Gemini 2.5 Flash • Hadoop Simulator</span>
          </div>
        </div>

        {/* Barge-in / Speaking Status Indicator */}
        {isSpeaking ? (
          <button
            onClick={handleBargeIn}
            style={{
              backgroundColor: '#ef4444',
              color: '#ffffff',
              border: 'none',
              borderRadius: '20px',
              padding: '4px 12px',
              fontSize: '11px',
              fontWeight: 'bold',
              cursor: 'pointer',
              animation: 'pulse 1.5s infinite',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            🛑 SPEAKING (BARGE-IN)
          </button>
        ) : (
          <span style={{ fontSize: '11px', backgroundColor: '#0f172a', color: '#22c55e', padding: '3px 8px', borderRadius: '4px', border: '1px solid #166534' }}>
            ● ONLINE
          </span>
        )}
      </div>

      {/* Suggestion Chips */}
      <div style={{
        padding: '6px 12px',
        backgroundColor: '#1e293b',
        borderBottom: '1px solid #334155',
        display: 'flex',
        gap: '6px',
        overflowX: 'auto',
        whiteSpace: 'nowrap'
      }}>
        {[
          'Jarvis, create a 1 GB HDFS file using 128 MB blocks and replication factor 3.',
          'Why are there 8 blocks?',
          'Quiz me on HDFS.',
          'Kill DataNode 3.',
          'Recover DataNode 3.',
          'Jarvis, stop.',
          'Continue.'
        ].map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(chip)}
            style={{
              backgroundColor: '#334155',
              color: '#cbd5e1',
              border: 'none',
              borderRadius: '12px',
              padding: '3px 10px',
              fontSize: '11px',
              cursor: 'pointer',
              flexShrink: 0
            }}
          >
            {chip.length > 32 ? chip.substring(0, 32) + '...' : chip}
          </button>
        ))}
      </div>

      {/* Messages Scroll Area */}
      <div style={{
        flex: 1,
        padding: '14px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px'
      }}>
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '88%',
              backgroundColor: m.sender === 'user' ? '#0284c7' : '#1e293b',
              padding: '10px 14px',
              borderRadius: '10px',
              borderBottomRightRadius: m.sender === 'user' ? '2px' : '10px',
              borderBottomLeftRadius: m.sender === 'assistant' ? '2px' : '10px',
              fontSize: '13px',
              lineHeight: '1.5',
              border: '1px solid',
              borderColor: m.sender === 'user' ? '#0369a1' : '#334155'
            }}
          >
            {m.intent && (
              <div style={{ marginBottom: '6px', display: 'flex', gap: '6px', alignItems: 'center', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '10px', backgroundColor: '#0f172a', padding: '2px 6px', borderRadius: '4px', color: '#38bdf8', fontWeight: 'bold' }}>
                  {m.intent}
                </span>
                {m.visualActions && m.visualActions.map((va, i) => (
                  <span key={i} style={{ fontSize: '10px', backgroundColor: '#4338ca', color: '#e0e7ff', padding: '2px 6px', borderRadius: '4px' }}>
                    ⚡ {va.type}
                  </span>
                ))}
              </div>
            )}
            <div style={{ whiteSpace: 'pre-wrap' }}>{m.text}</div>
            {m.sources && m.sources.length > 0 && (
              <div style={{ marginTop: '6px', fontSize: '10px', color: '#94a3b8', borderTop: '1px solid #334155', paddingTop: '4px' }}>
                Source: {m.sources.join(', ')}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: 'flex-start', color: '#94a3b8', fontSize: '12px', fontStyle: 'italic' }}>
            JARVIS is reasoning with Gemini...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        style={{
          padding: '10px',
          backgroundColor: '#1e293b',
          borderTop: '1px solid #334155',
          display: 'flex',
          gap: '8px',
          alignItems: 'center'
        }}
      >
        <button
          type="button"
          onClick={isRecording ? stopRecording : startRecording}
          style={{
            backgroundColor: isRecording ? '#ef4444' : '#334155',
            color: '#ffffff',
            border: 'none',
            borderRadius: '50%',
            width: '36px',
            height: '36px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '16px'
          }}
          title={isRecording ? 'Stop Recording' : 'Microphone Voice Input'}
        >
          {isRecording ? '⏹️' : '🎙️'}
        </button>

        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask JARVIS or command HDFS (e.g. Create 1GB file, Why 8 blocks?)..."
          disabled={loading}
          style={{
            flex: 1,
            backgroundColor: '#0f172a',
            border: '1px solid #475569',
            borderRadius: '6px',
            padding: '10px 12px',
            color: '#f8fafc',
            fontSize: '13px',
            outline: 'none'
          }}
        />
        <button
          type="submit"
          disabled={loading || !inputMessage.trim()}
          style={{
            backgroundColor: '#0284c7',
            color: '#ffffff',
            border: 'none',
            borderRadius: '6px',
            padding: '10px 18px',
            fontWeight: 'bold',
            fontSize: '13px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading || !inputMessage.trim() ? 0.6 : 1
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
};
