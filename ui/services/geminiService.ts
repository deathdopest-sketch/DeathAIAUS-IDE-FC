import { GoogleGenAI, Type, FunctionDeclaration, Chat, GenerateContentResponse } from "@google/genai";
import { FeasibilityReport, TaskPlan, ProjectPlan } from "../types";
import { FileNode } from "../components/FileTree";

if (!process.env.API_KEY) {
    throw new Error("API_KEY environment variable is not set");
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
const model = "gemini-2.5-flash";

// --- Tool Declarations ---
const listFilesTool: FunctionDeclaration = {
    name: "list_files",
    parameters: { type: Type.OBJECT, properties: {} },
    description: "List all files and folders in the current project workspace.",
};

const readFileTool: FunctionDeclaration = {
    name: "read_file",
    parameters: {
        type: Type.OBJECT,
        properties: { path: { type: Type.STRING, description: "The full path of the file to read." } },
        required: ["path"],
    },
    description: "Read the contents of a specific file in the workspace.",
};

const writeFileTool: FunctionDeclaration = {
    name: "write_file",
    parameters: {
        type: Type.OBJECT,
        properties: {
            path: { type: Type.STRING, description: "The full path of the file to write to. If the file doesn't exist, it will be created." },
            content: { type: Type.STRING, description: "The new content to write to the file." },
        },
        required: ["path", "content"],
    },
    description: "Write or overwrite the content of a file. Creates the file if it doesn't exist.",
};

const createFolderTool: FunctionDeclaration = {
    name: "create_folder",
    parameters: {
        type: Type.OBJECT,
        properties: { path: { type: Type.STRING, description: "The full path of the folder to create. e.g., 'src/components'" } },
        required: ["path"],
    },
    description: "Create a new folder (directory) in the project structure.",
};

const proposeChangePlanTool: FunctionDeclaration = {
    name: "propose_change_plan",
    parameters: {
        type: Type.OBJECT,
        properties: {
            goal: { type: Type.STRING, description: "A brief description of the overall goal." },
            steps: { type: Type.ARRAY, items: { type: Type.STRING }, description: "A list of steps to achieve the goal." },
            reasoning: { type: Type.STRING, description: "Why this plan is the correct approach." }
        },
        required: ["goal", "steps", "reasoning"],
    },
    description: "Propose a plan for a multi-step change before implementing it. Use this before making significant changes or creating multiple files.",
};

const lintFileTool: FunctionDeclaration = {
    name: "lint_file",
    parameters: {
        type: Type.OBJECT,
        properties: { path: { type: Type.STRING, description: "The full path of the file to lint." } },
        required: ["path"],
    },
    description: "Run a simulated linter on a file to check for errors, style issues, or potential bugs. Use this to verify your code.",
};


const allTools = {
    functionDeclarations: [
        listFilesTool,
        readFileTool,
        writeFileTool,
        createFolderTool,
        proposeChangePlanTool,
        lintFileTool,
    ]
};


// --- Chat Service ---
export function startChat(project: any, aiName?: string, aiPersonality?: string): Chat {
    const finalAiName = aiName?.trim() || 'an expert software developer';
    const finalAiPersonality = aiPersonality?.trim() || 'You are a helpful coding assistant.';

    const systemInstruction = `You are ${finalAiName}.
${finalAiPersonality}
- You are working on a project named "${project.name}" which uses the language "${project.language}".
- Pay close attention to the "CURRENT FOCUS" section which provides context about the user's current workflow, task plan, and recent terminal activity. This gives you hints about what the user is currently trying to achieve.
- The user will provide you with the current project file structure and the content of the active file.
- You may also be provided with RELEVANT CONTEXT from a knowledge base of other files in the project. Use this context to inform your response.
- Use the provided tools (list_files, read_file, write_file, create_folder, propose_change_plan, lint_file) to interact with the file system.
- Before using 'write_file' or 'create_folder' for any non-trivial change, you MUST first call 'propose_change_plan' to outline your strategy. The user will approve your plan before you proceed.
- When writing a file, always provide the full, complete file content, not just the changed parts.
- When asked to create a new component or module, create a folder for it first, then create the necessary files inside it (e.g., component file, index file, style file).
- After writing a new file, you can use the 'lint_file' tool to check your own work for errors.
- Be concise and helpful in your responses.`;
    
    return ai.chats.create({
        model,
        config: {
            systemInstruction,
            tools: [allTools]
        }
    });
}

export function generateDiff(path: string, originalContent: string, newContent: string): string {
    return `--- a/${path}\n+++ b/${path}\n... (diff preview of changes) ...\n\n${newContent}`;
}

export async function lintFile(path: string, content: string, language: string): Promise<string> {
    const prompt = `You are an expert code linter and quality assurance engineer for the ${language} language.
Analyze the following code from the file at path "${path}".
Identify any syntax errors, style violations, potential bugs, or areas for improvement.
If the code is perfect, respond with only the string "OK".
Otherwise, provide a concise list of the issues you found.

\`\`\`${language}
${content}
\`\`\`
`;
    const response = await ai.models.generateContent({ model, contents: prompt });
    return response.text;
}

// --- Knowledge Base Service Functions ---
export async function generateSummaryForCode(content: string, language: string): Promise<string> {
    if (!content.trim()) {
        return "This file is empty.";
    }
    const prompt = `Summarize the following ${language} code's primary purpose in one concise sentence. Focus on what it does or what it is for.
Do not describe the code structure, just its function.

\`\`\`${language}
${content}
\`\`\`
`;
    const response = await ai.models.generateContent({ model, contents: prompt });
    return response.text.trim();
}

// --- Feasibility Analysis ---
const feasibilitySchema = {
    type: Type.OBJECT,
    properties: {
        feasibility_score: { type: Type.NUMBER, description: "A score from 1-10 indicating feasibility. 1 is impossible, 10 is trivial." },
        complexity_level: { type: Type.STRING, description: "e.g., 'Low', 'Medium', 'High', 'Very High'" },
        estimated_time: { type: Type.STRING, description: "A rough time estimate, e.g., '2-3 days', '1 week'" },
        reality_check: { type: Type.STRING, description: "A brutally honest, slightly pessimistic assessment of the project's viability." },
        red_flags: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Critical issues or potential blockers." },
        warnings: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Potential challenges or things to watch out for." },
    },
    required: ["feasibility_score", "complexity_level", "estimated_time", "reality_check", "red_flags", "warnings"],
};

export async function analyzeFeasibility(description: string, language: string): Promise<FeasibilityReport> {
    const prompt = `Analyze the feasibility of the following project.
Project Description: "${description}"
Primary Language: ${language}
Provide a brutally honest analysis. Identify potential red flags and warnings.
Return the analysis in JSON format according to the provided schema.`;

    const response = await ai.models.generateContent({
        model,
        contents: prompt,
        config: {
            responseMimeType: "application/json",
            responseSchema: feasibilitySchema,
        },
    });

    const jsonText = response.text.trim();
    return JSON.parse(jsonText) as FeasibilityReport;
}

// --- Architect Mode ---
const projectPlanSchema = {
    type: Type.OBJECT,
    properties: {
        thought_process: { type: Type.STRING, description: "Your reasoning for the proposed structure and technologies." },
        file_structure: { type: Type.ARRAY, items: { type: Type.STRING }, description: "List of all files and folders to be created, like a file tree." },
        dependencies: { type: Type.ARRAY, items: { type: Type.STRING }, description: "List of required external libraries or packages (e.g., npm packages)." },
        next_steps: { type: Type.STRING, description: "A brief summary of the first few development steps after scaffolding." }
    },
    required: ["thought_process", "file_structure", "dependencies", "next_steps"],
};

export async function generateProjectPlan(description: string, language: string): Promise<ProjectPlan> {
    const prompt = `Act as a senior software architect. Analyze the following project idea and create a high-level project plan.
Project Description: "${description}"
Primary Language: ${language}
Your plan should outline the file structure, list key dependencies, and provide a brief thought process.
Return the plan in JSON format according to the provided schema.`;

    const response = await ai.models.generateContent({
        model,
        contents: prompt,
        config: {
            responseMimeType: "application/json",
            responseSchema: projectPlanSchema,
        },
    });
    const jsonText = response.text.trim();
    return JSON.parse(jsonText) as ProjectPlan;
}


// --- Project Scaffolding ---
const fileTreeSchema = {
    type: Type.ARRAY,
    items: {
        type: Type.OBJECT,
        properties: {
            name: { type: Type.STRING },
            path: { type: Type.STRING },
            content: { type: Type.STRING, description: "File content. Omit for directories." },
            children: { 
                type: Type.ARRAY, 
                // Using a generic object for items to avoid potential recursive schema issues with the API.
                items: { type: Type.OBJECT }, 
                description: "Child files/folders. Omit for files. Items should follow this same schema."
            },
        },
        required: ["name", "path"],
    },
};

export async function generateInitialProjectStructure(description: string, language: string, plan?: ProjectPlan): Promise<FileNode[]> {
    const planContext = plan ? `
---
ARCHITECT'S PLAN:
Thought Process: ${plan.thought_process}
File Structure: 
${plan.file_structure.join('\n')}
Dependencies: ${plan.dependencies.join(', ')}
---
` : '';

    const prompt = `Based on the following project description and architect's plan, generate a complete and logical initial file and folder structure.
Project Description: "${description}"
Primary Language: ${language}
${planContext}

- Implement the file structure as outlined in the plan.
- Include a README.md with a brief project summary.
- If it's a web project, include a basic index.html and a main script file (e.g., index.js, main.ts).
- If it's a backend project, include a main entry point file (e.g., main.go, app.py) and a simple example.
- Create a standard configuration file if applicable (e.g., package.json, go.mod, Cargo.toml) and include the dependencies from the plan.
- Organize files into logical folders (e.g., 'src', 'components', 'styles', 'api').
- Provide sensible boilerplate content for each file. The content should be minimal but functional.
- The 'path' for each node must be the full path from the root.
- Ensure the response is in JSON format matching the provided schema.`;

    const response = await ai.models.generateContent({
        model,
        contents: prompt,
        config: {
            responseMimeType: "application/json",
            responseSchema: fileTreeSchema,
        },
    });
    const jsonText = response.text.trim();
    return JSON.parse(jsonText) as FileNode[];
}

// --- Task Planning ---
const taskPlanSchema = {
    type: Type.OBJECT,
    properties: {
        title: { type: Type.STRING, description: "A concise title for the overall task." },
        tasks: {
            type: Type.ARRAY,
            items: {
                type: Type.OBJECT,
                properties: {
                    id: { type: Type.NUMBER },
                    description: { type: Type.STRING },
                    dependencies: { type: Type.ARRAY, items: { type: Type.NUMBER } },
                    estimatedTime: { type: Type.STRING, description: "e.g., '15 minutes', '2 hours'" },
                    status: { type: Type.STRING, description: "Should be 'pending' by default."}
                },
                required: ["id", "description", "dependencies", "estimatedTime", "status"],
            },
        },
    },
    required: ["title", "tasks"],
};

export async function generateTaskPlan(description: string): Promise<TaskPlan> {
     const prompt = `Create a detailed, step-by-step task plan for the following request: "${description}".
Break it down into manageable tasks. Include dependencies between tasks if any. Assign a unique ID to each task starting from 1.
Return the plan in JSON format according to the provided schema. The status of all tasks should be 'pending'.`;

    const response = await ai.models.generateContent({
        model,
        contents: prompt,
        config: {
            responseMimeType: "application/json",
            responseSchema: taskPlanSchema,
        },
    });
    
    const jsonText = response.text.trim();
    return JSON.parse(jsonText) as TaskPlan;
}