import React from 'react';
import { ToastData } from '../../types';
import XIcon from '../icons/XIcon';

interface ToastContainerProps {
  toasts: ToastData[];
  setToasts: React.Dispatch<React.SetStateAction<ToastData[]>>;
}

const TONE = {
  success: { label: 'OK', text: 'text-phosphor', bar: 'bg-phosphor' },
  error: { label: 'ERR', text: 'text-blood-light', bar: 'bg-blood' },
  info: { label: 'SYS', text: 'text-signal', bar: 'bg-signal' },
} as const;

const Toast: React.FC<{ toast: ToastData; onDismiss: (id: number) => void }> = ({ toast, onDismiss }) => {
  const tone = TONE[toast.type];
  return (
    <div
      role={toast.type === 'error' ? 'alert' : 'status'}
      className="dx-panel relative flex items-start gap-3 pl-4 pr-2 py-3 mb-2 w-80 max-w-[calc(100vw-2rem)] bg-[var(--bg-elevated)] shadow-2xl animate-fade-in-right"
    >
      <span className={`absolute left-0 top-0 bottom-0 w-[3px] ${tone.bar}`} aria-hidden="true" />
      <span className={`font-mono text-[10px] font-semibold tracking-hud pt-0.5 ${tone.text}`}>[{tone.label}]</span>
      <p className="flex-grow text-sm text-[var(--text-primary)] leading-snug">{toast.message}</p>
      <button onClick={() => onDismiss(toast.id)} className="p-1 text-[var(--text-muted)] hover:text-bone" aria-label="Dismiss notification">
        <XIcon className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};


const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, setToasts }) => {
  const handleDismiss = (id: number) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-14 right-4 z-[100]">
      {toasts.map(toast => (
        <Toast key={toast.id} toast={toast} onDismiss={handleDismiss} />
      ))}
    </div>
  );
};

export default ToastContainer;
