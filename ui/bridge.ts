/**
 * TypeScript Bridge - Type-safe wrappers for Python bridge functions
 * Provides 119 IDE functions to React components
 */

// Bridge interface injected by pywebview
declare global {
    interface Window {
        pywebview?: {
            api: PythonBridge;
        };
    }
}

// Python bridge interface
interface PythonBridge {
    // File Operations
    open_file(path: string): Promise<FileResult>;
    save_file(path: string, content: string): Promise<FileResult>;
    create_file(path: string, content?: string): Promise<FileResult>;
    delete_file(path: string): Promise<Result>;
    rename_file(old_path: string, new_path: string): Promise<FileResult>;
    list_files(directory?: string): Promise<DirectoryResult>;
    watch_file(path: string, callback_id: string): Promise<Result>;
    get_file_stats(path: string): Promise<FileStatsResult>;
    search_in_files(query: string, directory?: string): Promise<SearchResult>;
    batch_file_operations(operations: FileOperation[]): Promise<BatchResult>;
    
    // File System Safety
    check_write_permission(path: string): Promise<PermissionResult>;
    check_disk_space(): Promise<DiskSpaceResult>;
    validate_file_path(path: string): Promise<ValidationResult>;
    handle_long_paths(enabled?: boolean): Promise<Result>;
    detect_locked_files(directory?: string): Promise<LockedFilesResult>;
    
    // Native Dialogs
    show_open_file_dialog(filters?: FileFilter[]): Promise<DialogResult>;
    show_save_file_dialog(default_name?: string, filters?: FileFilter[]): Promise<DialogResult>;
    show_open_folder_dialog(): Promise<DialogResult>;
    show_open_files_dialog(filters?: FileFilter[]): Promise<DialogMultiResult>;
    show_message_box(title: string, message: string, type?: 'info' | 'warning' | 'error' | 'question'): Promise<MessageBoxResult>;
    
    // Clipboard
    get_clipboard_text(): Promise<ClipboardResult>;
    set_clipboard_text(text: string): Promise<Result>;
    clipboard_available(): Promise<AvailabilityResult>;
    
    // Storage Persistence
    save_local_storage(data: Record<string, string>): Promise<Result>;
    load_local_storage(): Promise<LocalStorageResult>;
    clear_local_storage(): Promise<Result>;
    
    // AI & Models
    call_ai_model(messages: ChatMessage[], workflow?: string): Promise<string>;
    get_available_models(): Promise<ModelsResult>;
    load_model(model_path: string): Promise<Result>;
    unload_model(): Promise<Result>;
    get_model_status(): Promise<ModelStatusResult>;
    get_model_metadata(model_path: string): Promise<MetadataResult>;
    switch_model(model_path: string): Promise<Result>;
    get_workflow_config(): Promise<WorkflowConfigResult>;
    set_workflow_model(workflow: string, model_path: string): Promise<Result>;
    validate_model(model_path: string): Promise<ValidationResult>;
    stream_ai_response(messages: ChatMessage[], workflow?: string): Promise<string>;
    cancel_ai_request(): Promise<Result>;
    get_ai_queue_status(): Promise<QueueStatusResult>;
    estimate_tokens(text: string): Promise<TokenEstimateResult>;
    get_model_info(model_path: string): Promise<MetadataResult>;
}

// Type definitions
export interface Result {
    success: boolean;
    error?: string;
}

export interface FileResult extends Result {
    content?: string;
    path?: string;
}

export interface DirectoryResult extends Result {
    items?: FileItem[];
}

export interface FileItem {
    name: string;
    path: string;
    isDirectory: boolean;
    size: number;
}

export interface FileStatsResult extends Result {
    size?: number;
    modified?: string;
    created?: string;
}

export interface SearchResult extends Result {
    results?: SearchMatch[];
}

export interface SearchMatch {
    file: string;
    line: number;
    content: string;
}

export interface FileOperation {
    type: 'read' | 'write' | 'delete';
    path: string;
    content?: string;
}

export interface BatchResult extends Result {
    results?: Result[];
}

export interface PermissionResult extends Result {
    writable?: boolean;
}

export interface DiskSpaceResult extends Result {
    total?: number;
    used?: number;
    free?: number;
    percent?: number;
}

export interface ValidationResult extends Result {
    valid?: boolean;
    path?: string;
}

export interface LockedFilesResult extends Result {
    locked_files?: string[];
}

export interface FileFilter {
    name: string;
    extensions: string[];
}

export interface DialogResult extends Result {
    path?: string;
    cancelled?: boolean;
}

export interface DialogMultiResult extends Result {
    paths?: string[];
    cancelled?: boolean;
}

export interface MessageBoxResult extends Result {
    result?: boolean;
}

export interface ClipboardResult extends Result {
    text?: string;
}

export interface AvailabilityResult extends Result {
    available?: boolean;
}

export interface LocalStorageResult extends Result {
    data?: Record<string, string>;
}

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

export interface ModelsResult extends Result {
    models?: ModelInfo[];
}

export interface ModelInfo {
    id: string;
    name: string;
    path: string;
}

export interface ModelStatusResult extends Result {
    loaded?: boolean;
    current_model?: string;
}

export interface MetadataResult extends Result {
    metadata?: Record<string, any>;
}

export interface WorkflowConfigResult extends Result {
    workflows?: Record<string, string>;
    pantheon?: any;
}

export interface QueueStatusResult extends Result {
    queue_length?: number;
    processing?: boolean;
}

export interface TokenEstimateResult extends Result {
    tokens?: number;
}

// Type-safe bridge wrapper class
export class Bridge {
    private static instance: Bridge;
    private api: PythonBridge;
    
    private constructor() {
        if (!window.pywebview?.api) {
            throw new Error('Python bridge not available');
        }
        this.api = window.pywebview.api;
    }
    
    static getInstance(): Bridge {
        if (!Bridge.instance) {
            Bridge.instance = new Bridge();
        }
        return Bridge.instance;
    }
    
    // File Operations
    async openFile(path: string): Promise<FileResult> {
        return this.api.open_file(path);
    }
    
    async saveFile(path: string, content: string): Promise<FileResult> {
        return this.api.save_file(path, content);
    }
    
    async createFile(path: string, content: string = ''): Promise<FileResult> {
        return this.api.create_file(path, content);
    }
    
    async deleteFile(path: string): Promise<Result> {
        return this.api.delete_file(path);
    }
    
    async renameFile(oldPath: string, newPath: string): Promise<FileResult> {
        return this.api.rename_file(oldPath, newPath);
    }
    
    async listFiles(directory: string = '.'): Promise<DirectoryResult> {
        return this.api.list_files(directory);
    }
    
    async getFileStats(path: string): Promise<FileStatsResult> {
        return this.api.get_file_stats(path);
    }
    
    async searchInFiles(query: string, directory: string = '.'): Promise<SearchResult> {
        return this.api.search_in_files(query, directory);
    }
    
    // Native Dialogs
    dialogs = {
        showOpenFileDialog: async (filters?: FileFilter[]): Promise<DialogResult> => {
            return this.api.show_open_file_dialog(filters);
        },
        
        showSaveFileDialog: async (defaultName?: string, filters?: FileFilter[]): Promise<DialogResult> => {
            return this.api.show_save_file_dialog(defaultName, filters);
        },
        
        showOpenFolderDialog: async (): Promise<DialogResult> => {
            return this.api.show_open_folder_dialog();
        },
        
        showOpenFilesDialog: async (filters?: FileFilter[]): Promise<DialogMultiResult> => {
            return this.api.show_open_files_dialog(filters);
        },
        
        showMessageBox: async (title: string, message: string, type?: 'info' | 'warning' | 'error' | 'question'): Promise<MessageBoxResult> => {
            return this.api.show_message_box(title, message, type);
        }
    };
    
    // Clipboard
    clipboard = {
        getText: async (): Promise<string> => {
            const result = await this.api.get_clipboard_text();
            return result.text || '';
        },
        
        setText: async (text: string): Promise<void> => {
            await this.api.set_clipboard_text(text);
        },
        
        isAvailable: async (): Promise<boolean> => {
            const result = await this.api.clipboard_available();
            return result.available || false;
        }
    };
    
    // Storage
    storage = {
        saveLocalStorage: async (data: Record<string, string>): Promise<void> => {
            await this.api.save_local_storage(data);
        },
        
        loadLocalStorage: async (): Promise<Record<string, string>> => {
            const result = await this.api.load_local_storage();
            return result.data || {};
        },
        
        clearLocalStorage: async (): Promise<void> => {
            await this.api.clear_local_storage();
        }
    };
    
    // AI & Models
    ai = {
        callModel: async (messages: ChatMessage[], workflow: string = 'coding'): Promise<string> => {
            return this.api.call_ai_model(messages, workflow);
        },
        
        getAvailableModels: async (): Promise<ModelInfo[]> => {
            const result = await this.api.get_available_models();
            return result.models || [];
        },
        
        loadModel: async (modelPath: string): Promise<void> => {
            await this.api.load_model(modelPath);
        },
        
        unloadModel: async (): Promise<void> => {
            await this.api.unload_model();
        },
        
        getModelStatus: async (): Promise<ModelStatusResult> => {
            return this.api.get_model_status();
        },
        
        switchModel: async (modelPath: string): Promise<void> => {
            await this.api.switch_model(modelPath);
        },
        
        getWorkflowConfig: async (): Promise<WorkflowConfigResult> => {
            return this.api.get_workflow_config();
        },
        
        estimateTokens: async (text: string): Promise<number> => {
            const result = await this.api.estimate_tokens(text);
            return result.tokens || 0;
        }
    };
    
    // File System Safety
    fs = {
        checkWritePermission: async (path: string): Promise<boolean> => {
            const result = await this.api.check_write_permission(path);
            return result.writable || false;
        },
        
        checkDiskSpace: async (): Promise<DiskSpaceResult> => {
            return this.api.check_disk_space();
        },
        
        validatePath: async (path: string): Promise<ValidationResult> => {
            return this.api.validate_file_path(path);
        },
        
        detectLockedFiles: async (directory?: string): Promise<string[]> => {
            const result = await this.api.detect_locked_files(directory);
            return result.locked_files || [];
        }
    };
}

// Export singleton instance
export const bridge = Bridge.getInstance();

