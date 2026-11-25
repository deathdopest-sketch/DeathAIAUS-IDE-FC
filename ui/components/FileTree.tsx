
import React, { useState, useEffect, useRef } from 'react';
// Fix: Import FileNode from the central types file.
import { ContextMenuData, CreationInputData, FileNode } from '../types';
import ChevronDownIcon from './icons/ChevronDownIcon';
import ContextMenu from './ContextMenu';

// Fix: The FileNode interface has been moved to types.ts to avoid circular dependencies.

interface FileTreeProps {
  files: FileNode[];
  onFileOpen: (file: FileNode) => void;
  contextMenu: ContextMenuData | null;
  setContextMenu: (data: ContextMenuData | null) => void;
  creationInput: CreationInputData | null;
  setCreationInput: (data: CreationInputData | null) => void;
  onFileCreate: (path: string) => void;
  onFolderCreate: (path: string) => void;
}

const CreationInput: React.FC<{
    type: 'file' | 'folder';
    parentPath: string;
    onCancel: () => void;
    onCreate: (path: string) => void;
    level: number;
}> = ({ type, parentPath, onCancel, onCreate, level }) => {
    const [name, setName] = useState('');
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const handleSubmit = () => {
        if (name.trim()) {
            const newPath = parentPath ? `${parentPath}/${name.trim()}` : name.trim();
            onCreate(newPath);
        }
        onCancel();
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSubmit();
        } else if (e.key === 'Escape') {
            onCancel();
        }
    };

    return (
        <div style={{ paddingLeft: `${level * 1.25}rem` }} className="p-1">
            <input
                ref={inputRef}
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyDown={handleKeyDown}
                onBlur={onCancel}
                placeholder={`New ${type} name...`}
                className="dx-input !py-1 !text-xs"
                aria-label={`New ${type} name`}
            />
        </div>
    );
};

const FileNodeItem: React.FC<{ 
    node: FileNode; 
    onFileOpen: (file: FileNode) => void; 
    level: number; 
    setContextMenu: (data: ContextMenuData) => void;
    creationInput: CreationInputData | null;
    setCreationInput: (data: CreationInputData | null) => void;
    onFileCreate: (path: string) => void;
    onFolderCreate: (path: string) => void;
}> = ({ node, onFileOpen, level, setContextMenu, creationInput, setCreationInput, onFileCreate, onFolderCreate }) => {
  const [isOpen, setIsOpen] = useState(true);
  const isDirectory = !!node.children;

  const handleToggle = () => {
    if (isDirectory) {
      setIsOpen(!isOpen);
    } else {
      onFileOpen(node);
    }
  };
  
  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setContextMenu({ x: e.clientX, y: e.clientY, targetPath: node.path });
  };

  return (
    <div>
      <div
        className="group relative flex items-center h-8 pr-3 cursor-pointer font-mono text-[12.5px] hover:bg-[var(--bg-hover)] hover:text-bone border-l-2 border-transparent hover:border-blood-light"
        style={{ paddingLeft: `${1 + level * 1}rem` }}
        onClick={handleToggle}
        onContextMenu={isDirectory ? handleContextMenu : undefined}
      >
        {isDirectory
          ? <ChevronDownIcon className={`w-3 h-3 mr-2 flex-shrink-0 text-blood-light transition-transform ${isOpen ? 'rotate-0' : '-rotate-90'}`} aria-hidden="true" />
          : <span className="w-3 mr-2 flex-shrink-0 text-center text-[var(--text-muted)] group-hover:text-blood-light" aria-hidden="true">†</span>}
        <span className={`truncate ${isDirectory ? 'text-[var(--text-primary)] font-semibold' : ''}`}>{node.name}{isDirectory ? '/' : ''}</span>
      </div>
      {isDirectory && isOpen && (
        <div>
          {node.children?.map(child => (
            <FileNodeItem 
                key={child.path} 
                node={child} 
                onFileOpen={onFileOpen} 
                level={level + 1}
                setContextMenu={setContextMenu}
                creationInput={creationInput}
                setCreationInput={setCreationInput}
                onFileCreate={onFileCreate}
                onFolderCreate={onFolderCreate}
            />
          ))}
          {creationInput && creationInput.parentPath === node.path && (
                <CreationInput
                    type={creationInput.type}
                    parentPath={creationInput.parentPath}
                    onCancel={() => setCreationInput(null)}
                    onCreate={creationInput.type === 'file' ? onFileCreate : onFolderCreate}
                    level={level + 1}
                />
            )}
        </div>
      )}
    </div>
  );
};

const FileTree: React.FC<FileTreeProps> = ({ files, onFileOpen, contextMenu, setContextMenu, creationInput, setCreationInput, onFileCreate, onFolderCreate }) => {
  
  const handleRootContextMenu = (e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setContextMenu({ x: e.clientX, y: e.clientY, targetPath: '' });
  }
  
  return (
    <div className="text-sm text-[var(--text-secondary)] h-full flex flex-col" onContextMenu={handleRootContextMenu}>
      <div className="dx-pane-header">
        <span className="dx-label">Workspace</span>
        <span className="dx-label">{files.length}</span>
      </div>
      <div className="flex-grow py-3">
        {files.map(file => (
          <FileNodeItem 
            key={file.path} 
            node={file} 
            onFileOpen={onFileOpen} 
            level={0}
            setContextMenu={setContextMenu as any}
            creationInput={creationInput}
            setCreationInput={setCreationInput}
            onFileCreate={onFileCreate}
            onFolderCreate={onFolderCreate}
            />
        ))}
        {creationInput && creationInput.parentPath === '' && (
            <CreationInput
                type={creationInput.type}
                parentPath=""
                onCancel={() => setCreationInput(null)}
                onCreate={creationInput.type === 'file' ? onFileCreate : onFolderCreate}
                level={0}
            />
        )}
      </div>

       {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          targetPath={contextMenu.targetPath}
          onClose={() => setContextMenu(null)}
          onNewFile={(path) => setCreationInput({ type: 'file', parentPath: path })}
          onNewFolder={(path) => setCreationInput({ type: 'folder', parentPath: path })}
        />
      )}
    </div>
  );
};

export default FileTree;
