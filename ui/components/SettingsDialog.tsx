import React, { useState } from 'react';
import XIcon from './icons/XIcon';
import { WorkflowSettings } from '../types';
import { AVAILABLE_MODELS, WORKFLOWS } from '../constants';

interface SettingsDialogProps {
  onClose: () => void;
  activeModel: string;
  setActiveModel: (model: string) => void;
  workflowSettings: WorkflowSettings;
  setWorkflowSettings: (settings: WorkflowSettings) => void;
  theme: string;
  setTheme: (theme: string) => void;
  backgroundImage: string | null;
  setBackgroundImage: (image: string | null) => void;
  aiName: string;
  setAiName: (name: string) => void;
  aiPersonality: string;
  setAiPersonality: (personality: string) => void;
}

const THEMES = [
    { id: 'deathai', name: 'DeathAI Glitch (Default)' },
    { id: 'dark', name: 'Dark' },
    { id: 'light', name: 'Light' },
    { id: 'gothic', name: 'Gothic' },
    { id: 'cyberpunk', name: 'Cyberpunk' },
];

const SettingsDialog: React.FC<SettingsDialogProps> = ({
  onClose,
  activeModel,
  setActiveModel,
  workflowSettings,
  setWorkflowSettings,
  theme,
  setTheme,
  backgroundImage,
  setBackgroundImage,
  aiName,
  setAiName,
  aiPersonality,
  setAiPersonality,
}) => {
  const [currentTab, setCurrentTab] = useState('general');
  const [localWorkflowSettings, setLocalWorkflowSettings] = useState(workflowSettings);

  const handleSave = () => {
    setWorkflowSettings(localWorkflowSettings);
    onClose();
  };
  
  const handleWorkflowChange = (stepId: string, model: string) => {
    setLocalWorkflowSettings(prev => ({
        ...prev,
        [stepId]: model
    }));
  };
  
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
        if (file.size > 2 * 1024 * 1024) { // 2MB limit
            alert('File is too large. Please select an image under 2MB.');
            return;
        }
        const reader = new FileReader();
        reader.onloadend = () => {
            setBackgroundImage(reader.result as string);
        };
        reader.readAsDataURL(file);
    }
  };

  return (
    <div className="dx-backdrop">
      <div className="dx-dialog w-full max-w-3xl h-[80vh]  flex flex-col text-[var(--text-primary)]">
        <header className="flex items-center justify-between p-4 border-b border-[var(--border-primary)]">
          <h2 className="font-display text-xl font-bold uppercase tracking-wide text-[var(--text-primary)]">⚙️ Settings</h2>
          <button onClick={onClose} className="text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
            <XIcon className="w-8 h-8" />
          </button>
        </header>

        <main className="flex-grow flex p-4 overflow-hidden">
            <div className="w-1/4 border-r border-[var(--border-primary)] pr-4">
                <nav className="space-y-2">
                    <button onClick={() => setCurrentTab('general')} className={`w-full text-left px-3 py-2 font-mono text-xs uppercase tracking-wider border-l-2 ${currentTab === 'general' ? 'border-blood bg-blood/10 text-bone' : 'border-transparent text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'}`}>General</button>
                    <button onClick={() => setCurrentTab('appearance')} className={`w-full text-left px-3 py-2 font-mono text-xs uppercase tracking-wider border-l-2 ${currentTab === 'appearance' ? 'border-blood bg-blood/10 text-bone' : 'border-transparent text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'}`}>Appearance</button>
                    <button onClick={() => setCurrentTab('workflows')} className={`w-full text-left px-3 py-2 font-mono text-xs uppercase tracking-wider border-l-2 ${currentTab === 'workflows' ? 'border-blood bg-blood/10 text-bone' : 'border-transparent text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'}`}>Workflows</button>
                </nav>
            </div>
            <div className="w-3/4 pl-4 overflow-y-auto">
                {currentTab === 'general' && (
                    <div>
                        <h3 className="font-display text-lg font-bold uppercase tracking-wide mb-4">AI Settings</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="dx-label block mb-2">AI Assistant Name</label>
                                <input 
                                    type="text"
                                    value={aiName}
                                    onChange={(e) => setAiName(e.target.value)}
                                    placeholder="e.g., Thanatos"
                                    className="dx-input"
                                />
                                <p className="text-xs text-[var(--text-muted)] mt-1">Give your AI assistant a custom name.</p>
                            </div>
                            <div>
                                <label className="dx-label block mb-2">AI Personality</label>
                                <textarea 
                                    value={aiPersonality}
                                    onChange={(e) => setAiPersonality(e.target.value)}
                                    rows={5}
                                    placeholder="Describe the AI's personality. e.g., 'You are a brutally honest assistant who gets straight to the point.'"
                                    className="dx-input resize-y"
                                />
                                <p className="text-xs text-[var(--text-muted)] mt-1">This is the core system instruction for the AI. Be descriptive about its desired behavior and tone.</p>
                            </div>
                            <div>
                                <label className="dx-label block mb-2">Default Chat Model</label>
                                <select value={activeModel} onChange={e => setActiveModel(e.target.value)} className="dx-input">
                                    {AVAILABLE_MODELS.map(model => <option key={model} value={model}>{model}</option>)}
                                </select>
                                <p className="text-xs text-[var(--text-muted)] mt-1">This model will be used for general chat unless a workflow-specific model is set.</p>
                            </div>
                        </div>
                    </div>
                )}
                 {currentTab === 'appearance' && (
                    <div>
                        <h3 className="font-display text-lg font-bold uppercase tracking-wide mb-4">Appearance</h3>
                        <div className="space-y-6">
                            <div>
                                <label className="dx-label block mb-2">Theme</label>
                                <select value={theme} onChange={e => setTheme(e.target.value)} className="dx-input">
                                    {THEMES.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                                </select>
                                <p className="text-xs text-[var(--text-muted)] mt-1">Select the visual theme for the IDE.</p>
                            </div>
                             <div>
                                <label className="dx-label block mb-2">Custom Background Image</label>
                                <input 
                                    type="file" 
                                    accept="image/png, image/jpeg, image/gif, image/webp"
                                    onChange={handleImageUpload}
                                    className="w-full text-sm text-[var(--text-secondary)] file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-[var(--bg-tertiary)] file:text-[var(--text-primary)] hover:file:bg-[var(--bg-hover)]"
                                />
                                {backgroundImage && (
                                    <div className="mt-2 flex items-center space-x-4">
                                        <img src={backgroundImage} alt="Background preview" className="w-32 h-20 object-cover rounded border border-[var(--border-primary)]" />
                                        <button onClick={() => setBackgroundImage(null)} className="px-3 py-1 text-xs bg-red-800 hover:bg-red-700 rounded text-white">Clear Image</button>
                                    </div>
                                )}
                                <p className="text-xs text-[var(--text-muted)] mt-1">Upload an image to use as the IDE background. (Max 2MB)</p>
                            </div>
                        </div>
                    </div>
                )}
                 {currentTab === 'workflows' && (
                    <div>
                        <h3 className="font-display text-lg font-bold uppercase tracking-wide mb-4">Workflow Model Assignments</h3>
                        <p className="text-sm text-[var(--text-muted)] mb-4">Assign specific models to different workflow steps for optimal performance. Leave empty to use the default model.</p>
                        <div className="space-y-6">
                            {WORKFLOWS.map(workflow => (
                                <div key={workflow.id}>
                                    <h4 className="text-lg font-semibold text-indigo-400 mb-2">{workflow.name}</h4>
                                    <div className="space-y-3 pl-4">
                                        {workflow.steps.map(step => (
                                            <div key={step.id}>
                                                <label className="dx-label block mb-2">{step.name}</label>
                                                 <select value={localWorkflowSettings[`${workflow.id}_${step.id}`] || ''} onChange={e => handleWorkflowChange(`${workflow.id}_${step.id}`, e.target.value)} className="dx-input">
                                                    <option value="">-- Use Default Model --</option>
                                                    {AVAILABLE_MODELS.map(model => <option key={model} value={model}>{model}</option>)}
                                                </select>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </main>
        <footer className="flex-shrink-0 flex items-center justify-end p-4 border-t border-[var(--border-primary)]">
            <button onClick={handleSave} className="dx-btn dx-btn-primary">
                Save & Close
            </button>
        </footer>
      </div>
    </div>
  );
};

export default SettingsDialog;