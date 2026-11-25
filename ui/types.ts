
export interface FileNode {
  name: string;
  path: string;
  content?: string;
  children?: FileNode[];
}

export interface Project {
    name: string;
    language: string;
    description: string;
    plan: ProjectPlan;
}

export interface ProjectPlan {
    thought_process: string;
    file_structure: string[];
    dependencies: string[];
    next_steps: string;
}

export interface FeasibilityReport {
    feasibility_score: number;
    complexity_level: string;
    estimated_time: string;
    reality_check: string;
    red_flags: string[];
    warnings: string[];
}

export interface Task {
    id: number;
    description: string;
    dependencies: number[];
    estimatedTime: string;
    status: 'pending' | 'in-progress' | 'completed' | 'skipped' | 'failed';
}

export interface TaskPlan {
    title: string;
    tasks: Task[];
}

export interface WorkflowStep {
    id: string;
    name: string;
}

export interface Workflow {
    id: string;
    name: string;
    steps: WorkflowStep[];
}

export interface WorkflowSettings {
    [stepId: string]: string;
}

export interface ProposedPlan {
    goal: string;
    steps: string[];
    reasoning: string;
}

export interface ChatMessage {
    id: string;
    role: 'user' | 'model' | 'system';
    text: string;
    proposedPlan?: ProposedPlan;
}

export type ToastType = 'success' | 'error' | 'info';

export interface ToastData {
    id: number;
    message: string;
    type: ToastType;
}

export interface ProposedChange {
    path: string;
    newContent?: string;
    diff?: string;
    type: 'create' | 'modify' | 'delete' | 'create_folder';
}

export interface ContextMenuData {
    x: number;
    y: number;
    targetPath: string;
}

export interface CreationInputData {
    type: 'file' | 'folder';
    parentPath: string;
}

export interface ModelPerformanceDataEntry {
    successes: number;
    failures: number;
    totalTime: number;
    errorLogs: { timestamp: number; message: string }[];
}

export interface ModelPerformanceData {
    [model: string]: ModelPerformanceDataEntry;
}

export interface KnowledgeBaseEntry {
    summary: string;
    content: string;
}

export type KnowledgeBaseData = Map<string, KnowledgeBaseEntry>;
