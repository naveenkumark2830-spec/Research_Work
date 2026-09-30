import React, { useState, useEffect } from 'react';
import { SessionState } from '../types/session';
import { hdfsApi, HDFSClusterConfigPayload } from '../api/hdfsApi';
import { sessionApi } from '../api/sessionClient';
import { InspectorTarget } from '../visualization/types/visualization';

interface InteractiveControlPanelProps {
  state: SessionState;
  selectedTarget: InspectorTarget | null;
  onStateUpdated: (newState: SessionState) => void;
  onError: (err: string) => void;
}

export const InteractiveControlPanel: React.FC<InteractiveControlPanelProps> = ({
  state,
  selectedTarget,
  onStateUpdated,
  onError
}) => {
  const { session, simulation, user } = state;
  const cfg = simulation.configuration;

  const [fileSizeMb, setFileSizeMb] = useState<number>(cfg.file_size_mb || 500);
  const [blockSizeMb, setBlockSizeMb] = useState<number>(cfg.block_size_mb || 128);
  const [replicationFactor, setReplicationFactor] = useState<number>(cfg.replication_factor || 3);
  const [datanodeCount, setDatanodeCount] = useState<number>(cfg.datanode_count || cfg.data_node_count || 5);
  const [reducerCount, setReducerCount] = useState<number>(cfg.reducer_count || 5);
  const [speed, setSpeed] = useState<number>(cfg.simulation_speed || 1.0);
  const [isApplying, setIsApplying] = useState(false);

  useEffect(() => {
    setFileSizeMb(cfg.file_size_mb || 500);
    setBlockSizeMb(cfg.block_size_mb || 128);
    setReplicationFactor(cfg.replication_factor || 3);
    setDatanodeCount(cfg.datanode_count || cfg.data_node_count || 5);
    setReducerCount(cfg.reducer_count || 5);
    setSpeed(cfg.simulation_speed || 1.0);
  }, [cfg]);

  const selectedDataNode = selectedTarget?.type === 'DATANODE' ? selectedTarget.id : null;
  const selectedNodeData = selectedTarget?.type === 'DATANODE' ? selectedTarget.data : null;
  const isFailedNode = selectedNodeData?.health === 'FAILED' || selectedNodeData?.status === 'FAILED';

  const handleApplyConfig = async () => {
    if (simulation.status === 'RUNNING') {
      onError('Configuration can only be changed while simulation is idle.');
      return;
    }
    if (replicationFactor > datanodeCount) {
      onError(`Replication factor ${replicationFactor} cannot exceed ${datanodeCount} available DataNodes.`);
      return;
    }

    setIsApplying(true);
    try {
      const payload: HDFSClusterConfigPayload = {
        file_size_mb: Number(fileSizeMb),
        block_size_mb: Number(blockSizeMb),
        replication_factor: Number(replicationFactor),
        data_node_count: Number(datanodeCount),
        reducer_count: Number(reducerCount),
        simulation_speed: Number(speed)
      };
      const newState = await hdfsApi.updateConfig(session.session_id, user.user_id, payload);
      onStateUpdated(newState);
    } catch (err: any) {
      onError(err.message || 'Failed to apply configuration');
    } finally {
      setIsApplying(false);
    }
  };

  const handleSpeedChange = async (newSpeed: number) => {
    setSpeed(newSpeed);
    try {
      const newState = await hdfsApi.setSpeed(session.session_id, user.user_id, newSpeed);
      onStateUpdated(newState);
    } catch (err: any) {
      onError(err.message || 'Failed to update simulation speed');
    }
  };

  const handleAddDataNode = async () => {
    try {
      const newState = await hdfsApi.addDatanode(session.session_id, user.user_id);
      onStateUpdated(newState);
    } catch (err: any) {
      onError(err.message || 'Failed to add DataNode');
    }
  };

  const handleKillDataNode = async (nodeId: string) => {
    try {
      const newState = await hdfsApi.killDatanode(session.session_id, user.user_id, nodeId);
      onStateUpdated(newState);
    } catch (err: any) {
      onError(err.message || `Failed to kill ${nodeId}`);
    }
  };

  const handleRecoverDataNode = async (nodeId: string) => {
    try {
      const newState = await hdfsApi.recoverDatanode(session.session_id, user.user_id, nodeId);
      onStateUpdated(newState);
    } catch (err: any) {
      onError(err.message || `Failed to recover ${nodeId}`);
    }
  };

  const handleStartSimulation = async () => {
    try {
      const newState = await hdfsApi.writeFile(session.session_id, user.user_id, 'input/data.csv', fileSizeMb);
      onStateUpdated(newState);
    } catch (err: any) {
      onError(err.message || 'Failed to start simulation write');
    }
  };

  const handlePause = async () => {
    try {
      const newState = await sessionApi.pauseSimulation(session.session_id, user.user_id);
      onStateUpdated(newState);
    } catch (err: any) {
      onError(err.message || 'Failed to pause simulation');
    }
  };

  const handleResume = async () => {
    try {
      const newState = await sessionApi.resumeSimulation(session.session_id, user.user_id);
      onStateUpdated(newState);
    } catch (err: any) {
      onError(err.message || 'Failed to resume simulation');
    }
  };

  const handleRestart = async () => {
    try {
      const newState = await hdfsApi.restartSimulation(session.session_id, user.user_id);
      onStateUpdated(newState);
    } catch (err: any) {
      onError(err.message || 'Failed to restart simulation');
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 font-mono text-xs shadow-xl text-left">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <span className="text-indigo-400">⚙️</span> HDFS SIMULATION CONTROLS (Level 6)
        </h3>
        <span className="text-[10px] text-slate-400">Authoritative Backend Execution</span>
      </div>

      {/* Configuration Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4 bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
        <div>
          <label className="text-slate-400 block mb-1 text-[11px]">Input File Size (MB):</label>
          <input
            type="number"
            min={1}
            max={10240}
            value={fileSizeMb}
            disabled={simulation.status === 'RUNNING'}
            onChange={(e) => setFileSizeMb(Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200 focus:border-indigo-500 font-bold"
          />
        </div>

        <div>
          <label className="text-slate-400 block mb-1 text-[11px]">Block Size (MB):</label>
          <input
            type="number"
            min={1}
            max={1024}
            value={blockSizeMb}
            disabled={simulation.status === 'RUNNING'}
            onChange={(e) => setBlockSizeMb(Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200 focus:border-indigo-500 font-bold"
          />
        </div>

        <div>
          <label className="text-slate-400 block mb-1 text-[11px]">Replication Factor:</label>
          <input
            type="number"
            min={1}
            max={10}
            value={replicationFactor}
            disabled={simulation.status === 'RUNNING'}
            onChange={(e) => setReplicationFactor(Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200 focus:border-indigo-500 font-bold"
          />
        </div>

        <div>
          <label className="text-slate-400 block mb-1 text-[11px]">DataNodes Count:</label>
          <input
            type="number"
            min={1}
            max={50}
            value={datanodeCount}
            disabled={simulation.status === 'RUNNING'}
            onChange={(e) => setDatanodeCount(Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200 focus:border-indigo-500 font-bold"
          />
        </div>

        <div>
          <label className="text-slate-400 block mb-1 text-[11px]">Reducers Count:</label>
          <input
            type="number"
            min={1}
            max={100}
            value={reducerCount}
            onChange={(e) => setReducerCount(Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200 focus:border-indigo-500 font-bold"
          />
        </div>

        <div>
          <label className="text-slate-400 block mb-1 text-[11px]">Simulation Speed:</label>
          <div className="flex gap-1">
            {[0.25, 0.5, 1, 2, 4].map((spd) => (
              <button
                key={spd}
                onClick={() => handleSpeedChange(spd)}
                className={`px-1.5 py-1 rounded text-[10px] font-bold border transition-colors ${
                  speed === spd
                    ? 'bg-indigo-600 text-white border-indigo-500'
                    : 'bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700'
                }`}
              >
                {spd}x
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Apply Config Button */}
      <button
        onClick={handleApplyConfig}
        disabled={isApplying || simulation.status === 'RUNNING'}
        className={`w-full py-1.5 mb-4 rounded font-bold transition-all text-xs border ${
          simulation.status === 'RUNNING'
            ? 'bg-slate-800 text-slate-500 border-slate-700 cursor-not-allowed'
            : 'bg-indigo-600 hover:bg-indigo-500 text-white border-indigo-500 shadow-md'
        }`}
      >
        {isApplying ? 'Applying Configuration...' : '[ APPLY CONFIGURATION ]'}
      </button>

      {/* Cluster Actions Section */}
      <div className="border-t border-slate-800 pt-3 mb-4">
        <h4 className="text-slate-300 font-bold mb-2 text-xs">CLUSTER ACTIONS</h4>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleAddDataNode}
            className="px-3 py-1 bg-emerald-700 hover:bg-emerald-600 text-white rounded font-semibold text-xs border border-emerald-600"
          >
            + Add DataNode
          </button>

          <span className="text-slate-500 text-xs">|</span>

          <span className="text-slate-400">
            Selected Node: {' '}
            <span className="text-indigo-300 font-bold">
              {selectedDataNode || 'None (Click canvas DataNode)'}
            </span>
          </span>

          {selectedDataNode && (
            <div className="flex gap-2">
              {!isFailedNode && (
                <button
                  onClick={() => handleKillDataNode(selectedDataNode)}
                  className="px-2.5 py-1 bg-rose-700 hover:bg-rose-600 text-white rounded font-bold text-xs border border-rose-600"
                >
                  Kill DataNode
                </button>
              )}
              {isFailedNode && (
                <button
                  onClick={() => handleRecoverDataNode(selectedDataNode)}
                  className="px-2.5 py-1 bg-sky-700 hover:bg-sky-600 text-white rounded font-bold text-xs border border-sky-600"
                >
                  Recover DataNode
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Simulation Control Buttons */}
      <div className="border-t border-slate-800 pt-3">
        <h4 className="text-slate-300 font-bold mb-2 text-xs">SIMULATION LIFECYCLE</h4>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleStartSimulation}
            disabled={simulation.status === 'RUNNING'}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-bold text-xs border border-emerald-500 disabled:opacity-50"
          >
            ▶ Start HDFS Write
          </button>
          <button
            onClick={handlePause}
            disabled={simulation.status !== 'RUNNING'}
            className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded font-bold text-xs border border-amber-500 disabled:opacity-50"
          >
            ⏸ Pause
          </button>
          <button
            onClick={handleResume}
            disabled={simulation.status !== 'PAUSED'}
            className="px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded font-bold text-xs border border-sky-500 disabled:opacity-50"
          >
            ▶ Resume
          </button>
          <button
            onClick={handleRestart}
            className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white rounded font-bold text-xs border border-slate-600"
          >
            ↻ Restart
          </button>
        </div>
      </div>
    </div>
  );
};
