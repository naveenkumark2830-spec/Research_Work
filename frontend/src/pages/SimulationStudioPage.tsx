import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Maximize2, Minimize2, Sparkles, Clock, RotateCcw, Volume2 } from 'lucide-react';
import { HDFSClusterView, InspectorTarget } from '../visualization';
import { FloatingCommandBar, TeddyStatus } from '../components/teddy/FloatingCommandBar';
import { TeddyExplanationOverlay } from '../components/teddy/TeddyExplanationOverlay';
import { CosmicNebulaCanvas } from '../components/teddy/CosmicNebulaCanvas';
import { useTeddyVoice, NarrationStep, unlockAudioOnce } from '../hooks/useTeddyVoice';
import { aiApi, TeddyResponse } from '../api/aiApi';
import { sessionApi } from '../api/sessionClient';

export const SimulationStudioPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [isActiveSimulation, setIsActiveSimulation] = useState(true);
  const [status, setStatus] = useState<'IDLE' | 'RUNNING' | 'PAUSED'>('RUNNING');
  const [teddyStatus, setTeddyStatus] = useState<TeddyStatus>('IDLE');
  const [explanationText, setExplanationText] = useState<string | null>("Welcome boss! I am TEDDY, your AI Hadoop Assistant. Ask me any question or give a simulation command.");
  const [sources, setSources] = useState<string[]>([]);
  const [isImmersiveMode, setIsImmersiveMode] = useState(false);
  const [showTimeline, setShowTimeline] = useState(false);
  const [selectedTarget, setSelectedTarget] = useState<InspectorTarget | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [dynamicScene, setDynamicScene] = useState<any | null>(null);

  const userId = useRef(`user-${Math.random().toString(36).substring(2, 9)}`).current;

  // Initialize backend HDFS session on mount
  useEffect(() => {
    async function initSession() {
      try {
        const res = await sessionApi.createSession(userId);
        const sId = res?.session?.session_id || (res as any)?.session_id;
        if (sId) {
          setSessionId(sId);
          console.log('[HDFS SIMULATOR] Backend Session initialized:', sId);
        }
      } catch (err) {
        console.warn('[HDFS SIMULATOR] Session init warning, using fallback session ID:', err);
        setSessionId(`sess_${Date.now()}`);
      }
    }
    initSession();
  }, [userId]);

  // Sequential Choreography Stage (0: Clean Idle, 1: Client, 2: NameNode, 3: Connections, 4..8: DataNodes 1..5, 9: Complete)
  const [assemblyStage, setAssemblyStage] = useState<number>(0);

  const containerRef = useRef<HTMLDivElement>(null);

  const narrationQueue: NarrationStep[] = [
    { step: 'dfs-client', text: "1. DFS Client initializes write pipeline for 1 GB file." },
    { step: 'namenode', text: "2. Active NameNode assigns 128 MB logical block locations." },
    { step: 'connections', text: "3. Connecting metadata routes to default storage rack." },
    { step: 'datanode-1', text: "4. DataNode 1 online, selected for primary block replica." },
    { step: 'datanode-2', text: "5. DataNode 2 online, selected for secondary block replica." },
    { step: 'datanode-3', text: "6. DataNode 3 online, selected for rack-aware replica." },
    { step: 'datanode-4', text: "7. DataNode 4 online, capacity balanced." },
    { step: 'datanode-5', text: "8. DataNode 5 online, capacity balanced." },
    { step: 'complete', text: "9. Pipeline complete. 128 MB blocks streaming and replicating across rack." }
  ];

  const [chatHistory, setChatHistory] = useState<Array<{ role: 'USER' | 'TEDDY'; content: string; time?: string }>>([
    { role: 'TEDDY', content: "Welcome boss! I am TEDDY, your AI Hadoop Assistant. Ask me any question or give a simulation command.", time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
  ]);

  // Wire Voice Hook
  const {
    isVoiceActive,
    orbMode,
    amplitude,
    transcript,
    toggleVoiceActive,
    speakText,
    stopAudio,
    playNarration,
    stopNarration
  } = useTeddyVoice({
    onCommandExecuted: (cmd) => handleSendCommand(cmd),
    onStopCommand: () => handleStopAudio(),
    onStartCommand: () => setStatus('RUNNING')
  });

  // Chained Sequential Assembly & Voice Narration
  const startActiveSimulation = (_cmdText: string) => {
    unlockAudioOnce();
    setIsActiveSimulation(true);
    setStatus('RUNNING');
    setTeddyStatus('SPEAKING');

    playNarration(
      narrationQueue,
      (stepKey, text) => {
        setExplanationText(text);
        if (stepKey === 'dfs-client') setAssemblyStage(1);
        else if (stepKey === 'namenode') setAssemblyStage(2);
        else if (stepKey === 'connections') setAssemblyStage(3);
        else if (stepKey.startsWith('datanode-')) {
          const num = parseInt(stepKey.split('-')[1], 10);
          setAssemblyStage(3 + num);
        } else if (stepKey === 'complete') {
          setAssemblyStage(9);
        }
      },
      () => {
        setTeddyStatus('IDLE');
        setStatus('RUNNING');
      }
    );
  };

  const handleResetSimulation = () => {
    stopNarration();
    setIsActiveSimulation(true);
    setStatus('RUNNING');
    setTeddyStatus('IDLE');
    setExplanationText(null);
    setSources([]);
    setAssemblyStage(0);
    setDynamicScene(null);
  };

  const handleSendCommand = async (cmdText: string) => {
    if (!cmdText.trim()) return;
    unlockAudioOnce();

    const lower = cmdText.toLowerCase();

    if (lower.includes('stop') || lower.includes('pause')) {
      handleStopAudio();
      return;
    }

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setChatHistory((prev) => [...prev, { role: 'USER', content: cmdText, time: timeStr }]);

    setTeddyStatus('THINKING');
    setIsActiveSimulation(true);
    setStatus('RUNNING');

    const activeSessId = sessionId || `sess_${Date.now()}`;

    try {
      const response: TeddyResponse = await aiApi.sendTeddyChat(activeSessId, userId, cmdText);
      console.log('[TEDDY RESPONSE]:', response);

      const plan = response.plan;
      const answerText = plan.answer || 'Command processed by Teddy Orchestrator.';
      const spokenText = plan.voice_text || plan.answer || 'Operation completed.';

      setSources(plan.sources || []);
      setChatHistory((prev) => [...prev, { role: 'TEDDY', content: answerText, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);

      // If visualization steps exist, play step-by-step voice & text narration
      if (plan.visualization && plan.visualization.length > 0) {
        const dynamicSteps: NarrationStep[] = plan.visualization.map((step: any, idx: number) => ({
          step: `step-${idx + 1}`,
          text: `${step.title}: ${step.description}`
        }));

        setTeddyStatus('SPEAKING');
        playNarration(
          dynamicSteps,
          (_stepKey, stepText) => {
            setExplanationText(stepText);
          },
          () => {
            setTeddyStatus('IDLE');
            setExplanationText(answerText);
          }
        );
      } else {
        setExplanationText(answerText);
        setTeddyStatus('SPEAKING');
        speakText(spokenText, () => {
          setTeddyStatus('IDLE');
        });
      }

      // Update cluster visualization dynamically if backend provided scene
      if (response.visualization_scene) {
        setDynamicScene(response.visualization_scene);
        setAssemblyStage(9);
      } else if (response.simulation_state) {
        setAssemblyStage(9);
      }
    } catch (err) {
      console.error('[TEDDY CHAT ERROR]:', err);
      const fallbackText = `Processing command: "${cmdText}". HDFS block distribution updated.`;
      setExplanationText(fallbackText);
      setChatHistory((prev) => [...prev, { role: 'TEDDY', content: fallbackText, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
      setTeddyStatus('SPEAKING');
      speakText(fallbackText, () => setTeddyStatus('IDLE'));
    }
  };

  const handleStopAudio = () => {
    stopNarration();
    stopAudio();
    setStatus('PAUSED');
    setTeddyStatus('PAUSED');
    setExplanationText('Speech audio halted. Simulation execution paused.');
  };

  // Deep Link Scenario Routing
  useEffect(() => {
    const scenarioId = searchParams.get('scenario');
    if (scenarioId) {
      const scenarioPrompts: Record<string, string> = {
        SC01: 'HDFS Write Pipeline (1 GB, 128 MB blocks, RF 3)',
        SC02: 'DataNode Hardware Failure during Write',
        SC03: 'MapReduce WordCount Execution',
        SC04: 'YARN Resource Allocation & Containers',
        SC05: 'Block Corruption & Automatic Recovery',
        SC06: 'Horizontal Cluster Scaling'
      };
      const prompt = scenarioPrompts[scenarioId] || `Execute Scenario ${scenarioId}`;
      startActiveSimulation(prompt);
    }
  }, [searchParams]);

  // Sync state with native browser fullscreenchange event (e.g. ESC key)
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsImmersiveMode(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  const enterImmersiveMode = async () => {
    try {
      if (containerRef.current && containerRef.current.requestFullscreen) {
        await containerRef.current.requestFullscreen();
      } else if (document.documentElement.requestFullscreen) {
        await document.documentElement.requestFullscreen();
      }
    } catch (_) {}
  };

  const exitImmersiveMode = async () => {
    try {
      if (document.fullscreenElement && document.exitFullscreen) {
        await document.exitFullscreen();
      }
    } catch (_) {}
  };

  // Map DataNodes based on assemblyStage (3 + N)
  const renderedDataNodeCount = Math.max(0, Math.min(5, assemblyStage - 3));

  const dataNodesMap = Array.from({ length: renderedDataNodeCount }).reduce<Record<string, any>>((acc, _, i) => {
    const id = `datanode-${i + 1}`;
    acc[id] = {
      id,
      type: 'DATANODE',
      label: `DataNode-${i + 1}`,
      hostname: `dn${i + 1}.hadoop.local`,
      status: i === 2 && status === 'PAUSED' ? 'FAILED' : 'LIVE',
      health: i === 2 && status === 'PAUSED' ? 'FAILED' : 'HEALTHY',
      x: 160 + i * 165,
      y: 340,
      capacity_bytes: 100 * 1024 * 1024 * 1024,
      used_bytes: 20 * 1024 * 1024 * 1024,
      blocks: i < 3 ? ['block-01', 'block-02'] : ['block-03']
    };
    return acc;
  }, {});

  const activeNodes: Record<string, any> = {};
  if (assemblyStage >= 1) {
    activeNodes['client-0'] = {
      id: 'client-0',
      type: 'CLIENT',
      label: 'DFS Client',
      hostname: 'client.hadoop.local',
      status: 'READY',
      health: 'HEALTHY',
      x: 120,
      y: 90,
      capacity_bytes: 0,
      used_bytes: 0,
      blocks: []
    };
  }
  if (assemblyStage >= 2) {
    activeNodes['namenode-1'] = {
      id: 'namenode-1',
      type: 'NAMENODE',
      label: 'Active NameNode',
      hostname: 'nn1.hadoop.local',
      status: 'ACTIVE',
      health: 'HEALTHY',
      x: 500,
      y: 90,
      capacity_bytes: 0,
      used_bytes: 0,
      blocks: []
    };
  }
  if (assemblyStage >= 4) {
    Object.assign(activeNodes, dataNodesMap);
  }

  const mockClusterState: any = {
    cluster_id: 'cls_hadoop_demo',
    nodes: activeNodes,
    blocks: {
      'block-01': {
        block_id: 'block-01',
        file_id: 'file-01',
        index: 0,
        size_bytes: 128 * 1024 * 1024,
        replica_nodes: ['datanode-1', 'datanode-2', 'datanode-3'],
        desired_replication: 3,
        state: 'WRITTEN'
      },
      'block-02': {
        block_id: 'block-02',
        file_id: 'file-01',
        index: 1,
        size_bytes: 128 * 1024 * 1024,
        replica_nodes: ['datanode-1', 'datanode-4', 'datanode-5'],
        desired_replication: 3,
        state: 'WRITTEN'
      }
    },
    transfers: status === 'RUNNING' && assemblyStage >= 3 ? [
      { id: 'tr-1', source_node_id: 'client-0', target_node_id: 'namenode-1', progress: 0.8, type: 'HEARTBEAT', label: 'FSImage Sync' },
      { id: 'tr-2', source_node_id: 'client-0', target_node_id: 'datanode-1', progress: 0.4, type: 'CLIENT_WRITE', label: 'Block Pipeline' }
    ] : [],
    file_count: status !== 'IDLE' ? 1 : 0,
    total_capacity: 500 * 1024 * 1024 * 1024,
    used_capacity: status !== 'IDLE' ? 2 * 128 * 1024 * 1024 * 3 : 0
  };

  const timelineStages = [
    { name: 'INPUT', active: true, done: true },
    { name: 'BLOCK CREATION', active: status === 'RUNNING' || status === 'PAUSED', done: status === 'PAUSED' },
    { name: 'REPLICATION', active: status === 'RUNNING' || status === 'PAUSED', done: false },
    { name: 'MAP', active: false, done: false },
    { name: 'SHUFFLE', active: false, done: false },
    { name: 'REDUCE', active: false, done: false },
    { name: 'OUTPUT', active: false, done: false }
  ];

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: isImmersiveMode ? '100vh' : 'calc(100vh - 60px)',
        backgroundColor: '#070a12',
        position: 'relative',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Quiet Top Sub-Header Bar */}
      <div style={{
        position: 'relative',
        top: '0',
        left: '0',
        right: '0',
        zIndex: 30,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 20px',
        backgroundColor: '#070a12',
        borderBottom: '1px solid #1e2942'
      }}>
        {/* Left Quiet Identity Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          backgroundColor: 'rgba(14, 21, 38, 0.75)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(30, 41, 66, 0.8)',
          padding: '6px 14px',
          borderRadius: '20px',
          fontSize: '12px',
          fontFamily: "'JetBrains Mono', monospace"
        }}>
          <span style={{ color: '#00f0ff', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '6px', fontFamily: "'Space Grotesk', sans-serif" }}>
            <Sparkles size={14} color="#00f0ff" />
            TEDDY CANVAS
          </span>
          <span style={{ color: '#475569' }}>|</span>
          <span style={{ color: '#94a3b8' }}>SYSTEM: <strong style={{ color: '#f8fafc' }}>HDFS</strong></span>
          <span style={{ color: '#475569' }}>|</span>
          <span style={{ color: '#94a3b8' }}>
            STATUS: <strong style={{ color: status === 'RUNNING' ? '#22c55e' : status === 'PAUSED' ? '#ef4444' : '#00f0ff' }}>● {status}</strong>
          </span>
        </div>

        {/* Right Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={() => {
              setExplanationText("Hello boss, TEDDY voice intelligence is online and operational.");
              speakText("Hello boss, TEDDY voice intelligence is online and operational.");
            }}
            title="Test TEDDY Audible Voice Output"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: 'rgba(0, 240, 255, 0.12)',
              color: '#00f0ff',
              border: '1px solid rgba(0, 240, 255, 0.4)',
              backdropFilter: 'blur(12px)',
              padding: '6px 14px',
              borderRadius: '20px',
              fontSize: '12px',
              cursor: 'pointer',
              fontWeight: 700,
              boxShadow: '0 0 12px rgba(0, 240, 255, 0.25)',
              transition: 'all 0.15s ease'
            }}
          >
            <Volume2 size={14} color="#00f0ff" />
            <span>Test Voice (Speak)</span>
          </button>
          {isActiveSimulation && (
            <button
              onClick={handleResetSimulation}
              title="Reset to Idle Canvas"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: 'rgba(14, 21, 38, 0.75)',
                color: '#94a3b8',
                border: '1px solid #1e2942',
                backdropFilter: 'blur(12px)',
                padding: '6px 12px',
                borderRadius: '20px',
                fontSize: '12px',
                cursor: 'pointer',
                fontWeight: 600
              }}
            >
              <RotateCcw size={14} />
              <span>Reset Canvas</span>
            </button>
          )}

          <button
            onClick={() => setShowTimeline(!showTimeline)}
            title="Toggle Stage Timeline"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: showTimeline ? 'rgba(0, 240, 255, 0.15)' : 'rgba(14, 21, 38, 0.75)',
              color: showTimeline ? '#00f0ff' : '#94a3b8',
              border: showTimeline ? '1px solid rgba(0, 240, 255, 0.4)' : '1px solid #1e2942',
              backdropFilter: 'blur(12px)',
              padding: '6px 12px',
              borderRadius: '20px',
              fontSize: '12px',
              cursor: 'pointer',
              fontWeight: 600,
              transition: 'all 0.15s ease'
            }}
          >
            <Clock size={14} />
            <span>Timeline</span>
          </button>

          {!isImmersiveMode ? (
            <button
              onClick={enterImmersiveMode}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                backgroundColor: '#00f0ff',
                color: '#070a12',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: 800,
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(0, 240, 255, 0.4)',
                transition: 'all 0.15s ease'
              }}
            >
              <Maximize2 size={14} />
              <span>Enter Immersive Mode</span>
            </button>
          ) : (
            <button
              onClick={exitImmersiveMode}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: 'rgba(14, 21, 38, 0.85)',
                color: '#00f0ff',
                border: '1px solid rgba(0, 240, 255, 0.4)',
                backdropFilter: 'blur(12px)',
                padding: '6px 14px',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              <Minimize2 size={14} />
              <span>Exit Immersive (ESC)</span>
            </button>
          )}
        </div>
      </div>

      {/* Dock 1: Top Canvas Sticky Status Strip */}
      <TeddyExplanationOverlay
        explanationText={explanationText}
        status={teddyStatus}
        sources={sources}
      />

      {/* CANVAS CONTAINER */}
      <div style={{ flex: 1, width: '100%', height: '100%', position: 'relative' }}>
        {/* Deep Blue Cosmic Nebula & Fluid Flow Canvas */}
        <CosmicNebulaCanvas
          mode={orbMode}
          amplitude={amplitude}
          activeSimulation={isActiveSimulation}
          onClick={toggleVoiceActive}
        />

        {/* STATE 2: ACTIVE SIMULATION MODE (Sequentially Assembled Topology below status strip) */}
        {isActiveSimulation && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            style={{ width: '100%', height: '100%', paddingTop: explanationText ? '12px' : '0px' }}
          >
            <HDFSClusterView
              clusterState={dynamicScene || mockClusterState}
              onSelectTarget={(target) => setSelectedTarget(target)}
              selectedTarget={selectedTarget}
            />
          </motion.div>
        )}
      </div>

      {/* Optional Top-Right HUD Stage Timeline Overlay */}
      {showTimeline && (
        <div
          style={{
            position: 'absolute',
            top: '120px',
            right: '20px',
            zIndex: 35,
            backgroundColor: 'rgba(14, 21, 38, 0.92)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(0, 240, 255, 0.4)',
            borderRadius: '12px',
            padding: '10px 16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            fontSize: '11px',
            fontFamily: "'JetBrains Mono', monospace",
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 15px rgba(0, 240, 255, 0.15)',
            transition: 'all 0.2s ease'
          }}
        >
          <div style={{ color: '#00f0ff', fontWeight: 800, fontSize: '10px', letterSpacing: '0.5px', fontFamily: "'Space Grotesk', sans-serif" }}>
            [ STAGE TIMELINE ]
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            {timelineStages.map((stage, idx) => (
              <React.Fragment key={stage.name}>
                <span style={{
                  color: stage.done ? '#22c55e' : stage.active ? '#00f0ff' : '#475569',
                  fontWeight: stage.active || stage.done ? 700 : 400
                }}>
                  {stage.done ? '✓ ' : ''}{stage.name}
                </span>
                {idx < timelineStages.length - 1 && <span style={{ color: '#1e2942' }}>→</span>}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

      {/* Dock 2: Bottom Fixed Command Bar */}
      <FloatingCommandBar
        onSendCommand={handleSendCommand}
        status={teddyStatus}
        isVoiceMode={isVoiceActive}
        onToggleVoiceMode={toggleVoiceActive}
        onStopAudio={handleStopAudio}
        liveTranscript={transcript}
        chatHistory={chatHistory}
      />
    </div>
  );
};
