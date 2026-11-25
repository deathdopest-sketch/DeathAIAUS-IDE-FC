
import React, { useState, useEffect, useCallback } from 'react';
import Split from 'react-split';
import WelcomeScreen from './components/WelcomeScreen';
import Toolbar from './components/Toolbar';
import FileTree, { FileNode } from './components/FileTree';
import EditorTabs from './components/EditorTabs';
import AiChat from './components/AiChat';
import Terminal from './components/Terminal';
import ToastContainer from './components/ui/ToastContainer';
import PreviewDialog from './components/PreviewDialog';
import ModelPerformanceTracker from './components/ModelPerformanceTracker';
import SettingsDialog from './components/SettingsDialog';
import Documentation from './components/Documentation';
import FeaturesList from './components/FeaturesList';
import TaskPlanner from './components/TaskPlanner';
import ProjectKnowledgeBase from './components/ProjectKnowledgeBase';
import { KnowledgeBaseService } from './services/knowledgeBaseService';
import {
  Project, FeasibilityReport, ChatMessage, WorkflowSettings, ProposedChange, ToastData, ToastType,
  ModelPerformanceData, ContextMenuData, CreationInputData, TaskPlan, KnowledgeBaseData
} from './types';
import { AVAILABLE_MODELS } from './constants';
import { sortFileTree } from './utils/sortFileTree';
import { useWhisper, corrupt } from './components/ui/haunt';

const App: React.FC = () => {
    const [project, setProject] = useState<Project | null>(null);
    const [files, setFiles] = useState<FileNode[]>([]);
    const [openFiles, setOpenFiles] = useState<Map<string, string>>(new Map());
    const [activeFile, setActiveFile] = useState<string | null>(null);

    // AI & Chat State
    const [chat, setChat] = useState<any>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isAiLoading, setIsAiLoading] = useState(false);
    const [activeModel, setActiveModel] = useState(AVAILABLE_MODELS[AVAILABLE_MODELS.length - 1]);
    const [aiName, setAiName] = useState('Thanatos');
    const [aiPersonality, setAiPersonality] = useState('You are a brutally honest, expert-level software engineer who gets straight to the point.');


    // UI State
    const [toasts, setToasts] = useState<ToastData[]>([]);
    const [theme, setTheme] = useState('deathai');
    const [backgroundImage, setBackgroundImage] = useState<string | null>(null);

    // Modal & Dialog State
    const [showPerfTracker, setShowPerfTracker] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [showDocs, setShowDocs] = useState(false);
    const [showFeatures, setShowFeatures] = useState(false);
    const [showTaskPlanner, setShowTaskPlanner] = useState(false);
    const [showKnowledgeBase, setShowKnowledgeBase] = useState(false);
    const [proposedChange, setProposedChange] = useState<ProposedChange | null>(null);

    // Feasibility & Planning State
    const [report, setReport] = useState<FeasibilityReport | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [taskPlan, setTaskPlan] = useState<TaskPlan | null>(null);

    // Performance & Knowledge Base State
    const [perfStats, setPerfStats] = useState<ModelPerformanceData>({});
    const [knowledgeBaseService] = useState(() => new KnowledgeBaseService());
    const [knowledgeBaseData, setKnowledgeBaseData] = useState<KnowledgeBaseData>(new Map());
    const [isIndexing, setIsIndexing] = useState(false);


    // Other State
    const [terminalHistory, setTerminalHistory] = useState<string[]>([]);
    const [workflowSettings, setWorkflowSettings] = useState<WorkflowSettings>({});
    const [contextMenu, setContextMenu] = useState<ContextMenuData | null>(null);
    const [creationInput, setCreationInput] = useState<CreationInputData | null>(null);
    const whisper = useWhisper();

    useEffect(() => {
        document.documentElement.dataset.theme = theme;
        document.documentElement.dataset.bgImage = backgroundImage ? 'true' : 'false';
        if (backgroundImage) {
            document.body.style.backgroundImage = `url(${backgroundImage})`;
            document.body.style.backgroundSize = 'cover';
            document.body.style.backgroundPosition = 'center';
            document.body.style.backgroundAttachment = 'fixed';
        } else {
            document.body.style.backgroundImage = 'none';
        }
    }, [theme, backgroundImage]);
    
    const addToast = useCallback((message: string, type: ToastType = 'info') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type }]);
        setTimeout(() => {
            setToasts(prev => prev.filter(t => t.id !== id));
        }, 5000);
    }, []);

    const handleProjectCreate = (newProject: Project, initialFiles: FileNode[]) => {
        setProject(newProject);
        setFiles(sortFileTree(initialFiles));
        addToast(`Project "${newProject.name}" created successfully!`, 'success');
    };
    
    const findNodeByPath = (nodes: FileNode[], path: string): FileNode | null => {
      for (const node of nodes) {
          if (node.path === path) return node;
          if (node.children) {
              const found = findNodeByPath(node.children, path);
              if (found) return found;
          }
      }
      return null;
    };

    const handleFileOpen = (file: FileNode) => {
        if (!openFiles.has(file.path)) {
            setOpenFiles(prev => new Map(prev).set(file.path, file.content || ''));
        }
        setActiveFile(file.path);
    };
    
    const handleContentChange = (path: string, content: string) => {
        setOpenFiles(prev => new Map(prev).set(path, content));
    };
    
    const handleTabClose = (path: string) => {
        setOpenFiles(prev => {
            const newMap = new Map(prev);
            newMap.delete(path);
            return newMap;
        });
        if (activeFile === path) {
            const remainingFiles = Array.from(openFiles.keys()).filter(p => p !== path);
            setActiveFile(remainingFiles.length > 0 ? remainingFiles[0] : null);
        }
    };
    
    const trackPerformance = useCallback((model: string, duration: number, error?: string) => {
        setPerfStats(prev => {
            const newStats = { ...prev };
            if (!newStats[model]) {
                newStats[model] = { successes: 0, failures: 0, totalTime: 0, errorLogs: [] };
            }
            if (error) {
                newStats[model].failures++;
                newStats[model].errorLogs.push({ timestamp: Date.now(), message: error });
            } else {
                newStats[model].successes++;
                newStats[model].totalTime += duration;
            }
            return newStats;
        });
    }, []);

    const sendMessageToChat = async (message: string) => {
      // Dummy function for now
      console.log("Sending message to chat:", message);
    }
    
    const handleApplyChange = () => {
        if (!proposedChange) return;

        const { path, newContent, type } = proposedChange;
        
        const updateFileTree = (nodes: FileNode[], fullPath: string): FileNode[] => {
            return nodes.map(node => {
                if (node.path === fullPath && node.content !== undefined) {
                    return { ...node, content: newContent! };
                }
                if (node.children) {
                    return { ...node, children: updateFileTree(node.children, fullPath) };
                }
                return node;
            });
        };
        
        if (type === 'modify') {
            const node = findNodeByPath(files, path);
            if(node){
                setFiles(updateFileTree(files, path));
                if(openFiles.has(path)){
                    handleContentChange(path, newContent!);
                }
                addToast(`File ${path} modified.`, 'success');
            }
        }
        // Other change types (create, delete, etc.) would be handled here.
        setProposedChange(null);
    };

    const handleIndexProject = async () => {
      if (!project) return;
      setIsIndexing(true);
      addToast('Indexing project files...', 'info');
      await knowledgeBaseService.indexProject(files, project.language);
      setKnowledgeBaseData(new Map(knowledgeBaseService.getKnowledgeBase()));
      setIsIndexing(false);
      addToast('Project indexing complete.', 'success');
    };

    if (!project) {
        return <WelcomeScreen onProjectCreate={handleProjectCreate} addToast={addToast} />;
    }

    return (
        <div className="h-screen w-screen flex flex-col bg-[var(--bg-primary)] text-[var(--text-primary)]">
            <Toolbar 
                onShowPerfTracker={() => setShowPerfTracker(true)}
                onShowTaskPlanner={() => setShowTaskPlanner(true)}
                onShowDocs={() => setShowDocs(true)}
                onShowSettings={() => setShowSettings(true)}
                onShowFeatures={() => setShowFeatures(true)}
                onShowKnowledgeBase={() => setShowKnowledgeBase(true)}
                onProjectReset={() => { if(window.confirm('Are you sure?')) { setProject(null); setFiles([]); setOpenFiles(new Map()); setActiveFile(null); setMessages([]); }}}
            />
            <main className="flex-grow flex overflow-hidden">
                <Split
                    sizes={[18, 52, 30]}
                    minSize={[220, 420, 340]}
                    gutterSize={6}
                    className="flex w-full h-full"
                >
                    <div className="h-full bg-[var(--bg-secondary)] overflow-y-auto">
                      <FileTree 
                        files={files} 
                        onFileOpen={handleFileOpen}
                        contextMenu={contextMenu}
                        setContextMenu={setContextMenu}
                        creationInput={creationInput}
                        setCreationInput={setCreationInput}
                        onFileCreate={(path) => console.log('create file', path)}
                        onFolderCreate={(path) => console.log('create folder', path)}
                       />
                    </div>
                    <div className="h-full flex flex-col">
                        <Split direction="vertical" sizes={[68, 32]} minSize={[200, 120]} gutterSize={6} className="flex flex-col h-full">
                            <EditorTabs
                                openFiles={openFiles}
                                activeFile={activeFile}
                                onTabClick={setActiveFile}
                                onTabClose={handleTabClose}
                                onContentChange={handleContentChange}
                            />
                            <Terminal history={terminalHistory} />
                        </Split>
                    </div>
                    <div className="h-full bg-[var(--bg-secondary)] overflow-y-auto">
                        <AiChat 
                            project={project}
                            report={report}
                            setReport={setReport}
                            isLoading={isLoading}
                            setIsLoading={setIsLoading}
                            addToast={addToast}
                            trackPerformance={trackPerformance}
                            chat={chat}
                            setChat={setChat}
                            messages={messages}
                            setMessages={setMessages}
                            isAiLoading={isAiLoading}
                            setIsAiLoading={setIsAiLoading}
                            activeModel={activeModel}
                            workflowSettings={workflowSettings}
                            files={files}
                            openFiles={openFiles}
                            activeFile={activeFile}
                            onPreviewRequest={setProposedChange}
                            findNodeByPath={findNodeByPath}
                            knowledgeBaseService={knowledgeBaseService}
                            terminalHistory={terminalHistory}
                            taskPlan={taskPlan}
                            aiName={aiName}
                            aiPersonality={aiPersonality}
                        />
                    </div>
                </Split>
            </main>
            <footer className="h-[var(--status-h)] flex-shrink-0 flex items-center justify-between px-6 bg-[var(--bg-tertiary)] border-t border-[var(--border-secondary)] font-mono text-[10px] uppercase tracking-[0.14em] text-[var(--text-muted)]">
                <div className="flex items-center gap-6 min-w-0">
                    <span className="text-blood-light">■ {project.name}</span>
                    <span>{project.language}</span>
                    {whisper
                        ? <span className="truncate text-blood-light normal-case tracking-normal" title={whisper}>{corrupt(whisper, 0.12)}</span>
                        : <span className="truncate">{activeFile ?? 'no buffer'}</span>}
                </div>
                <div className="flex items-center gap-6 flex-shrink-0">
                    <span>{activeModel.split('-')[0]}</span>
                    <span>UTF-8</span>
                    <span className="text-ochre">AUS // {new Date().toLocaleDateString('en-AU')}</span>
                </div>
            </footer>
            <ToastContainer toasts={toasts} setToasts={setToasts} />
            {proposedChange && <PreviewDialog change={proposedChange} onClose={() => setProposedChange(null)} onApply={handleApplyChange} />}
            {showPerfTracker && <ModelPerformanceTracker stats={perfStats} onClose={() => setShowPerfTracker(false)} onClear={() => setPerfStats({})} />}
            {showSettings && <SettingsDialog 
                onClose={() => setShowSettings(false)}
                activeModel={activeModel} setActiveModel={setActiveModel}
                workflowSettings={workflowSettings} setWorkflowSettings={setWorkflowSettings}
                theme={theme} setTheme={setTheme}
                backgroundImage={backgroundImage} setBackgroundImage={setBackgroundImage}
                aiName={aiName} setAiName={setAiName}
                aiPersonality={aiPersonality} setAiPersonality={setAiPersonality}
            />}
            {showDocs && <Documentation onClose={() => setShowDocs(false)} />}
            {showFeatures && <FeaturesList onClose={() => setShowFeatures(false)} />}
            {showTaskPlanner && <TaskPlanner onClose={() => setShowTaskPlanner(false)} project={project} addToast={addToast} sendMessageToChat={sendMessageToChat} taskPlan={taskPlan} setTaskPlan={setTaskPlan} />}
            {showKnowledgeBase && <ProjectKnowledgeBase onClose={() => setShowKnowledgeBase(false)} knowledgeBaseData={knowledgeBaseData} onIndexProject={handleIndexProject} isIndexing={isIndexing} />}
        </div>
    );
};

export default App;
