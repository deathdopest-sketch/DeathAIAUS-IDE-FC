
import React, { forwardRef, useImperativeHandle } from 'react';

export interface CodeEditorHandles {
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;
}

interface CodeEditorProps {
    id: string;
    role: string;
    content: string;
    onChange: (content: string) => void;
}

// A simple placeholder that doesn't actually support undo/redo yet,
// but satisfies the interface to allow the app to compile and run.
const CodeEditor = forwardRef<CodeEditorHandles, CodeEditorProps>(({ content, onChange, ...props }, ref) => {

    useImperativeHandle(ref, () => ({
        undo: () => console.warn("Undo not implemented"),
        redo: () => console.warn("Redo not implemented"),
        canUndo: false,
        canRedo: false,
    }));

    const lineCount = Math.max(1, content.split('\n').length);
    const gutterRef = React.useRef<HTMLDivElement>(null);

    return (
        <div className="absolute inset-0 flex font-mono text-[13.5px] leading-[1.75]">
            <div ref={gutterRef} className="flex-shrink-0 overflow-hidden select-none py-6 pl-5 pr-4 text-right text-[var(--text-muted)] border-r border-[var(--border-secondary)] bg-[var(--bg-primary)]" aria-hidden="true">
                {Array.from({ length: lineCount }, (_, i) => <div key={i}>{i + 1}</div>)}
            </div>
            <textarea
                {...props}
                value={content}
                onChange={(e) => onChange(e.target.value)}
                onScroll={(e) => { if (gutterRef.current) gutterRef.current.scrollTop = e.currentTarget.scrollTop; }}
                className="flex-grow h-full py-6 px-6 bg-[var(--bg-primary)] text-[var(--text-primary)] resize-none focus:outline-none caret-blood-light selection:bg-blood/50 whitespace-pre overflow-auto"
                spellCheck="false"
            />
        </div>
    );
});

export default CodeEditor;
