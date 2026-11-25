import React, { useState } from 'react';
import { Project, FeasibilityReport, ToastType } from '../types';
import { analyzeFeasibility } from '../services/pythonBackendService';
import ReaperIcon from './icons/ReaperIcon';

interface FeasibilityAnalyzerProps {
    project: Project;
    report: FeasibilityReport | null;
    setReport: (report: FeasibilityReport | null) => void;
    isLoading: boolean;
    setIsLoading: (loading: boolean) => void;
    addToast: (message: string, type?: ToastType) => void;
    trackPerformance: (model: string, duration: number, error?: string) => void;
}

const FeasibilityAnalyzer: React.FC<FeasibilityAnalyzerProps> = ({ project, report, setReport, isLoading, setIsLoading, addToast, trackPerformance }) => {
    const [description, setDescription] = useState(project.description || '');

    const handleAnalyze = async () => {
        if (!description.trim() || isLoading) return;
        setIsLoading(true);
        setReport(null);
        addToast("Running feasibility check...", "info");
        const startTime = Date.now();
        const modelName = 'gemini-2.5-flash';

        try {
            const newReport = await analyzeFeasibility(description, project.language);
            setReport(newReport);
            addToast(`Feasibility check complete. Score: ${newReport.feasibility_score}/10`, "success");
            trackPerformance(modelName, Date.now() - startTime);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
            console.error(error);
            addToast(`Feasibility Check Error: ${errorMessage}`, "error");
            trackPerformance(modelName, Date.now() - startTime, errorMessage);
        } finally {
            setIsLoading(false);
        }
    };
    
    const getScoreColor = (score: number) => {
        if (score >= 8) return 'text-green-400';
        if (score >= 5) return 'text-yellow-400';
        return 'text-red-500';
    };

    return (
        <div className="px-5 py-4 border-b border-[var(--border-primary)]">
            <div className="flex items-center space-x-2 mb-2">
                <ReaperIcon className="w-4 h-4 text-ochre" />
                <h2 className="dx-label !text-ochre">Feasibility Check</h2>
            </div>
            <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe your project here... Be specific."
                className="dx-input h-16 resize-y !text-xs"
                disabled={isLoading}
                aria-label="Project description for feasibility analysis"
            />
            <button onClick={handleAnalyze} disabled={isLoading || !description.trim()} className="dx-btn w-full mt-2">
                {isLoading ? 'Analyzing...' : 'Analyze Feasibility'}
            </button>
            
            {report && (
                <div className="mt-4 text-sm space-y-2 max-h-48 overflow-y-auto">
                    <div className="flex justify-between items-baseline p-2 bg-[var(--bg-tertiary)] rounded">
                        <span className="font-bold">Feasibility Score:</span>
                        <span className={`text-2xl font-bold ${getScoreColor(report.feasibility_score)}`}>{report.feasibility_score}/10</span>
                    </div>
                     <div className="p-2 bg-[var(--bg-tertiary)] rounded">
                        <span className="font-bold">Complexity:</span> {report.complexity_level}
                    </div>
                    <div className="p-2 bg-[var(--bg-tertiary)] rounded">
                        <span className="font-bold">Est. Time:</span> {report.estimated_time}
                    </div>
                    <div className="p-2 bg-red-900/50 text-red-300 rounded">
                        <p className="font-bold">💀 REALITY CHECK:</p>
                        <p>{report.reality_check}</p>
                    </div>

                    {report.red_flags.length > 0 && (
                        <div className="p-2 bg-red-900/50 text-red-300 rounded">
                            <p className="font-bold">Red Flags:</p>
                            <ul className="list-disc list-inside">
                                {report.red_flags.map((flag, i) => <li key={i}>{flag}</li>)}
                            </ul>
                        </div>
                    )}

                    {report.warnings.length > 0 && (
                        <div className="p-2 bg-[var(--accent-warning)] text-[var(--accent-warning-text)] rounded">
                            <p className="font-bold">Warnings:</p>
                             <ul className="list-disc list-inside">
                                {report.warnings.map((warn, i) => <li key={i}>{warn}</li>)}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default FeasibilityAnalyzer;