/**
 * Python Backend Service - Replaces Gemini with DeathAIAUS Backend
 * Uses pywebview bridge to communicate with Python backend
 */

import { FeasibilityReport, TaskPlan, ProjectPlan } from "../types";
import { FileNode } from "../components/FileTree";

// Bridge interface - will be injected by pywebview
declare global {
    interface Window {
        pywebview?: {
            api: any;
        };
    }
}

// Backend the desktop bridge talks to (webview_bridge.py -> simple_backend.py).
// In a plain browser (e.g. the Vite dev server) we call it directly; it has CORS enabled.
export const BACKEND_URL = (import.meta as any).env?.VITE_BACKEND_URL || 'http://localhost:8888';

export class BackendUnavailableError extends Error {
    constructor() {
        super(`Can't reach the DeathAIAUS backend at ${BACKEND_URL}. Start it with "python simple_backend.py", or launch the desktop app.`);
        this.name = 'BackendUnavailableError';
    }
}

/** Send messages to the AI model via the pywebview bridge, or over HTTP when running in a browser. */
export async function callModel(messages: { role: string; content: string }[], workflow = 'coding'): Promise<string> {
    if (window.pywebview?.api) {
        return window.pywebview.api.call_ai_model(messages, workflow);
    }
    let res: Response;
    try {
        res = await fetch(`${BACKEND_URL}/v1/chat/completions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages, workflow, temperature: 0.7, max_tokens: 2000 }),
            signal: AbortSignal.timeout(120_000),
        });
    } catch (e) {
        if ((e as Error)?.name === 'TimeoutError') throw new Error('The model took longer than 2 minutes to answer. Try a smaller model or a shorter request.');
        throw new BackendUnavailableError();
    }
    if (!res.ok) {
        const detail = await res.text().catch(() => '');
        throw new Error(`Backend returned ${res.status}${detail ? `: ${detail.slice(0, 200)}` : ''}`);
    }
    const data = await res.json();
    return data.choices?.[0]?.message?.content ?? '';
}

// --- Chat Service ---
export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

export interface ChatSession {
    messages: ChatMessage[];
    send: (message: string) => Promise<string>;
}

export function startChat(project: any, aiName?: string, aiPersonality?: string): ChatSession {
    const finalAiName = aiName?.trim() || 'an expert software developer';
    const finalAiPersonality = aiPersonality?.trim() || 'You are a helpful coding assistant.';

    const systemInstruction = `You are ${finalAiName}.
${finalAiPersonality}
- You are working on a project named "${project.name}" which uses the language "${project.language}".
- Pay close attention to the "CURRENT FOCUS" section which provides context about the user's current workflow, task plan, and recent terminal activity.
- The user will provide you with the current project file structure and the content of the active file.
- Use the provided tools to interact with the file system.
- Before making any non-trivial change, outline your strategy.
- When writing a file, always provide the full, complete file content.
- Be concise and helpful in your responses.`;

    const messages: ChatMessage[] = [
        { role: 'system', content: systemInstruction }
    ];

    return {
        messages,
        async send(userMessage: string): Promise<string> {
            messages.push({ role: 'user', content: userMessage });
            
            try {
                const response = await callModel(
                    messages.map(m => ({ role: m.role, content: m.content })),
                    'coding'
                );
                messages.push({ role: 'assistant', content: response });
                return response;
            } catch (error) {
                console.error('AI call failed:', error);
                throw error;
            }
        }
    };
}

export function generateDiff(path: string, originalContent: string, newContent: string): string {
    // Simple diff generation - can be enhanced later
    return `--- a/${path}\n+++ b/${path}\n\nOld content:\n${originalContent}\n\nNew content:\n${newContent}`;
}

export async function lintFile(path: string, content: string, language: string): Promise<string> {
    const prompt = `You are an expert code linter for ${language}.
Analyze this code from "${path}".
Identify syntax errors, style violations, potential bugs.
If perfect, respond with only "OK".
Otherwise, provide a concise list of issues.

\`\`\`${language}
${content}
\`\`\``;

    try {
        const response = await callModel(
            [{ role: 'user', content: prompt }],
            'coding'
        );
        return response;
    } catch (error) {
        console.error('Lint failed:', error);
        return `Error: ${error}`;
    }
}

// --- Knowledge Base Service Functions ---
export async function generateSummaryForCode(content: string, language: string): Promise<string> {
    if (!content.trim()) {
        return "This file is empty.";
    }
    
    const prompt = `Summarize the following ${language} code's primary purpose in one concise sentence.

\`\`\`${language}
${content}
\`\`\``;

    try {
        const response = await callModel(
            [{ role: 'user', content: prompt }],
            'coding'
        );
        return response.trim();
    } catch (error) {
        console.error('Summary generation failed:', error);
        return `Error generating summary: ${error}`;
    }
}

// --- Feasibility Analysis ---
export async function analyzeFeasibility(description: string, language: string): Promise<FeasibilityReport> {
    const prompt = `Analyze the feasibility of this project.
Project: "${description}"
Language: ${language}

Provide a JSON response with:
- feasibility_score (1-10)
- complexity_level (Low/Medium/High/Very High)
- estimated_time (e.g., "2-3 days")
- reality_check (honest assessment)
- red_flags (array of critical issues)
- warnings (array of potential challenges)`;

    try {
        const response = await callModel(
            [{ role: 'user', content: prompt }],
            'planner'
        );
        
        // Try to extract JSON from response
        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            return JSON.parse(jsonMatch[0]) as FeasibilityReport;
        }
        
        // Fallback if AI doesn't return JSON
        return {
            feasibility_score: 5,
            complexity_level: 'Medium',
            estimated_time: 'Unknown',
            reality_check: response,
            red_flags: ['Unable to parse structured response'],
            warnings: ['Manual assessment may be needed']
        };
    } catch (error) {
        console.error('Feasibility analysis failed:', error);
        throw error;
    }
}

// --- Architect Mode ---
export async function generateProjectPlan(description: string, language: string): Promise<ProjectPlan> {
    const prompt = `Act as a senior software architect.
Project: "${description}"
Language: ${language}

Provide a JSON response with:
- thought_process (your reasoning)
- file_structure (array of files/folders)
- dependencies (array of required packages)
- next_steps (brief summary of first dev steps)`;

    try {
        const response = await callModel(
            [{ role: 'user', content: prompt }],
            'planner'
        );
        
        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            return JSON.parse(jsonMatch[0]) as ProjectPlan;
        }
        
        // Fallback
        return {
            thought_process: response,
            file_structure: [],
            dependencies: [],
            next_steps: 'Review generated plan and begin implementation'
        };
    } catch (error) {
        console.error('Project plan generation failed:', error);
        throw error;
    }
}

// --- Project Scaffolding ---
export async function generateInitialProjectStructure(
    description: string,
    language: string,
    plan?: ProjectPlan
): Promise<FileNode[]> {
    
    const planContext = plan ? `
Architect's Plan:
- Thought: ${plan.thought_process}
- Files: ${plan.file_structure.join(', ')}
- Dependencies: ${plan.dependencies.join(', ')}
` : '';

    const prompt = `Generate initial file/folder structure for:
Project: "${description}"
Language: ${language}
${planContext}

Return JSON array of FileNode objects with:
- name (string)
- path (string, full path)
- content (string, for files only)
- children (array, for directories only)

Include README.md, entry point, config files, and logical folders.`;

    try {
        const response = await callModel(
            [{ role: 'user', content: prompt }],
            'planner'
        );
        
        const jsonMatch = response.match(/\[[\s\S]*\]/);
        if (jsonMatch) {
            return JSON.parse(jsonMatch[0]) as FileNode[];
        }
        
        // Fallback minimal structure
        return [
            {
                name: 'README.md',
                path: 'README.md',
                content: `# ${description}\n\nA ${language} project.`,
                isDirectory: false
            }
        ];
    } catch (error) {
        console.error('Structure generation failed:', error);
        throw error;
    }
}

// --- Task Planning ---
export async function generateTaskPlan(description: string): Promise<TaskPlan> {
    const prompt = `Create a detailed task plan for: "${description}"

Return JSON with:
- title (string)
- tasks (array of objects with id, description, dependencies, estimatedTime, status)

All tasks should start with status='pending'.`;

    try {
        const response = await callModel(
            [{ role: 'user', content: prompt }],
            'planner'
        );
        
        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            return JSON.parse(jsonMatch[0]) as TaskPlan;
        }
        
        // Fallback
        return {
            title: description,
            tasks: [
                {
                    id: 1,
                    description: 'Analyze requirements',
                    dependencies: [],
                    estimatedTime: '30 minutes',
                    status: 'pending'
                }
            ]
        };
    } catch (error) {
        console.error('Task plan generation failed:', error);
        throw error;
    }
}

