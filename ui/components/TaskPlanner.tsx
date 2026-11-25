// Fix: Implemented the TaskPlanner component.
import React, { useState } from 'react';
import { Project, Task, TaskPlan, ToastType } from '../types';
import { generateTaskPlan } from '../services/pythonBackendService';
import XIcon from './icons/XIcon';
import SitemapIcon from './icons/SitemapIcon';
import ViewListIcon from './icons/ViewListIcon';
import TaskGraph from './TaskGraph';

interface TaskPlannerProps {
  onClose: () => void;
  project: Project;
  addToast: (message: string, type?: ToastType) => void;
  sendMessageToChat: (message: string) => Promise<void>;
  taskPlan: TaskPlan | null;
  setTaskPlan: (plan: TaskPlan | null) => void;
}

const TaskPlanner: React.FC<TaskPlannerProps> = ({ onClose, project, addToast, sendMessageToChat, taskPlan, setTaskPlan }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [description, setDescription] = useState('');
    const [viewMode, setViewMode] = useState<'list' | 'graph'>('list');

    const handleGeneratePlan = async () => {
        if (!description.trim()) {
            addToast("Please provide a description for the task plan.", "error");
            return;
        }
        setIsLoading(true);
        addToast("Generating task plan...", "info");
        try {
            const newPlan = await generateTaskPlan(description);
            setTaskPlan(newPlan);
            addToast("Task plan generated successfully.", "success");
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
            addToast(`Error generating plan: ${errorMessage}`, "error");
        } finally {
            setIsLoading(false);
        }
    };

    const handleTaskStatusChange = (taskId: number, status: Task['status']) => {
        if (!taskPlan) return;
        const newTasks = taskPlan.tasks.map(t => t.id === taskId ? { ...t, status } : t);
        setTaskPlan({ ...taskPlan, tasks: newTasks });
    };

    return (
        <div className="dx-backdrop">
            <div className="dx-dialog w-full max-w-5xl h-[90vh]  flex flex-col p-4 text-[var(--text-primary)]">
                <header className="flex items-center justify-between pb-4 border-b border-[var(--border-primary)]">
                    <h2 className="font-display text-xl font-bold uppercase tracking-wide text-blood-light">📋 Task Planner</h2>
                    <button onClick={onClose} className="text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
                        <XIcon className="w-8 h-8" />
                    </button>
                </header>
                
                <div className="flex-grow flex mt-4 overflow-hidden space-x-4">
                    <div className="w-1/3 flex flex-col space-y-4">
                        <div className="flex-shrink-0">
                            <h3 className="text-lg font-bold mb-2">Generate a New Plan</h3>
                            <textarea
                                value={description}
                                onChange={e => setDescription(e.target.value)}
                                placeholder="Describe the feature or task you want to plan..."
                                className="dx-input h-32 resize-y"
                                disabled={isLoading}
                            />
                            <button
                                onClick={handleGeneratePlan}
                                disabled={isLoading || !description.trim()}
                                className="dx-btn dx-btn-primary w-full mt-2"
                            >
                                {isLoading ? 'Generating...' : 'Generate Plan'}
                            </button>
                        </div>
                        <div className="flex-grow bg-[var(--bg-primary)] p-2 rounded overflow-y-auto">
                           <h3 className="text-lg font-bold mb-2">Current Plan</h3>
                           {taskPlan ? (
                                <div>
                                    <h4 className="font-bold text-[var(--text-primary)]">{taskPlan.title}</h4>
                                    <p className="text-xs text-[var(--text-secondary)]">{taskPlan.tasks.length} tasks</p>
                                </div>
                           ) : (
                               <p className="text-sm text-[var(--text-muted)]">No plan has been generated yet.</p>
                           )}
                        </div>
                    </div>

                    <div className="w-2/3 flex flex-col">
                        <div className="flex items-center justify-between mb-2">
                             <h3 className="text-lg font-bold">Plan Details</h3>
                             <div className="flex items-center space-x-2 p-1 bg-[var(--bg-primary)] rounded-md">
                                <button onClick={() => setViewMode('list')} className={`px-2 py-1 rounded ${viewMode === 'list' ? 'bg-indigo-600' : ''}`}><ViewListIcon className="w-5 h-5"/></button>
                                <button onClick={() => setViewMode('graph')} className={`px-2 py-1 rounded ${viewMode === 'graph' ? 'bg-indigo-600' : ''}`}><SitemapIcon className="w-5 h-5"/></button>
                             </div>
                        </div>
                        <div className="flex-grow bg-[var(--bg-primary)] p-2 rounded overflow-y-auto">
                            {!taskPlan && <div className="text-center text-[var(--text-muted)] pt-10">Generate a plan to see the details.</div>}
                            {taskPlan && viewMode === 'list' && (
                                <ul className="space-y-2">
                                    {taskPlan.tasks.map(task => (
                                        <li key={task.id} className="p-2 bg-[var(--bg-tertiary)] rounded flex justify-between items-center">
                                            <div>
                                                <p className="font-semibold">{task.id}. {task.description}</p>
                                                <p className="text-xs text-[var(--text-secondary)]">
                                                    Dependencies: {task.dependencies.join(', ') || 'None'} | Est. Time: {task.estimatedTime}
                                                </p>
                                            </div>
                                            <select 
                                                value={task.status} 
                                                onChange={e => handleTaskStatusChange(task.id, e.target.value as Task['status'])}
                                                className="bg-[var(--bg-primary)] border border-[var(--border-primary)] rounded p-1 text-xs"
                                            >
                                                <option value="pending">Pending</option>
                                                <option value="in-progress">In Progress</option>
                                                <option value="completed">Completed</option>
                                                <option value="skipped">Skipped</option>
                                                <option value="failed">Failed</option>
                                            </select>
                                        </li>
                                    ))}
                                </ul>
                            )}
                             {taskPlan && viewMode === 'graph' && (
                                <TaskGraph tasks={taskPlan.tasks} />
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TaskPlanner;