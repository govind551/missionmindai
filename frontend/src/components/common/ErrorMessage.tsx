import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const ErrorMessage: React.FC<{ message: string; onRetry?: () => void }> = ({ message, onRetry }) => (
  <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-start gap-3">
    <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
    <div className="flex-1">
      <p className="text-xs font-medium leading-relaxed">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 text-xs font-semibold text-rose-400 hover:text-rose-300 underline"
        >
          Try Again
        </button>
      )}
    </div>
  </div>
);
