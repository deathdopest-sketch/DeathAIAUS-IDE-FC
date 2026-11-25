import React from 'react';
import CodeEditor, { CodeEditorHandles } from './ui/CodeEditor';
import UndoIcon from './icons/UndoIcon';
import RedoIcon from './icons/RedoIcon';
import XIcon from './icons/XIcon';
import SkullIcon from './icons/SkullIcon';

interface EditorTabsProps {
    openFiles: Map<string, string>;
    activeFile: string | null;
    onTabClick: (path: string) => void;
    onTabClose: (path: string) => void;
    onContentChange: (path: string, content: string) => void;
}

const EditorTabs: React.FC<EditorTabsProps> = ({ openFiles, activeFile, onTabClick, onTabClose, onContentChange }) => {

    const editorRef = React.useRef<CodeEditorHandles>(null);
    const [canUndo, setCanUndo] = React.useState(false);
    const [canRedo, setCanRedo] = React.useState(false);

    React.useEffect(() => {
        const interval = setInterval(() => {
            setCanUndo(editorRef.current?.canUndo ?? false);
            setCanRedo(editorRef.current?.canRedo ?? false);
        }, 200);
        return () => clearInterval(interval);
    }, []);

    const handleClose = (e: React.MouseEvent, path: string) => {
        e.stopPropagation();
        onTabClose(path);
    }

    const handleUndo = () => {
        editorRef.current?.undo();
    };

    const handleRedo = () => {
        editorRef.current?.redo();
    };

    const currentFileContent = activeFile ? openFiles.get(activeFile) || '' : '';

    return (
        <div className="flex flex-col h-full bg-[var(--bg-primary)]">
            <div className="flex-shrink-0 flex justify-between items-stretch h-11 bg-[var(--bg-secondary)] border-b border-[var(--border-primary)]">
                <div role="tablist" aria-orientation="horizontal" className="flex overflow-x-auto">
                    {Array.from(openFiles.keys()).map(path => {
                        const isActive = activeFile === path;
                        const name = path.split('/').pop();
                        return (
                            <div
                                key={path}
                                role="tab"
                                aria-selected={isActive}
                                aria-controls={`editor-panel-${path.replace(/[^a-zA-Z0-9]/g, '-')}`}
                                onClick={() => onTabClick(path)}
                                className={`group relative flex items-center gap-3 pl-5 pr-3 cursor-pointer border-r border-[var(--border-secondary)] font-mono text-xs whitespace-nowrap transition-colors ${isActive
                                    ? 'bg-[var(--bg-primary)] text-bone'
                                    : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]'}`}
                            >
                                {isActive && <span className="absolute inset-x-0 top-0 h-[2px] bg-blood-light shadow-bleed" aria-hidden="true" />}
                                <span className={isActive ? 'text-blood-light' : 'text-[var(--text-muted)]'}>›</span>
                                <span>{name}</span>
                                <button onClick={(e) => handleClose(e, path)} className="p-0.5 opacity-40 group-hover:opacity-100 hover:text-blood-light" aria-label={`Close tab ${name}`}>
                                    <XIcon className="w-3 h-3" />
                                </button>
                            </div>
                        );
                    })}
                    {openFiles.size === 0 && (
                        <div className="flex items-center px-5 dx-label">No buffer</div>
                    )}
                </div>
                {activeFile && (
                    <div className="flex items-center gap-1 px-2">
                        <button onClick={handleUndo} disabled={!canUndo} className="p-1 text-[var(--text-secondary)] hover:text-bone disabled:opacity-30 disabled:cursor-not-allowed" aria-label="Undo">
                            <UndoIcon className="w-4 h-4" />
                        </button>
                        <button onClick={handleRedo} disabled={!canRedo} className="p-1 text-[var(--text-secondary)] hover:text-bone disabled:opacity-30 disabled:cursor-not-allowed" aria-label="Redo">
                            <RedoIcon className="w-4 h-4" />
                        </button>
                    </div>
                )}
            </div>
            {activeFile && (
                <div className="flex-shrink-0 px-6 h-8 flex items-center gap-1.5 font-mono text-[11px] text-[var(--text-muted)] border-b border-[var(--border-secondary)]">
                    {activeFile.split('/').map((seg, i, arr) => (
                        <React.Fragment key={i}>
                            {i > 0 && <span className="text-blood-light/70">/</span>}
                            <span className={i === arr.length - 1 ? 'text-[var(--text-secondary)]' : ''}>{seg}</span>
                        </React.Fragment>
                    ))}
                </div>
            )}
            <div className="flex-grow relative min-h-0">
                {activeFile ? (
                    <CodeEditor
                        ref={editorRef}
                        id={`editor-panel-${activeFile.replace(/[^a-zA-Z0-9]/g, '-')}`}
                        role="tabpanel"
                        content={currentFileContent}
                        onChange={(content) => onContentChange(activeFile, content)}
                    />
                ) : (
                    <div className="flex flex-col items-center justify-center h-full gap-6 text-[var(--text-muted)]">
                        <SkullIcon className="w-16 h-16 text-[var(--border-primary)] dx-flicker" />
                        <p className="dx-label">Select a file to raise it from the dead</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default EditorTabs;
