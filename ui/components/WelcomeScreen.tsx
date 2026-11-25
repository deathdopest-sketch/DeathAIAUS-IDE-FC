import React, { useState } from 'react';
import { Project, ProjectPlan } from '../types';
import { FileNode } from './FileTree';
import { ALL_LANGUAGES, AVAILABLE_MODELS } from '../constants';
import { generateInitialProjectStructure, generateProjectPlan } from '../services/pythonBackendService';
import RobotIcon from './icons/RobotIcon';
import SkullIcon from './icons/SkullIcon';
import SouthernCross from './ui/SouthernCross';
import { BloodDrips, CorruptText, TypeLog, WatchingEye } from './ui/haunt';

interface WelcomeScreenProps {
  onProjectCreate: (project: Project, files: FileNode[]) => void;
  addToast: (message: string, type?: 'success' | 'error' | 'info') => void;
}

type Stage = 'input' | 'planning' | 'review' | 'building';

const asciiArt = `
▓█████▄ ▓█████  ▄▄▄      ▄▄▄█████▓ ██░ ██  ▄▄▄       ██▓ ▄▄▄       █    ██   ██████ 
▒██▀ ██▌▓█   ▀ ▒████▄    ▓  ██▒ ▓▒▓██░ ██▒▒████▄    ▓██▒▒████▄     ██  ▓██▒▒██    ▒ 
░██   █▌▒███   ▒██  ▀█▄  ▒ ▓██░ ▒░▒██▀▀██░▒██  ▀█▄  ▒██▒▒██  ▀█▄  ▓██  ▒██░░ ▓██▄   
░▓█▄   ▌▒▓█  ▄ ░██▄▄▄▄██ ░ ▓██▓ ░ ░▓█ ░██ ░██▄▄▄▄██ ░██░░██▄▄▄▄██ ▓▓█  ░██░  ▒   ██▒
░▒████▓ ░▒████▒ ▓█   ▓██▒  ▒██▒ ░ ░▓█▒░██▓ ▓█   ▓██▒░██░ ▓█   ▓██▒▒▒█████▓ ▒██████▒▒
 ▒▒▓  ▒ ░░ ▒░ ░ ▒▒   ▓▒█░  ▒ ░░    ▒ ░░▒░▒ ▒▒   ▓▒█░░▓   ▒▒   ▓▒█░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░
 ░ ▒  ▒  ░ ░  ░  ▒   ▒▒ ░    ░     ▒ ░▒░ ░  ▒   ▒▒ ░ ▒ ░  ▒   ▒▒ ░░░▒░ ░ ░ ░ ░▒  ░ ░
 ░ ░  ░    ░     ░   ▒     ░       ░  ░░ ░  ░   ▒    ▒ ░  ░   ▒    ░░░ ░ ░ ░  ░  ░  
   ░       ░  ░      ░  ░          ░  ░  ░      ░  ░ ░        ░  ░   ░           ░  
 ░                                                                                  
`;

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onProjectCreate, addToast }) => {
  const [project, setProject] = useState<Partial<Project>>({ language: 'JavaScript' });
  const [stage, setStage] = useState<Stage>('input');
  const [plan, setPlan] = useState<ProjectPlan | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!project.name?.trim() || !project.description?.trim()) {
      addToast('Project name and description are required.', 'error');
      return;
    }
    setError(null);
    setStage('planning');
    addToast('AI Architect is designing a plan...', 'info');

    try {
      const newPlan = await generateProjectPlan(project.description, project.language || 'JavaScript');
      setPlan(newPlan);
      setStage('review');
      addToast('Project plan is ready for your review.', 'success');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred during planning.";
      setError(errorMessage);
      setStage('input');
    }
  };

  const handleBuild = async () => {
    if (!project.name || !project.description || !project.language || !plan) return;
    setError(null);
    setStage('building');
    addToast('Generating project structure... This may take a moment.', 'info');
    
    try {
      const fullProject: Project = { ...project, plan } as Project;
      const generatedFiles = await generateInitialProjectStructure(fullProject.description!, fullProject.language, plan);
      onProjectCreate(fullProject, generatedFiles);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred during project generation.";
      setError(errorMessage);
      setStage('review');
    }
  };
  
  const isLoading = stage === 'planning' || stage === 'building';
  const localModels = AVAILABLE_MODELS.filter(m => m.endsWith('.gguf')).length;

  return (
    <div className="relative h-screen overflow-y-auto bg-[var(--bg-primary)] text-[var(--text-primary)]">
      {/* backdrop: red bloom + grid */}
      <div className="pointer-events-none absolute inset-0" aria-hidden="true"
        style={{
          background:
            'radial-gradient(60% 50% at 20% 30%, rgb(var(--c-blood-base) / .18), transparent 70%),' +
            'radial-gradient(40% 40% at 90% 90%, rgb(var(--c-signal-base) / .04), transparent 70%),' +
            'linear-gradient(rgb(var(--c-ash-base) / .25) 1px, transparent 1px) 0 0 / 100% 48px,' +
            'linear-gradient(90deg, rgb(var(--c-ash-base) / .25) 1px, transparent 1px) 0 0 / 48px 100%',
        }}
      />
      <BloodDrips count={22} maxLen={130} />

      <div className="relative min-h-full max-w-7xl mx-auto px-4 sm:px-10 lg:px-16 py-16 grid lg:grid-cols-[1.2fr_1fr] gap-16 xl:gap-24 items-center">
        {/* ---------- Hero ---------- */}
        <section className="min-w-0">
          <div className="flex items-center gap-3 mb-10">
            <SkullIcon className="w-6 h-6 text-blood-light" />
            <span className="dx-label">DeathAI Australia // Local-first AI IDE</span>
          </div>

          <div className="flex items-center gap-8">
          <div className="overflow-hidden dx-tear min-w-0">
            <pre
              className="glitch font-mono text-blood-light leading-[1.05] text-[5px] sm:text-[7px] xl:text-[8px] whitespace-pre select-none"
              data-text={asciiArt}
              aria-label="DeathAIAUS"
            >{asciiArt}</pre>
          </div>
          <WatchingEye size={88} className="hidden sm:block flex-shrink-0" />
          </div>

          <h1 className="mt-12 font-display font-bold uppercase text-3xl sm:text-5xl leading-[1.05] tracking-wide">
            It already knows<br />
            what you're <span className="text-blood-light dx-split"><CorruptText text="going to build." /></span>
          </h1>
          <p className="mt-6 max-w-lg text-base leading-relaxed text-[var(--text-secondary)]">
            A brutally honest AI architect, running on your own metal. Local models. No telemetry. Nothing leaves this machine. <span className="text-[var(--text-muted)]">Nothing.</span>
          </p>

          <dl className="mt-12 grid grid-cols-3 max-w-lg border border-[var(--border-primary)] divide-x divide-[var(--border-primary)]">
            <div className="px-5 py-4"><dt className="dx-label">Local models</dt><dd className="font-mono text-2xl text-bone mt-2">{String(localModels).padStart(2, '0')}</dd></div>
            <div className="px-5 py-4"><dt className="dx-label">Telemetry</dt><dd className="font-mono text-2xl text-phosphor mt-2">NIL</dd></div>
            <div className="px-5 py-4"><dt className="dx-label">Survivors</dt><dd className="font-mono text-2xl text-blood-light mt-2 dx-flicker">00</dd></div>
          </dl>

          <TypeLog className="mt-10 max-w-lg" />

          <div className="mt-12 flex items-center gap-4 text-ochre">
            <SouthernCross className="w-9 h-9" />
            <span className="dx-label !text-ochre">Built under the Southern Cross</span>
          </div>
        </section>

        {/* ---------- Console ---------- */}
        <section className="dx-dialog p-8 sm:p-10 min-w-0">
          <div className="flex items-center justify-between mb-8">
            <span className="dx-label">{stage === 'review' ? '02 // Review' : stage === 'input' ? '01 // Define' : '>> Processing'}</span>
            <span className="dx-tag text-blood-light">Thanatos</span>
          </div>

          {error && !isLoading && (
            <div role="alert" className="mb-8 border border-blood/60 border-l-2 border-l-blood-light bg-blood-deep/40 px-4 py-3">
              <div className="flex items-start justify-between gap-4">
                <p className="dx-label !text-blood-light">The summoning failed</p>
                <button onClick={() => setError(null)} className="dx-label hover:!text-bone" aria-label="Dismiss error">Dismiss</button>
              </div>
              <p className="mt-2 text-sm text-[var(--text-primary)] leading-relaxed">{error}</p>
            </div>
          )}

          {stage === 'input' && (
            <form onSubmit={handlePlan} className="space-y-7">
              <div>
                <h2 className="font-display text-3xl font-bold uppercase tracking-wide dx-caret">Choose your grave</h2>
                <p className="mt-2 text-sm text-[var(--text-secondary)]">Name it. Describe it. Thanatos will decide if it survives.</p>
              </div>
              <div>
                <label htmlFor="projectName" className="dx-label block mb-3">Project name</label>
                <input type="text" id="projectName" value={project.name ?? ''} onChange={(e) => setProject(p => ({...p, name: e.target.value}))} placeholder="e.g. reaper-api" className="dx-input" required />
              </div>
              <div>
                <label htmlFor="projectLang" className="dx-label block mb-3">Primary language</label>
                <select id="projectLang" value={project.language ?? 'JavaScript'} onChange={(e) => setProject(p => ({...p, language: e.target.value}))} className="dx-input">
                  {ALL_LANGUAGES.map(lang => <option key={lang} value={lang}>{lang}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="projectDesc" className="dx-label block mb-3">Description</label>
                <textarea id="projectDesc" value={project.description ?? ''} onChange={(e) => setProject(p => ({...p, description: e.target.value}))} placeholder="Describe what you want to build. Be detailed — vague in, vague out." rows={5} className="dx-input resize-y" required />
              </div>
              <button type="submit" disabled={isLoading} className="dx-btn dx-btn-primary dx-btn-lg w-full !mt-10">
                <RobotIcon className="w-4 h-4" />
                Summon the architect
              </button>
            </form>
          )}

          {(stage === 'planning' || stage === 'building') && (
            <div className="py-12 text-center">
              <div className="mx-auto w-16 h-16 relative dx-tear" aria-hidden="true">
                <SkullIcon className="absolute inset-0 w-16 h-16 text-signal opacity-70 translate-x-[3px]" />
                <SkullIcon className="absolute inset-0 w-16 h-16 text-blood-light animate-pulse" />
              </div>
              <h2 className="mt-6 font-display text-2xl font-bold uppercase tracking-wide dx-caret">
                {stage === 'planning' ? 'Architect is thinking' : 'Building your project'}
              </h2>
              <p className="mt-2 text-[var(--text-secondary)] text-sm">
                {stage === 'planning' ? 'Drafting the blueprint. Hold tight.' : 'Generating files and boilerplate. This might take a moment.'}
              </p>
              <div className="mt-6 h-1 w-full bg-[var(--border-secondary)] overflow-hidden">
                <div className="h-full w-1/3 bg-blood shadow-bleed dx-scan" />
              </div>
            </div>
          )}

          {stage === 'review' && plan && (
            <div>
              <h2 className="font-display text-2xl font-bold uppercase tracking-wide mb-4">Architect's plan</h2>
              <div className="space-y-5 max-h-[55vh] overflow-y-auto pr-2">
                <section>
                  <h3 className="dx-label mb-1">Thought process</h3>
                  <p className="text-sm text-[var(--text-secondary)] whitespace-pre-wrap">{plan.thought_process}</p>
                </section>
                <section>
                  <h3 className="dx-label mb-1">File structure</h3>
                  <pre className="text-xs text-signal bg-[var(--bg-primary)] border border-[var(--border-secondary)] border-l-2 border-l-signal p-3 overflow-x-auto"><code>{plan.file_structure.join('\n')}</code></pre>
                </section>
                <section>
                  <h3 className="dx-label mb-2">Dependencies</h3>
                  <div className="flex flex-wrap gap-1.5">
                    {plan.dependencies.length ? plan.dependencies.map(d => <span key={d} className="dx-tag text-[var(--text-secondary)]">{d}</span>) : <span className="text-sm text-[var(--text-muted)]">None</span>}
                  </div>
                </section>
                <section>
                  <h3 className="dx-label mb-1">Next steps</h3>
                  <p className="text-sm text-[var(--text-secondary)] whitespace-pre-wrap">{plan.next_steps}</p>
                </section>
              </div>
              <div className="flex justify-end gap-2 mt-6">
                <button onClick={() => setStage('input')} className="dx-btn">Back</button>
                <button onClick={handleBuild} className="dx-btn dx-btn-primary">Approve &amp; build</button>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default WelcomeScreen;
