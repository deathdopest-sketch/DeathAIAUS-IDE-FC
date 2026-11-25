import React from 'react';
import ChartBarIcon from './icons/ChartBarIcon';
import ClipboardListIcon from './icons/ClipboardListIcon';
import BookOpenIcon from './icons/BookOpenIcon';
import WrenchScrewdriverIcon from './icons/WrenchScrewdriverIcon';
import RocketIcon from './icons/RocketIcon';
import BrainIcon from './icons/BrainIcon';
import TrashIcon from './icons/TrashIcon';
import UndoIcon from './icons/UndoIcon';
import SkullIcon from './icons/SkullIcon';
import SettingsIcon from './icons/SettingsIcon';
import { BloodDrips, CorruptText } from './ui/haunt';

interface ToolbarProps {
  onShowPerfTracker: () => void;
  onShowTaskPlanner: () => void;
  onShowDocs: () => void;
  onShowSettings: () => void;
  onShowFeatures: () => void;
  onShowKnowledgeBase: () => void;
  onProjectReset: () => void;
}

const Toolbar: React.FC<ToolbarProps> = ({
  onShowPerfTracker,
  onShowTaskPlanner,
  onShowDocs,
  onShowSettings,
  onShowFeatures,
  onShowKnowledgeBase,
  onProjectReset
}) => {
  return (
    <header className="h-[var(--bar-h)] bg-[var(--bg-tertiary)] flex items-center justify-between px-6 flex-shrink-0 relative z-10">
      {/* heartbeat line + seeping blood under the bar */}
      <div className="absolute inset-x-0 bottom-0 h-px bg-blood-deep" aria-hidden="true" />
      <div className="absolute left-0 bottom-0 h-px w-64 bg-blood-light dx-heartbeat" aria-hidden="true" />
      <div className="absolute inset-x-0 top-full h-0">
        <BloodDrips count={12} maxLen={22} />
      </div>

      <div className="flex items-center gap-6 min-w-0">
        <div className="flex items-center gap-3 pr-6 border-r border-[var(--border-primary)] h-8 dx-tear">
          <SkullIcon className="w-5 h-5 text-blood-light" />
          <CorruptText text="DEATHAI" every={[5000, 14000]} className="font-display font-bold text-lg tracking-[0.2em] text-bone" />
          <span className="dx-tag text-ochre">AUS</span>
        </div>

        <nav className="flex items-center gap-2 overflow-x-auto" aria-label="Main tools">
          <button className="dx-btn dx-btn-primary" aria-label="Fix Errors">
            <WrenchScrewdriverIcon className="w-3.5 h-3.5" />
            <span>Fix Errors</span>
          </button>
          <button className="dx-btn" aria-label="Undo AI Change" disabled>
            <UndoIcon className="w-3.5 h-3.5" />
            <span>Undo AI</span>
          </button>
          <div className="h-5 w-px bg-[var(--border-primary)] mx-3" aria-hidden="true" />
          <button onClick={onShowTaskPlanner} className="dx-btn" aria-label="Open Task Planner">
            <ClipboardListIcon className="w-3.5 h-3.5" />
            <span>Tasks</span>
          </button>
          <button onClick={onShowKnowledgeBase} className="dx-btn" aria-label="Open Knowledge Base">
            <BrainIcon className="w-3.5 h-3.5" />
            <span>Knowledge</span>
          </button>
          <button onClick={onShowPerfTracker} className="dx-btn" aria-label="Open Model Stats">
            <ChartBarIcon className="w-3.5 h-3.5" />
            <span>Models</span>
          </button>
          <button onClick={onShowDocs} className="dx-btn" aria-label="Open Documentation">
            <BookOpenIcon className="w-3.5 h-3.5" />
            <span>Docs</span>
          </button>
          <button onClick={onShowFeatures} className="dx-btn" aria-label="Open Features List">
            <RocketIcon className="w-3.5 h-3.5" />
            <span>Features</span>
          </button>
        </nav>
      </div>

      <div className="flex items-center gap-3 flex-shrink-0 pl-6">
        <div className="flex items-center gap-2 px-4 h-[34px] border border-[var(--border-primary)] text-phosphor dx-flicker" role="status" aria-label="Backend Status">
          <span className="dx-dot" aria-hidden="true" />
          <span className="dx-label !text-phosphor">ReapGate // Online</span>
        </div>
        <button onClick={onProjectReset} className="dx-btn dx-btn-icon dx-btn-danger" aria-label="Reset Project" title="Reset project">
          <TrashIcon className="w-4 h-4" />
        </button>
        <button onClick={onShowSettings} className="dx-btn dx-btn-icon" aria-label="Open Settings" title="Settings">
          <SettingsIcon className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};

export default Toolbar;
