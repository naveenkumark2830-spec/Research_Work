import React from 'react';
import { VisualBlock, InspectorTarget } from '../types/visualization';

interface FilePanelProps {
  files: Record<string, any>;
  blocks: Record<string, VisualBlock>;
  selectedTarget: InspectorTarget | null;
  onSelectTarget: (target: InspectorTarget) => void;
}

export const FilePanel: React.FC<FilePanelProps> = ({
  files,
  blocks: _blocks,
  selectedTarget,
  onSelectTarget
}) => {
  const fileKeys = Object.keys(files || {});

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 text-xs font-mono">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <span className="text-indigo-400">📁</span> HDFS Namespace Files ({fileKeys.length})
        </h3>
        <span className="text-[10px] text-slate-400">Authoritative File Listing</span>
      </div>

      {fileKeys.length === 0 ? (
        <div className="text-slate-500 py-4 text-center italic">
          No files written to HDFS cluster yet. Trigger an HDFS write simulation.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                <th className="py-2 px-2">Path</th>
                <th className="py-2 px-2">Size</th>
                <th className="py-2 px-2">Block Size</th>
                <th className="py-2 px-2">Blocks</th>
                <th className="py-2 px-2">Replication</th>
                <th className="py-2 px-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {fileKeys.map((fileId) => {
                const f = files[fileId];
                const isSelected =
                  selectedTarget?.type === 'FILE' && selectedTarget?.id === fileId;
                const sizeMb = (f.size_bytes / (1024 * 1024)).toFixed(1);
                const blkMb = (f.block_size_bytes / (1024 * 1024)).toFixed(0);

                return (
                  <tr
                    key={fileId}
                    onClick={() =>
                      onSelectTarget({
                        type: 'FILE',
                        id: fileId,
                        data: f
                      })
                    }
                    className={`cursor-pointer border-b border-slate-800/60 hover:bg-slate-800/50 transition-colors ${
                      isSelected ? 'bg-indigo-950/40 text-indigo-200' : 'text-slate-300'
                    }`}
                  >
                    <td className="py-2 px-2 font-semibold text-indigo-300">{f.path}</td>
                    <td className="py-2 px-2">{sizeMb} MB</td>
                    <td className="py-2 px-2">{blkMb} MB</td>
                    <td className="py-2 px-2">{(f.block_ids || []).length} blocks</td>
                    <td className="py-2 px-2">{f.replication_factor || 3}x</td>
                    <td className="py-2 px-2">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] ${
                          f.status === 'CLOSED'
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            : 'bg-amber-950 text-amber-400 border border-amber-800'
                        }`}
                      >
                        {f.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
