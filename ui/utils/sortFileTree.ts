import { FileNode } from '../components/FileTree';

export const sortFileTree = (nodes: FileNode[]): FileNode[] => {
  const sortedNodes = [...nodes].sort((a, b) => {
    const aIsDir = !!a.children;
    const bIsDir = !!b.children;

    // Directories before files
    if (aIsDir && !bIsDir) return -1;
    if (!aIsDir && bIsDir) return 1;

    // Alphabetical sort for nodes of the same type
    return a.name.localeCompare(b.name);
  });

  // Recursively sort children
  return sortedNodes.map(node => {
    if (node.children) {
      return { ...node, children: sortFileTree(node.children) };
    }
    return node;
  });
};
