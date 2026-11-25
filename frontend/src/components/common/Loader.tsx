import React from 'react';

export const Loader: React.FC<{ message?: string }> = ({ message = 'Loading aerospace telemetry...' }) => (
  <div className="flex flex-col items-center justify-center p-8 space-y-3">
    <div className="relative w-10 h-10">
      <div className="absolute inset-0 rounded-full border-2 border-cosmic-purple/20"></div>
      <div className="absolute inset-0 rounded-full border-2 border-t-cosmic-purple animate-spin"></div>
    </div>
    <p className="text-xs text-slate-400 font-mono tracking-wide">{message}</p>
  </div>
);
