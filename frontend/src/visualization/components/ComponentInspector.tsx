import React from 'react';
import { InspectorTarget } from '../types/visualization';

interface ComponentInspectorProps {
  target: InspectorTarget | null;
  onClose: () => void;
  onKillDataNode?: (nodeId: string) => void;
  onRecoverDataNode?: (nodeId: string) => void;
}

export const ComponentInspector: React.FC<ComponentInspectorProps> = ({
  target,
  onClose,
  onKillDataNode,
  onRecoverDataNode
}) => {
  if (!target) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 text-xs font-mono text-slate-500 h-full flex flex-col justify-center items-center text-center">
        <span className="text-2xl mb-2 opacity-40">🔍</span>
        <p className="font-semibold text-slate-400">Component Inspector</p>
        <p className="text-[11px] mt-1 max-w-[200px]">
          Click on NameNode, DataNode, File, or Block to inspect detailed simulation metadata.
        </p>
      </div>
    );
  }

  const { type, id, data } = target;

  const isFailedNode = data.health === 'FAILED' || data.status === 'FAILED';

  return (
    <div className="bg-slate-900 border border-indigo-900/60 rounded-lg p-4 text-xs font-mono shadow-xl relative animate-fadeIn text-left">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-950 text-indigo-300 border border-indigo-800">
            {type}
          </span>
          <span className="font-bold text-slate-200 truncate max-w-[180px]">{id}</span>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-200 text-sm px-1 font-bold"
          title="Close Inspector"
        >
          ✕
        </button>
      </div>

      {/* NAMENODE Details */}
      {type === 'NAMENODE' && (
        <div className="space-y-2">
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Status:</span>
            <span className="text-emerald-400 font-bold">{data.status || 'ACTIVE'}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Node ID:</span>
            <span className="text-slate-200">{data.id}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Hostname:</span>
            <span className="text-slate-200">{data.hostname}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">EditLog State:</span>
            <span className="text-indigo-400">OPEN / SYNCHRONIZED</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">FSImage Status:</span>
            <span className="text-emerald-400">PERSISTED</span>
          </div>
        </div>
      )}

      {/* DATANODE Details */}
      {type === 'DATANODE' && (
        <div className="space-y-2">
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Status:</span>
            <span
              className={`font-bold ${
                isFailedNode ? 'text-rose-400' : 'text-emerald-400'
              }`}
            >
              {data.status} ({data.health})
            </span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Hostname:</span>
            <span className="text-slate-200">{data.hostname}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Rack Path:</span>
            <span className="text-slate-300">{data.rack_id || '/default-rack'}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Storage Used:</span>
            <span className="text-slate-200">
              {(data.used_bytes / (1024 * 1024 * 1024)).toFixed(2)} GB /{' '}
              {(data.capacity_bytes / (1024 * 1024 * 1024)).toFixed(0)} GB
            </span>
          </div>
          <div className="pt-2">
            <span className="text-slate-400 block mb-1">Stored Replicas ({data.blocks?.length || 0}):</span>
            <div className="flex flex-wrap gap-1 max-h-24 overflow-y-auto mb-3">
              {(data.blocks || []).map((bId: string) => (
                <span
                  key={bId}
                  className="px-1.5 py-0.5 bg-indigo-950 border border-indigo-800 text-indigo-300 text-[10px] rounded"
                >
                  {bId.slice(0, 10)}
                </span>
              ))}
            </div>
          </div>

          {/* Contextual Action Buttons */}
          <div className="pt-2 border-t border-slate-800 flex gap-2">
            {!isFailedNode && onKillDataNode && (
              <button
                onClick={() => onKillDataNode(id)}
                className="w-full py-1 bg-rose-700 hover:bg-rose-600 text-white rounded font-bold text-xs border border-rose-600 shadow-sm"
              >
                Kill DataNode
              </button>
            )}
            {isFailedNode && onRecoverDataNode && (
              <button
                onClick={() => onRecoverDataNode(id)}
                className="w-full py-1 bg-sky-700 hover:bg-sky-600 text-white rounded font-bold text-xs border border-sky-600 shadow-sm"
              >
                Recover DataNode
              </button>
            )}
          </div>
        </div>
      )}

      {/* FILE Details */}
      {type === 'FILE' && (
        <div className="space-y-2">
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">HDFS Path:</span>
            <span className="text-indigo-300 font-bold">{data.path}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">File Size:</span>
            <span className="text-slate-200">
              {(data.size_bytes / (1024 * 1024)).toFixed(1)} MB
            </span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Block Size:</span>
            <span className="text-slate-200">
              {(data.block_size_bytes / (1024 * 1024)).toFixed(0)} MB
            </span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Replication Factor:</span>
            <span className="text-slate-200">{data.replication_factor}x</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Status:</span>
            <span className="text-emerald-400">{data.status}</span>
          </div>
        </div>
      )}

      {/* BLOCK Details */}
      {type === 'BLOCK' && (
        <div className="space-y-2">
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Block ID:</span>
            <span className="text-indigo-300 font-bold">{data.block_id}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">File ID:</span>
            <span className="text-slate-200">{data.file_id}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">State:</span>
            <span className="text-emerald-400 font-bold">{data.state}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/60 py-1">
            <span className="text-slate-400">Replicas:</span>
            <span className="text-slate-200">
              {data.replica_nodes?.length || 0} / {data.desired_replication || 3}
            </span>
          </div>
          <div className="pt-2">
            <span className="text-slate-400 block mb-1">Replica Locations:</span>
            <div className="space-y-1">
              {(data.replica_nodes || []).map((dnId: string) => (
                <div
                  key={dnId}
                  className="flex items-center gap-1.5 text-[10px] text-slate-300 bg-slate-800/60 px-2 py-1 rounded"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  <span>DataNode: {dnId}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
