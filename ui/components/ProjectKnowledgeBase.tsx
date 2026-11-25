import React from 'react';
import XIcon from './icons/XIcon';
import BrainIcon from './icons/BrainIcon';
import { KnowledgeBaseData } from '../types';

interface ProjectKnowledgeBaseProps {
  onClose: () => void;
  knowledgeBaseData: KnowledgeBaseData;
  onIndexProject: () => void;
  isIndexing: boolean;
}

const ProjectKnowledgeBase: React.FC<ProjectKnowledgeBaseProps> = ({ onClose, knowledgeBaseData, onIndexProject, isIndexing }) => {
  return (
    <div className="dx-backdrop">
      <div className="dx-dialog w-full max-w-3xl h-[80vh]  flex flex-col p-4 text-[var(--text-primary)]">
        <header className="flex items-center justify-between pb-4 border-b border-[var(--border-primary)]">
          <h2 className="font-display text-xl font-bold uppercase tracking-wide text-blood-light flex items-center space-x-2">
            <BrainIcon className="w-8 h-8"/>
            <span>Project Knowledge Base</span>
          </h2>
          <button onClick={onClose} className="text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
            <XIcon className="w-8 h-8" />
          </button>
        </header>
        <main className="flex-grow mt-4 overflow-y-auto bg-[var(--bg-primary)] p-2 rounded">
            {Array.from(knowledgeBaseData.entries()).length === 0 ? (
                <div className="text-center text-[var(--text-muted)] mt-10">
                    <p>The knowledge base is empty.</p>
                    <p>Index the project to enable semantic search for the AI.</p>
                </div>
            ) : (
                <div className="space-y-2">
                    {Array.from(knowledgeBaseData.entries()).map(([path, entry]) => (
                        <div key={path} className="bg-[var(--bg-tertiary)] p-3 rounded">
                            <p className="font-mono text-[var(--link-text)] text-sm">{path}</p>
                            <p className="text-[var(--text-secondary)] text-xs italic mt-1">"{entry.summary}"</p>
                        </div>
                    ))}
                </div>
            )}
        </main>
         <footer className="flex-shrink-0 flex items-center justify-end p-4 border-t border-[var(--border-primary)]">
            <button 
                onClick={onIndexProject}
                disabled={isIndexing}
                className="dx-btn dx-btn-primary"
            >
                {isIndexing && <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>}
                <span>{isIndexing ? 'Indexing...' : 'Re-index Project'}</span>
            </button>
        </footer>
      </div>
    </div>
  );
};

export default ProjectKnowledgeBase;