import React, { useState, useRef, useEffect } from 'react';
import { Project, FeasibilityReport, ChatMessage, WorkflowSettings, ProposedChange, ToastType, ProposedPlan, TaskPlan } from '../types';
import FeasibilityAnalyzer from './FeasibilityAnalyzer';
import { WORKFLOWS } from '../constants';
import { startChat, generateDiff, lintFile } from '../services/pythonBackendService';
import { KnowledgeBaseService } from '../services/knowledgeBaseService';
import { FileNode } from './FileTree';
import CheckIcon from './icons/CheckIcon';
import { CorruptText } from './ui/haunt';
import XIcon from './icons/XIcon';

interface AiChatProps {
    project: Project;
    report: FeasibilityReport | null;
    setReport: (report: FeasibilityReport | null) => void;
    isLoading: boolean;
    setIsLoading: (loading: boolean) => void;
    addToast: (message: string, type?: ToastType) => void;
    trackPerformance: (model: string, duration: number, error?: string) => void;
    chat: any; // Gemini Chat Session
    setChat: (chat: any) => void;
    messages: ChatMessage[];
    setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
    isAiLoading: boolean;
    setIsAiLoading: (loading: boolean) => void;
    activeModel: string; // Note: model is now set on chat creation
    workflowSettings: WorkflowSettings;
    files: FileNode[];
    openFiles: Map<string, string>;
    activeFile: string | null;
    onPreviewRequest: (change: ProposedChange) => void;
    findNodeByPath: (nodes: FileNode[], path: string) => FileNode | null;
    knowledgeBaseService: KnowledgeBaseService;
    terminalHistory: string[];
    taskPlan: TaskPlan | null;
    aiName: string;
    aiPersonality: string;
}

const buildFileTreeString = (nodes: FileNode[], indent = ''): string => {
    let treeString = '';
    nodes.forEach(node => {
        treeString += `${indent}${node.name}${node.children ? '/' : ''}\n`;
        if (node.children) {
            treeString += buildFileTreeString(node.children, indent + '  ');
        }
    });
    return treeString;
};


const AiChat: React.FC<AiChatProps> = (props) => {
    const { 
        project, report, setReport, isLoading, setIsLoading, addToast, trackPerformance,
        chat, setChat, messages, setMessages, isAiLoading, setIsAiLoading,
        files, openFiles, activeFile, onPreviewRequest, findNodeByPath,
        knowledgeBaseService, terminalHistory, taskPlan, aiName, aiPersonality
    } = props;
    
    const [input, setInput] = useState('');
    const [selectedWorkflow, setSelectedWorkflow] = useState(WORKFLOWS[0].id);
    const [selectedStep, setSelectedStep] = useState(WORKFLOWS[0].steps[0].id);

    const chatEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (project) {
            setChat(startChat(project, aiName, aiPersonality));
        }
    }, [project, aiName, aiPersonality, setChat]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);
    
    useEffect(() => {
        const workflow = WORKFLOWS.find(w => w.id === selectedWorkflow);
        if (workflow) {
            setSelectedStep(workflow.steps[0].id);
        }
    }, [selectedWorkflow]);

    const continueChat = async (parts: any[]) => {
        setIsAiLoading(true);
        try {
            let response = await chat.sendMessage({ parts });
            
            while (response.functionCalls && response.functionCalls.length > 0) {
                 const toolResponseParts = await processToolCalls(response.functionCalls);
                 if (toolResponseParts.length === 0) break; // Awaiting user action
                 response = await chat.sendMessage({ parts: toolResponseParts });
            }

            if (response.text) {
                const aiResponseMessage: ChatMessage = {
                    id: Date.now().toString(), role: 'model', text: response.text
                };
                setMessages(prev => [...prev, aiResponseMessage]);
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : "An unexpected error occurred.";
            addToast(message, 'error');
            const errorMessage: ChatMessage = { id: Date.now().toString(), role: 'model', text: `Error: ${message}`};
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsAiLoading(false);
        }
    };
    
    const processToolCalls = async (toolCalls: any[]): Promise<any[]> => {
        const functionCallParts: any[] = [];

        for (const fnCall of toolCalls) {
            let functionResponseResult;

            if (fnCall.name === 'list_files') {
                functionResponseResult = { result: buildFileTreeString(files) };
            } else if (fnCall.name === 'read_file') {
                const { path } = fnCall.args;
                const node = findNodeByPath(files, path);
                const content = openFiles.get(path) ?? node?.content ?? `Error: File not found at path: ${path}`;
                functionResponseResult = { result: content };
            } else if (fnCall.name === 'write_file') {
                const { path, content } = fnCall.args;
                const existingNode = findNodeByPath(files, path);
                const originalContent = existingNode ? (openFiles.get(path) ?? existingNode.content) : '';
                const change: ProposedChange = { path, newContent: content, type: existingNode ? 'modify' : 'create', diff: generateDiff(path, originalContent ?? '', content) };
                onPreviewRequest(change);
                functionResponseResult = { result: "OK. The change has been proposed to the user for approval. Await user action." };
            } else if (fnCall.name === 'create_folder') {
                const { path } = fnCall.args;
                const change: ProposedChange = { path, type: 'create_folder' };
                onPreviewRequest(change);
                functionResponseResult = { result: "OK. The folder creation has been proposed to the user for approval. Await user action." };
            } else if (fnCall.name === 'propose_change_plan') {
                const newPlanMessage: ChatMessage = {
                    id: Date.now().toString(), role: 'model', text: "I have a plan to address your request.", proposedPlan: fnCall.args
                };
                setMessages(prev => [...prev, newPlanMessage]);
                return []; // Stop processing, wait for user approval
            } else if (fnCall.name === 'lint_file') {
                const { path } = fnCall.args;
                const node = findNodeByPath(files, path);
                const content = openFiles.get(path) ?? node?.content;
                if (content === undefined) {
                    functionResponseResult = { result: `Error: File not found or is empty at path: ${path}`};
                } else {
                    const lintResult = await lintFile(path, content, project.language);
                    functionResponseResult = { result: lintResult };
                }
            }

            if (functionResponseResult) {
                functionCallParts.push({ functionResponse: { name: fnCall.name, response: functionResponseResult }});
            }
        }
        return functionCallParts;
    };

    const handleSendMessage = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        if (!input.trim() || isAiLoading || !chat) return;
    
        const newUserMessage: ChatMessage = { id: Date.now().toString(), role: 'user', text: input };
        setMessages(prev => [...prev, newUserMessage]);
        
        const currentInput = input;
        setInput('');

        setIsAiLoading(true);
        addToast("Searching knowledge base...", "info");
        const relevantFiles = await knowledgeBaseService.search(currentInput);
        addToast(`Found ${relevantFiles.length} relevant file(s) in knowledge base.`, "info");
        setIsAiLoading(false);
        
        const knowledgeContext = relevantFiles.map(file => `
--- RELEVANT FILE: ${file.path} ---
\`\`\`
${file.content}
\`\`\`
`).join('\n\n');

        const fileTreeString = buildFileTreeString(files);
        const activeFileContent = activeFile ? openFiles.get(activeFile) : 'No file is currently open.';

        const workflow = WORKFLOWS.find(w => w.id === selectedWorkflow);
        const step = workflow?.steps.find(s => s.id === selectedStep);
        
        const focusContext = `
--- CURRENT FOCUS ---
Workflow: ${workflow?.name || 'None'} > Step: ${step?.name || 'None'}
${taskPlan ? `Current Task Plan: "${taskPlan.title}"` : ''}
Recent Terminal History (last 3):
${terminalHistory.slice(-3).map(line => `> ${line}`).join('\n') || 'N/A'}
---`;
        
        const initialPrompt = `${focusContext}

${knowledgeContext ? `--- RELEVANT CONTEXT FROM KNOWLEDGE BASE ---\n${knowledgeContext}\n-------------------------------------------\n\n` : ''}
---
CONTEXT:
File Tree:
${fileTreeString}
    
Active File (${activeFile || 'None'}):
\`\`\`
${activeFileContent}
\`\`\`
---
USER REQUEST: ${currentInput}`;
        
        await continueChat([{ text: initialPrompt }]);
    };
    
    const handlePlanResponse = (approved: boolean) => {
        const toolResponse = {
            functionResponse: {
                name: "propose_change_plan",
                response: { result: approved ? "Plan approved. You may now proceed with the implementation using other tools." : "Plan rejected. Please propose a new plan or ask for clarification." }
            }
        };
        
        // Remove the plan from the last message so the buttons disappear
        setMessages(prev => prev.map((msg, index) => index === prev.length - 1 ? { ...msg, proposedPlan: undefined } : msg));
        
        // Add a system message to record the decision
        const systemMessage: ChatMessage = { id: Date.now().toString(), role: 'system', text: `User ${approved ? 'approved' : 'rejected'} the plan.`};
        setMessages(prev => [...prev, systemMessage]);

        if (approved) {
            continueChat([toolResponse]);
        }
    };


    const workflow = WORKFLOWS.find(w => w.id === selectedWorkflow);

    return (
        <div className="h-full flex flex-col min-h-0">
            <div className="dx-pane-header">
                <span className="dx-label">{aiName}</span>
                <span className={`flex items-center gap-1.5 dx-label ${isAiLoading ? '!text-amber' : '!text-phosphor'}`}>
                    <span className="dx-dot" aria-hidden="true" />{isAiLoading ? 'Thinking' : 'Ready'}
                </span>
            </div>

            <FeasibilityAnalyzer
                project={project}
                report={report}
                setReport={setReport}
                isLoading={isLoading}
                setIsLoading={setIsLoading}
                addToast={addToast}
                trackPerformance={trackPerformance}
            />

            <div className="flex-grow flex flex-col overflow-hidden min-h-0">
                <div className="flex-shrink-0 grid grid-cols-2 gap-3 px-5 py-4 border-b border-[var(--border-secondary)]">
                    <div>
                        <label htmlFor="workflow-select" className="dx-label block mb-2">Workflow</label>
                        <select id="workflow-select" value={selectedWorkflow} onChange={e => setSelectedWorkflow(e.target.value)} className="dx-input !py-1 !text-xs">
                            {WORKFLOWS.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
                        </select>
                    </div>
                    <div>
                        <label htmlFor="step-select" className="dx-label block mb-2">Step</label>
                        <select id="step-select" value={selectedStep} onChange={e => setSelectedStep(e.target.value)} className="dx-input !py-1 !text-xs">
                            {workflow?.steps.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                        </select>
                    </div>
                </div>

                <div className="flex-grow overflow-y-auto space-y-7 px-5 py-6 text-sm leading-relaxed">
                    {messages.length === 0 && !isAiLoading && (
                        <div className="h-full flex flex-col items-center justify-center text-center gap-2 text-[var(--text-muted)]">
                            <p className="font-display uppercase tracking-wide text-[var(--text-secondary)] text-lg"><CorruptText text="Speak, mortal." /></p>
                            <p className="dx-label">Enter to send · Shift+Enter for newline</p>
                        </div>
                    )}
                    {messages.map(msg => {
                        if (msg.role === 'system') {
                            return (
                                <div key={msg.id} className="flex items-center gap-2 dx-label">
                                    <span className="flex-grow h-px bg-[var(--border-primary)]" />{msg.text}<span className="flex-grow h-px bg-[var(--border-primary)]" />
                                </div>
                            );
                        }
                        const isUser = msg.role === 'user';
                        const isError = msg.text.startsWith('Error:');
                        return (
                            <div key={msg.id} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                                <span className={`dx-label mb-2 ${isUser ? '' : '!text-blood-light'}`}>{isUser ? 'You' : `// ${aiName}`}</span>
                                <div className={`px-4 py-3 max-w-[92%] break-words whitespace-pre-wrap leading-relaxed ${isUser
                                    ? 'bg-[var(--bg-hover)] border-r-2 border-[var(--text-secondary)]'
                                    : isError
                                        ? 'bg-blood-deep/40 border-l-2 border-blood text-blood-light'
                                        : 'bg-[var(--bg-tertiary)] border-l-2 border-blood-light'}`}>
                                    {msg.text}
                                    {msg.proposedPlan && (
                                        <div className="mt-3 p-3 bg-[var(--bg-primary)] border border-[var(--border-primary)] text-xs font-mono whitespace-normal">
                                            <p className="font-display font-bold text-sm uppercase tracking-wide text-bone mb-2">{msg.proposedPlan.goal}</p>
                                            <p className="dx-label mb-1">Reasoning</p>
                                            <p className="text-[var(--text-secondary)] mb-3">{msg.proposedPlan.reasoning}</p>
                                            <p className="dx-label mb-1">Steps</p>
                                            <ol className="space-y-1 text-[var(--text-secondary)]">
                                                {msg.proposedPlan.steps.map((step, i) => (
                                                    <li key={i} className="flex gap-2"><span className="text-blood-light">{String(i + 1).padStart(2, '0')}</span><span>{step}</span></li>
                                                ))}
                                            </ol>
                                            <div className="flex justify-end gap-2 mt-4">
                                                <button onClick={() => handlePlanResponse(false)} className="dx-btn dx-btn-danger"><XIcon className="w-3.5 h-3.5"/><span>Reject</span></button>
                                                <button onClick={() => handlePlanResponse(true)} className="dx-btn dx-btn-success"><CheckIcon className="w-3.5 h-3.5"/><span>Approve</span></button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                    {isAiLoading && (
                        <div className="flex flex-col items-start">
                            <span className="dx-label mb-2 !text-blood-light">// {aiName}</span>
                            <div className="px-4 py-3 bg-[var(--bg-tertiary)] border-l-2 border-blood-light font-mono text-xs text-[var(--text-secondary)] dx-caret">
                                processing
                            </div>
                        </div>
                    )}
                    <div ref={chatEndRef} />
                </div>

                <form onSubmit={handleSendMessage} className="flex-shrink-0 p-5 border-t border-[var(--border-primary)] bg-[var(--bg-tertiary)]">
                    <div className="relative">
                        <span className="absolute left-3 top-[11px] font-mono text-blood-light select-none" aria-hidden="true">&gt;</span>
                        <textarea
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            placeholder={`Ask ${aiName} anything...`}
                            className="dx-input h-24 !pl-7 resize-none"
                            disabled={isAiLoading}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSendMessage();
                                }
                            }}
                            aria-label="AI Chat Input"
                        />
                    </div>
                    <button type="submit" disabled={isAiLoading || !input.trim()} className="dx-btn dx-btn-primary w-full mt-3">
                        {isAiLoading ? 'Thinking…' : 'Transmit'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default AiChat;
