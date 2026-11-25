import React from 'react';
import FilePlusIcon from './icons/FilePlusIcon';
import FolderPlusIcon from './icons/FolderPlusIcon';

interface ContextMenuProps {
  x: number;
  y: number;
  targetPath: string;
  onClose: () => void;
  onNewFile: (path: string) => void;
  onNewFolder: (path: string) => void;
}

const ContextMenu: React.FC<ContextMenuProps> = ({ x, y, targetPath, onClose, onNewFile, onNewFolder }) => {
  const menuStyle: React.CSSProperties = {
    top: y,
    left: x,
  };

  const handleNewFile = () => {
    onNewFile(targetPath);
    onClose();
  };

  const handleNewFolder = () => {
    onNewFolder(targetPath);
    onClose();
  };

  return (
    <div
      style={menuStyle}
      className="fixed dx-panel bg-[var(--bg-elevated)] shadow-2xl py-1 z-50 min-w-[160px] text-[var(--text-primary)] font-mono text-xs animate-fade-in-right"
    >
      <ul>
        <li
          onClick={handleNewFile}
          className="px-3 py-1.5 hover:bg-blood/15 hover:text-bone border-l-2 border-transparent hover:border-blood cursor-pointer flex items-center gap-2 uppercase tracking-wider"
        >
          <FilePlusIcon className="w-4 h-4" />
          <span>New File</span>
        </li>
        <li
          onClick={handleNewFolder}
          className="px-3 py-1.5 hover:bg-blood/15 hover:text-bone border-l-2 border-transparent hover:border-blood cursor-pointer flex items-center gap-2 uppercase tracking-wider"
        >
          <FolderPlusIcon className="w-4 h-4" />
          <span>New Folder</span>
        </li>
      </ul>
    </div>
  );
};

export default ContextMenu;