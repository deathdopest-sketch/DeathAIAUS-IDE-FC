import React from 'react';
import XIcon from './icons/XIcon';
import CheckIcon from './icons/CheckIcon';
import { ProposedChange } from '../types';

interface PreviewDialogProps {
  change: ProposedChange;
  onClose: () => void;
  onApply: () => void;
}

const DiffLine: React.FC<{ line: string }> = ({ line }) => {
    if (line.startsWith('+')) {
        return <div className="bg-green-900 bg-opacity-50 text-green-300">{line}</div>;
    }
    if (line.startsWith('-')) {
        return <div className="bg-red-900 bg-opacity-50 text-red-300">{line}</div>;
    }
    return <div className="text-[var(--text-secondary)]">{line}</div>;
};

const PreviewDialog: React.FC<PreviewDialogProps> = ({ change, onClose, onApply }) => {

  const renderChangeType = () => {
    switch (change.type) {
        case 'create':
            return <span className="text-sm font-bold bg-green-700 text-white px-2 py-1 rounded">CREATE</span>;
        case 'modify':
            return <span className="text-sm font-bold bg-yellow-600 text-white px-2 py-1 rounded">MODIFY</span>;
        case 'delete':
            return <span className="text-sm font-bold bg-red-700 text-white px-2 py-1 rounded">DELETE</span>;
        case 'create_folder':
            return <span className="text-sm font-bold bg-blue-600 text-white px-2 py-1 rounded">CREATE FOLDER</span>
    }
  }

  return (
    <div className="dx-backdrop" role="dialog" aria-modal="true" aria-labelledby="preview-title">
      <div className="dx-dialog w-full max-w-4xl h-[80vh]  flex flex-col p-4 text-[var(--text-primary)]">
        <header className="flex items-center justify-between pb-4 border-b border-[var(--border-primary)]">
          <div className="flex items-center space-x-4">
            <h2 id="preview-title" className="font-display text-xl font-bold uppercase tracking-wide text-blood-light">🤖 AI Change Preview</h2>
            {renderChangeType()}
          </div>
          <button onClick={onClose} className="text-[var(--text-secondary)] hover:text-[var(--text-primary)]" aria-label="Close Preview">
            <XIcon className="w-8 h-8" />
          </button>
        </header>

        <div className="my-2 p-2 bg-[var(--bg-primary)] rounded font-mono text-sm">
            <p className="font-bold">Target Path:</p>
            <p className="text-[var(--link-text)]">{change.path}</p>
        </div>

        <main className="flex-grow overflow-y-auto bg-[var(--bg-primary)] p-2 rounded font-mono text-sm">
          {change.type === 'create_folder' ? (
                <div className="flex items-center justify-center h-full text-[var(--text-muted)]">
                    <p>A new folder will be created at the specified path.</p>
                </div>
            ) : (
                <pre className="whitespace-pre-wrap">
                    {change.diff ? change.diff.split('\n').map((line, i) => <DiffLine key={i} line={line} />) : change.newContent}
                </pre>
            )}
        </main>

        <footer className="flex-shrink-0 flex items-center justify-end p-4 border-t border-[var(--border-primary)] space-x-4">
            <button onClick={onClose} className="dx-btn">
                <XIcon className="w-5 h-5" />
                <span>Reject</span>
            </button>
            <button onClick={onApply} className="dx-btn dx-btn-success">
                <CheckIcon className="w-5 h-5" />
                <span>Apply Changes</span>
            </button>
        </footer>
      </div>
    </div>
  );
};

export default PreviewDialog;