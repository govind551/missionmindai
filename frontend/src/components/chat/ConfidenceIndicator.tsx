import React from 'react';
import { Gauge, ShieldCheck, AlertCircle, HelpCircle, AlertTriangle } from 'lucide-react';

interface ConfidenceDetails {
  score?: number;
  level?: string;
  label?: string;
  warning?: string;
  is_grounded?: boolean;
  mission_consistent?: boolean;
}

interface ConfidenceProps {
  confidence: number; // 0.0 to 1.0
  isGrounded?: boolean;
  confidenceDetails?: ConfidenceDetails;
}

export const ConfidenceIndicator: React.FC<ConfidenceProps> = ({
  confidence,
  isGrounded = true,
  confidenceDetails
}) => {
  const percent = Math.min(100, Math.max(0, Math.round((confidenceDetails?.score ?? confidence) * 100)));
  const level = confidenceDetails?.level;
  const customLabel = confidenceDetails?.label;
  const warning = confidenceDetails?.warning;

  let statusColor = "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
  let barColor = "bg-emerald-400";
  let label = customLabel || "High Confidence (Documented Findings)";
  let Icon = ShieldCheck;

  if (level === "AMBIGUOUS") {
    statusColor = "text-cosmic-purple border-cosmic-purple/30 bg-cosmic-purple/10";
    barColor = "bg-cosmic-purple";
    label = customLabel || "Mission Clarification Needed";
    Icon = HelpCircle;
  } else if (level === "INSUFFICIENT" || percent < 45 || !isGrounded) {
    statusColor = "text-rose-400 border-rose-500/30 bg-rose-500/10";
    barColor = "bg-rose-400";
    label = customLabel || "Insufficient Documented Evidence";
    Icon = AlertCircle;
  } else if (level === "LOW" || percent < 55) {
    statusColor = "text-amber-400 border-amber-500/30 bg-amber-500/10";
    barColor = "bg-amber-400";
    label = customLabel || "Low Confidence (Sparse Documentation)";
    Icon = AlertTriangle;
  } else if (level === "MODERATE" || percent < 72) {
    statusColor = "text-sky-400 border-sky-500/30 bg-sky-500/10";
    barColor = "bg-sky-400";
    label = customLabel || "Moderate Confidence (Single Source Document)";
    Icon = ShieldCheck;
  }

  return (
    <div className="space-y-1">
      <div className={`inline-flex items-center gap-2.5 px-3 py-1.5 rounded-lg border text-xs font-mono ${statusColor}`}>
        <div className="flex items-center gap-1.5">
          <Icon className="w-3.5 h-3.5" />
          <span className="font-bold">{percent}%</span>
        </div>
        <div className="w-14 h-1.5 bg-space-800 rounded-full overflow-hidden hidden sm:block">
          <div className={`h-full ${barColor} transition-all duration-500`} style={{ width: `${percent}%` }}></div>
        </div>
        <span className="text-[11px] font-sans font-medium text-slate-200 hidden md:inline">{label}</span>
      </div>
      {warning && (
        <p className="text-[10px] text-amber-400/90 font-mono italic flex items-center gap-1 mt-0.5">
          <span>* Note: {warning}</span>
        </p>
      )}
    </div>
  );
};
