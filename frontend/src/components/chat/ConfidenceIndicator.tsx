import React from 'react';
import { Gauge, ShieldCheck, AlertCircle } from 'lucide-react';

interface ConfidenceProps {
  confidence: number; // 0.0 to 1.0
  isGrounded?: boolean;
}

export const ConfidenceIndicator: React.FC<ConfidenceProps> = ({ confidence, isGrounded = true }) => {
  const percent = Math.min(100, Math.max(0, Math.round(confidence * 100)));
  
  let statusColor = "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
  let barColor = "bg-emerald-400";
  let label = "High Confidence (Grounded)";

  if (percent < 45 || !isGrounded) {
    statusColor = "text-rose-400 border-rose-500/30 bg-rose-500/10";
    barColor = "bg-rose-400";
    label = "Low Confidence (Below Evidence Threshold)";
  } else if (percent < 70) {
    statusColor = "text-amber-400 border-amber-500/30 bg-amber-500/10";
    barColor = "bg-amber-400";
    label = "Moderate Confidence (Corroborated)";
  }

  return (
    <div className={`inline-flex items-center gap-3 px-3 py-1.5 rounded-lg border text-xs font-mono ${statusColor}`}>
      <div className="flex items-center gap-1.5">
        <Gauge className="w-3.5 h-3.5" />
        <span className="font-bold">{percent}%</span>
      </div>
      <div className="w-16 h-1.5 bg-space-800 rounded-full overflow-hidden hidden sm:block">
        <div className={`h-full ${barColor} transition-all duration-500`} style={{ width: `${percent}%` }}></div>
      </div>
      <span className="text-[11px] font-sans font-medium text-slate-300 hidden md:inline">{label}</span>
    </div>
  );
};
