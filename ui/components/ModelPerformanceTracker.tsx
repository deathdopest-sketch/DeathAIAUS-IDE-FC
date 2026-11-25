
import React, { useState } from 'react';
// Fix: Import ModelPerformanceDataEntry for type casting.
import { ModelPerformanceData, ModelPerformanceDataEntry } from '../types';
import XIcon from './icons/XIcon';

interface ModelPerformanceTrackerProps {
  stats: ModelPerformanceData;
  onClose: () => void;
  onClear: () => void;
}

const ModelPerformanceTracker: React.FC<ModelPerformanceTrackerProps> = ({ stats, onClose, onClear }) => {
    const [selectedModel, setSelectedModel] = useState<string | null>(null);

    // Fix: Cast the result of Object.entries to ensure correct types for sorting and mapping.
    const sortedModels = (Object.entries(stats) as [string, ModelPerformanceDataEntry][]).sort(([, a], [, b]) => {
        const aSuccessRate = a.successes / (a.successes + a.failures) || 0;
        const bSuccessRate = b.successes / (b.successes + b.failures) || 0;
        return bSuccessRate - aSuccessRate;
    });

    const getSuccessRateColor = (rate: number) => {
        if (rate >= 0.9) return 'text-green-400';
        if (rate >= 0.7) return 'text-yellow-400';
        return 'text-red-500';
    };

    const selectedModelErrors = selectedModel ? stats[selectedModel]?.errorLogs : null;

    return (
    <div className="dx-backdrop">
      <div className="dx-dialog w-full max-w-4xl h-[80vh]  flex flex-col p-4 text-[var(--text-primary)]">
        <header className="flex items-center justify-between pb-4 border-b border-[var(--border-primary)]">
          <h2 className="font-display text-xl font-bold uppercase tracking-wide text-blood-light">📊 Model Performance Stats</h2>
          <button onClick={onClose} className="text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
            <XIcon className="w-8 h-8" />
          </button>
        </header>

        <div className="flex-grow flex mt-4 overflow-hidden">
            <div className="w-1/2 pr-2 overflow-y-auto">
                 <div className="flex justify-end mb-2">
                    <button onClick={onClear} className="px-3 py-1 text-xs bg-red-800 hover:bg-red-700 rounded text-white">Clear Stats</button>
                </div>
                <div className="space-y-2">
                    {sortedModels.map(([model, data]) => {
                        const total = data.successes + data.failures;
                        const successRate = total > 0 ? data.successes / total : 0;
                        const avgTime = data.successes > 0 ? (data.totalTime / data.successes / 1000).toFixed(2) : 'N/A';
                        return (
                            <div key={model} onClick={() => setSelectedModel(model)} className={`p-3 bg-[var(--bg-tertiary)] rounded-lg border-2 ${selectedModel === model ? 'border-purple-500' : 'border-transparent'} cursor-pointer hover:bg-[var(--bg-hover)]`}>
                                <div className="flex justify-between items-center">
                                    <h3 className="font-bold text-lg">{model}</h3>
                                    <div className={`font-bold text-xl ${getSuccessRateColor(successRate)}`}>
                                        {(successRate * 100).toFixed(1)}%
                                    </div>
                                </div>
                                <div className="text-xs text-[var(--text-secondary)] mt-1 flex justify-between">
                                    <span>Success: {data.successes} / Fails: {data.failures}</span>
                                    <span>Avg Time: {avgTime}s</span>
                                </div>
                            </div>
                        );
                    })}
                     {sortedModels.length === 0 && <p className="text-center text-[var(--text-muted)]">No performance data yet. Use an AI feature to start tracking.</p>}
                </div>
            </div>
            <div className="w-1/2 pl-2 border-l border-[var(--border-primary)] flex flex-col">
                <h3 className="text-lg font-bold text-center mb-2">Error Logs for {selectedModel || "..."}</h3>
                <div className="flex-grow bg-[var(--bg-primary)] rounded p-2 overflow-y-auto font-mono text-xs">
                   {selectedModelErrors && selectedModelErrors.length > 0 ? (
                        selectedModelErrors.map((log, index) => (
                           <div key={index} className="border-b border-[var(--border-secondary)] py-1">
                               <p className="text-[var(--text-muted)]">{new Date(log.timestamp).toLocaleString()}</p>
                               <p className="text-red-400 whitespace-pre-wrap">{log.message}</p>
                           </div>
                        ))
                   ) : (
                       <p className="text-[var(--text-muted)] text-center mt-4">
                           {selectedModel ? 'No errors logged for this model.' : 'Select a model to view its error logs.'}
                        </p>
                   )}
                </div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default ModelPerformanceTracker;
