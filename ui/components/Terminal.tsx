import React, { useRef, useEffect } from 'react';

interface TerminalProps {
  history: string[];
}

const Terminal: React.FC<TerminalProps> = ({ history }) => {
  const endOfTerminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfTerminalRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  return (
    <div className="h-full flex flex-col bg-[var(--terminal-bg)] min-h-0">
      <div className="dx-pane-header">
        <span className="dx-label">Terminal</span>
        <span className="dx-label">{history.length} lines</span>
      </div>
      <div className="flex-grow px-6 py-4 overflow-y-auto font-mono text-[13px] leading-7 text-[var(--terminal-text)]" style={{ textShadow: '0 0 6px rgb(var(--c-phosphor-base) / calc(.35 * var(--glow-strength)))' }}>
        {history.map((line, index) => (
          <div key={index}><span className="text-blood-light select-none">✝ </span>{line}</div>
        ))}
        <div className="dx-caret text-[var(--text-muted)]"><span className="text-blood-light select-none">✝ </span></div>
        <div ref={endOfTerminalRef} />
      </div>
    </div>
  );
};

export default Terminal;
