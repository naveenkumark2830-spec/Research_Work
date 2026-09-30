import { useState, useEffect, useCallback, useRef } from 'react';
import { TeddyOrbMode } from '../components/teddy/TeddyOrb';
import { teddyAudioEngine } from '../utils/teddyAudioEngine';

export interface UseTeddyVoiceOptions {
  onCommandExecuted?: (command: string) => void;
  onStopCommand?: () => void;
  onStartCommand?: () => void;
}

export interface NarrationStep {
  step: string;
  text: string;
}

const WAKE_PHRASES = [
  'wake up teddy',
  'wake up',
  'wake teddy',
  'hey teddy',
  'hello teddy',
  'ok teddy',
  'teddy'
];

export function isWakePhrase(text: string): boolean {
  const normalized = text.toLowerCase().trim();
  return WAKE_PHRASES.some(phrase => normalized.includes(phrase));
}

export function unlockAudioOnce() {
  teddyAudioEngine.unlock();
}

export function useTeddyVoice(options: UseTeddyVoiceOptions = {}) {
  const { onCommandExecuted, onStopCommand, onStartCommand } = options;

  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [orbMode, setOrbMode] = useState<TeddyOrbMode>('idle');
  const [transcript, setTranscript] = useState('');
  const [amplitude, setAmplitude] = useState(0.15);

  const recognitionRef = useRef<any>(null);
  const isStoppedRef = useRef(false);

  // Guaranteed Audible Voice Output (Web Audio Synth + SpeechSynthesis Dual Engine)
  const speakText = useCallback((text: string, onEndCallback?: () => void) => {
    isStoppedRef.current = false;
    console.log('[TEDDY VOICE] speakText:', text);
    setIsSpeaking(true);
    setOrbMode('speaking');

    teddyAudioEngine.speak(text, () => {
      setIsSpeaking(false);
      setOrbMode(isListening ? 'listening' : 'idle');
      if (!isStoppedRef.current) onEndCallback?.();
    });
  }, [isListening]);

  const stopAudio = useCallback(() => {
    isStoppedRef.current = true;
    teddyAudioEngine.stop();
    setIsSpeaking(false);
    setOrbMode('idle');
  }, []);

  // Chained Narration Queue driven by teddyAudioEngine
  const playNarration = useCallback((
    queue: NarrationStep[],
    onStepVisual: (step: string, text: string) => void,
    onAllDone?: () => void
  ) => {
    isStoppedRef.current = false;
    let i = 0;

    const nextStep = () => {
      if (isStoppedRef.current || i >= queue.length) {
        setIsSpeaking(false);
        setOrbMode(isListening ? 'listening' : 'idle');
        if (!isStoppedRef.current) onAllDone?.();
        return;
      }

      const { step, text } = queue[i];
      onStepVisual(step, text);
      setIsSpeaking(true);
      setOrbMode('speaking');

      teddyAudioEngine.speak(text, () => {
        if (!isStoppedRef.current) {
          i++;
          nextStep();
        }
      });
    };

    nextStep();
  }, [isListening]);

  // Audio Amplitude Visualizer
  useEffect(() => {
    let audioCtx: AudioContext | null = null;
    let animId: number | null = null;
    let stream: MediaStream | null = null;

    if (isVoiceActive && isListening) {
      if (typeof navigator !== 'undefined' && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true }).then((micStream) => {
          stream = micStream;
          audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
          const analyser = audioCtx.createAnalyser();
          analyser.fftSize = 256;
          const source = audioCtx.createMediaStreamSource(micStream);
          source.connect(analyser);

          const data = new Uint8Array(analyser.frequencyBinCount);
          const tick = () => {
            analyser.getByteFrequencyData(data);
            const avg = data.reduce((a, b) => a + b, 0) / data.length / 255;
            setAmplitude(avg);
            animId = requestAnimationFrame(tick);
          };
          tick();
        }).catch(() => {
          let phase = 0;
          const timer = setInterval(() => {
            phase += 0.1;
            setAmplitude(0.2 + Math.sin(phase) * 0.15);
          }, 100);
          return () => clearInterval(timer);
        });
      }
    } else if (isSpeaking) {
      let phase = 0;
      const timer = setInterval(() => {
        phase += 0.2;
        setAmplitude(0.35 + Math.sin(phase) * 0.25);
      }, 80);
      return () => clearInterval(timer);
    } else {
      setAmplitude(0.15);
    }

    return () => {
      if (animId) cancelAnimationFrame(animId);
      if (audioCtx) audioCtx.close();
      if (stream) stream.getTracks().forEach(t => t.stop());
    };
  }, [isVoiceActive, isListening, isSpeaking]);

  // Speech Recognition (Controlled by isVoiceActive)
  useEffect(() => {
    if (typeof window === 'undefined' || !isVoiceActive) return;

    const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognitionAPI) return;

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event: any) => {
      let currentResult = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        currentResult += event.results[i][0].transcript;
      }
      setTranscript(currentResult);

      if (isWakePhrase(currentResult)) {
        speakText("Hello boss, I'm ready.");
        return;
      }

      if (event.results[event.results.length - 1].isFinal) {
        const lower = currentResult.toLowerCase().trim();
        if (lower.includes('stop') || lower.includes('pause') || lower.includes('halt')) {
          onStopCommand?.();
          stopAudio();
          speakText("Simulation paused.");
        } else if (lower.includes('start') || lower.includes('continue') || lower.includes('resume')) {
          onStartCommand?.();
          speakText("Resuming simulation.");
        } else if (lower.length > 3) {
          onCommandExecuted?.(currentResult);
        }
      }
    };

    recognition.onstart = () => {
      setIsListening(true);
      setOrbMode('listening');
    };

    recognition.onend = () => {
      if (isVoiceActive) {
        try {
          recognition.start();
        } catch (_) {}
      } else {
        setIsListening(false);
        setOrbMode('idle');
      }
    };

    try {
      recognition.start();
    } catch (_) {}

    recognitionRef.current = recognition;

    return () => {
      try {
        recognition.stop();
      } catch (_) {}
    };
  }, [isVoiceActive, onCommandExecuted, onStopCommand, onStartCommand, speakText, stopAudio]);

  const toggleVoiceActive = useCallback(() => {
    teddyAudioEngine.unlock();
    if (isVoiceActive) {
      setIsVoiceActive(false);
      stopAudio();
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (_) {}
      }
      setIsListening(false);
      setOrbMode('idle');
    } else {
      setIsVoiceActive(true);
      setIsListening(true);
      setOrbMode('listening');
      speakText("Hello boss, I'm ready.");
    }
  }, [isVoiceActive, speakText, stopAudio]);

  return {
    isVoiceActive,
    isListening,
    isSpeaking,
    orbMode,
    transcript,
    amplitude,
    toggleVoiceActive,
    speakText,
    stopAudio,
    playNarration,
    stopNarration: stopAudio
  };
}
