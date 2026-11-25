import { callModel } from './pythonBackendService';
import { FileNode } from '../components/FileTree';
import { KnowledgeBaseData, KnowledgeBaseEntry } from '../types';
import { generateSummaryForCode } from './pythonBackendService';

// Bridge interface
declare global {
    interface Window {
        pywebview?: {
            api: any;
        };
    }
}

export class KnowledgeBaseService {
    private knowledgeBase: KnowledgeBaseData = new Map();

    private flattenFileTree(nodes: FileNode[]): FileNode[] {
        let files: FileNode[] = [];
        for (const node of nodes) {
            if (node.children) {
                files = files.concat(this.flattenFileTree(node.children));
            } else {
                files.push(node);
            }
        }
        return files;
    }

    async indexProject(files: FileNode[], language: string): Promise<void> {
        this.knowledgeBase.clear();
        const allFiles = this.flattenFileTree(files);

        // Process files in parallel batches to avoid overwhelming the API
        const batchSize = 5;
        for (let i = 0; i < allFiles.length; i += batchSize) {
            const batch = allFiles.slice(i, i + batchSize);
            await Promise.all(batch.map(async file => {
                if (file.content !== undefined) {
                    const summary = await generateSummaryForCode(file.content, language);
                    this.knowledgeBase.set(file.path, { summary, content: file.content });
                }
            }));
        }
    }

    async search(query: string, limit: number = 3): Promise<{path: string, content: string}[]> {
        if (this.knowledgeBase.size === 0) {
            return [];
        }

        const summaries = Array.from(this.knowledgeBase.entries()).map(([path, entry]) => {
            return `- File: "${path}"\n  Summary: ${entry.summary}`;
        }).join('\n');

        const prompt = `Based on the user's query, identify the most relevant files from the following list.
Return ONLY a comma-separated list of the top ${limit} most relevant file paths, and nothing else.
Do not add any explanation or formatting.

Example response: src/components/Button.tsx,src/styles/main.css

---
User Query: "${query}"
---
File Summaries:
${summaries}
---

Most relevant file paths:`;

        const response = await callModel(
            [{ role: 'user', content: prompt }],
            'coding'
        );
        const relevantPaths = response.trim().split(',').map(p => p.trim()).filter(Boolean);
        
        const results = relevantPaths
            .map(path => {
                const entry = this.knowledgeBase.get(path);
                return entry ? { path, content: entry.content } : null;
            })
            .filter((item): item is {path: string, content: string} => item !== null);
            
        return results;
    }

    getKnowledgeBase(): KnowledgeBaseData {
        return this.knowledgeBase;
    }
}
