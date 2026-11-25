import React from 'react';
import XIcon from './icons/XIcon';

interface FeaturesListProps {
  onClose: () => void;
}

const featuresText = `
# DeathAIAUS IDE F.C - Complete Features List

## Overview
DeathAIAUS IDE F.C (Feasibility Check Edition) is a professional AI-powered development environment that combines traditional IDE functionality with advanced AI capabilities. Built with Python and Tkinter, it provides a modern, efficient coding experience with intelligent assistance.

---

## Core IDE Features

### 1. **Multi-File Editor System**
- **Tabbed Interface**: Open multiple files simultaneously with intuitive tab management
- **Syntax Highlighting**: Full syntax highlighting for Python, JavaScript, HTML, CSS, and more
... and more.

---
## AI-Powered Features

### 4. **AI Chat Interface**
- **Persistent Sidebar**: Always-available AI assistant in a dedicated panel
- **Context-Aware Responses**: AI understands your current file and project context
... and more.

---
## ASCII Art Branding
\`\`\`
▓█████▄ ▓█████ ▄▄▄      ▄▄▄█████▓ ██░ ██  ▄▄▄       ██▓ ▄▄▄       █    ██   ██████ 
▒██▀ ██▌▓█   ▀▒████▄    ▓  ██▒ ▓▒▓██░ ██▒▒████▄    ▓██▒▒████▄     ██  ▓██▒▒██    ▒ 
░██   █▌▒███  ▒██  ▀█▄  ▒ ▓██░ ▒░▒██▀▀██░▒██  ▀█▄  ▒██▒▒██  ▀█▄  ▓██  ▒██░░ ▓██▄   
░▓█▄   ▌▒▓█  ▄░██▄▄▄▄██ ░ ▓██▓ ░ ░▓█ ░██ ░██▄▄▄▄██ ░██░░██▄▄▄▄██ ▓▓█  ░██░  ▒   ██▒
░▒████▓ ░▒████▒▓█   ▓██▒  ▒██▒ ░ ░▓█▒░██▓ ▓█   ▓██▒░██░ ▓█   ▓██▒▒▒█████▓ ▒██████▒▒
 ▒▒▓  ▒ ░░ ▒░ ░▒▒   ▓▒█░  ▒ ░░    ▒ ░░▒░▒ ▒▒   ▓▒█░░▓   ▒▒   ▓▒█░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░
 ░ ▒  ▒  ░ ░  ░ ▒   ▒▒ ░    ░     ▒ ░▒░ ░  ▒   ▒▒ ░ ▒ ░  ▒   ▒▒ ░░░▒░ ░ ░ ░ ░▒  ░ ░
 ░ ░  ░    ░     ░   ▒     ░       ░  ░░ ░  ░   ▒    ▒ ░  ░   ▒    ░░░ ░ ░ ░  ░  ░  
   ░       ░  ░     ░  ░          ░  ░  ░      ░  ░ ░        ░  ░   ░           ░  
 ░                                                                               
\`\`\`
---

*© DeathAIAUS 2025 - Powered by Death's Pantheon AI Models*
`;


const FeaturesList: React.FC<FeaturesListProps> = ({ onClose }) => {
  return (
    <div className="dx-backdrop">
      <div className="dx-dialog w-full max-w-4xl h-[90vh]  flex flex-col p-4 text-[var(--text-primary)]">
        <header className="flex items-center justify-between pb-4 border-b border-[var(--border-primary)]">
          <h2 className="font-display text-xl font-bold uppercase tracking-wide text-blood-light">🚀 IDE Features</h2>
          <button onClick={onClose} className="text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
            <XIcon className="w-8 h-8" />
          </button>
        </header>
        <main className="flex-grow mt-4 overflow-y-auto bg-[var(--bg-primary)] p-4 rounded font-mono text-sm">
            <pre className="whitespace-pre-wrap">
                {featuresText.replace(/```\n([\s\S]*?)\n```/g, (match, p1) => p1)}
            </pre>
        </main>
      </div>
    </div>
  );
};

export default FeaturesList;