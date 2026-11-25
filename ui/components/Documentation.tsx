import React from 'react';
import XIcon from './icons/XIcon';

interface DocumentationProps {
  onClose: () => void;
}

const docText = `
================================================================================
                    REAPGATE & DEATHAIAUS COMPLETE DOCUMENTATION
================================================================================

TABLE OF CONTENTS:
1. OVERVIEW & PHILOSOPHY
2. DEATHAIAUS IDE FC - COMPLETE BREAKDOWN
3. REAPGATE BACKEND - FULL TECHNICAL SPECIFICATION
4. DEATH'S PANTHEON MODEL SYSTEM - COMPREHENSIVE GUIDE
5. TECHNICAL ARCHITECTURE - DETAILED ANALYSIS
...and more.

================================================================================
1. OVERVIEW
================================================================================

DEATHAIAUS IDE FC is a comprehensive AI-powered integrated development environment
designed specifically for DeathAIAUS models. It combines a modern Cursor.ink-style
interface with a custom Go-based inference backend called ReapGate.

Key Features:
- Multi-file tab system with syntax highlighting
- AI Chat sidebar for real-time assistance
- AI Composer for code generation
- Smart Model Manager for on-demand model loading
- Death's Pantheon model organization system
- Built-in terminal, file explorer, and project management
- Workflow-based AI model assignment
- Session memory and error recovery
- Branded launcher with splash screen

================================================================================
3. REAPGATE BACKEND
================================================================================

REAPGATE is a custom Go-based inference server designed specifically for
DeathAIAUS IDE FC. It replaces LM Studio with a purpose-built solution.

TECHNICAL SPECIFICATIONS:
- Language: Go 1.21 (Simulated in this React version)
- Web Framework: Gin-Gonic
- AI Backend: go-llama.cpp (Go bindings for llama.cpp)
- Architecture: RESTful API server
- Port: 7777
- Model Format: GGUF (GGML Universal Format)

API ENDPOINTS:
- GET  /health                    - Health check
- GET  /v1/models                 - List available models
- POST /v1/chat/completions       - Chat completions (This is what the app uses)
... and more.

================================================================================
4. DEATH'S PANTHEON MODEL SYSTEM
================================================================================

Death's Pantheon is a custom naming and organization scheme for AI models,
inspired by various mythologies and designed for DeathAIAUS branding.

MODEL NAMING CONVENTION:
Format: [DEITY]-DeathAIAUS-[SIZE]B-[QUANTIZATION].gguf

EXAMPLE MODELS:
- THANATOS-DeathAIAUS-22B-Q4_K_M.gguf
- ANUBIS-DeathAIAUS-1.2B-Q8_0.gguf
- MORRIGAN-DeathAIAUS-7B-Q4_0.gguf

================================================================================
7. INSTALLATION & SETUP
================================================================================

This is a web-based React application powered by the Gemini API. The ReapGate
backend and Python/Go components described are part of the project's lore and
are simulated in this version.

PREREQUISITES:
- A modern web browser.
- An internet connection.
- A valid Gemini API key set in the environment variables.

================================================================================
9. USAGE GUIDE
================================================================================

STARTING THE IDE:
1. Open the web page.
2. Enter a project name and select a language.

AI FEATURES:
- Model Manager: Access via Settings button.
- Workflow Config: Access via Settings button.
- Pantheon Viewer: The model list uses Pantheon names.
- Backend Status: Indicated in the top toolbar.

================================================================================
END OF DOCUMENTATION
================================================================================
`;

const Documentation: React.FC<DocumentationProps> = ({ onClose }) => {
  return (
    <div className="dx-backdrop">
      <div className="dx-dialog w-full max-w-4xl h-[90vh]  flex flex-col p-4 text-[var(--text-primary)]">
        <header className="flex items-center justify-between pb-4 border-b border-[var(--border-primary)]">
          <h2 className="font-display text-xl font-bold uppercase tracking-wide text-blood-light">📄 Project Documentation</h2>
          <button onClick={onClose} className="text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
            <XIcon className="w-8 h-8" />
          </button>
        </header>
        <main className="flex-grow mt-4 overflow-y-auto bg-[var(--bg-primary)] p-4 rounded font-mono text-sm">
            <pre className="whitespace-pre-wrap">
                {docText}
            </pre>
        </main>
      </div>
    </div>
  );
};

export default Documentation;