// Fix: Implemented the TaskGraph component.
import React from 'react';
import { Task } from '../types';

interface TaskGraphProps {
  tasks: Task[];
}

const TaskGraph: React.FC<TaskGraphProps> = ({ tasks }) => {
  if (!tasks || tasks.length === 0) {
    return <div className="text-center text-[var(--text-muted)]">No tasks to display in graph.</div>;
  }

  // A very simple layout algorithm
  const levels: Task[][] = [];
  const taskMap = new Map(tasks.map(t => [t.id, { ...t, level: -1 }]));

  let changed = true;
  let iterations = 0;
  const maxIterations = tasks.length + 1; // Prevent infinite loops
  while (changed && iterations < maxIterations) {
    changed = false;
    taskMap.forEach(task => {
      if (task.level !== -1) return;

      if (task.dependencies.length === 0) {
        task.level = 0;
        changed = true;
      } else {
        const deps = task.dependencies.map(depId => taskMap.get(depId));
        if (deps.every(dep => dep && dep.level !== -1)) {
          task.level = Math.max(...deps.map(dep => dep!.level)) + 1;
          changed = true;
        }
      }
    });
    iterations++;
  }

  taskMap.forEach(task => {
      if (task.level === -1) task.level = 99; // Handle circular or missing dependencies
      if (!levels[task.level]) levels[task.level] = [];
      levels[task.level].push(task);
  });
  
  const getStatusColor = (status: Task['status']) => {
      switch(status) {
          case 'completed': return 'border-green-500 bg-green-900/50';
          case 'in-progress': return 'border-blue-500 bg-blue-900/50';
          case 'failed': return 'border-red-500 bg-red-900/50';
          case 'skipped': return 'border-gray-500 bg-gray-700/50';
          case 'pending':
          default:
            return 'border-[var(--border-primary)] bg-[var(--bg-tertiary)]';
      }
  }


  return (
    <div className="p-4 flex space-x-4 overflow-x-auto">
      {levels.map((levelTasks, levelIndex) => (
        <div key={levelIndex} className="flex flex-col items-center space-y-4 flex-shrink-0">
          <h4 className="font-bold text-sm text-[var(--text-secondary)]">Step {levelIndex + 1}</h4>
          {levelTasks.map(task => (
            <div
              key={task.id}
              className={`p-3 rounded-md border-2 w-48 ${getStatusColor(task.status)}`}
              title={`Dependencies: ${task.dependencies.join(', ') || 'None'}`}
            >
              <p className="font-bold text-sm truncate text-[var(--text-primary)]">{task.description}</p>
              <p className="text-xs text-[var(--text-secondary)]">ID: {task.id}</p>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default TaskGraph;