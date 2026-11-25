import React from 'react';
import { Layers, AlertTriangle, ShieldCheck, FileText, ArrowRight } from 'lucide-react';
import { FailureIncident } from '../../types';

interface FailureCardProps {
  incident: FailureIncident;
  onInspectCitation?: (docId: number, pageNum: number) => void;
}

export const FailureCard: React.FC<FailureCardProps> = ({ incident, onInspectCitation }) => {
  const scorePercent = incident.similarity_score
    ? Math.round(incident.similarity_score * 100)
    : 100;

  let badgeColor = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
  if (scorePercent < 60) badgeColor = "bg-amber-500/10 text-amber-400 border-amber-500/30";
  if (scorePercent < 45) badgeColor = "bg-slate-500/10 text-slate-400 border-slate-500/30";

  return (
    <div className="p-5 rounded-2xl bg-space-900 border border-space-700 hover:border-cosmic-purple/50 transition-all shadow-lg flex flex-col justify-between space-y-4">
      {/* Top Header */}
      <div>
        <div className="flex items-start justify-between gap-3 mb-2">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-space-800 text-cosmic-purple border border-space-700 uppercase font-semibold">
                {incident.space_agency}
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-space-800 text-slate-400 border border-space-700">
                Subsystem: {incident.subsystem}
              </span>
            </div>
            <h4 className="text-base font-bold text-white tracking-wide">
              {incident.mission_name}
            </h4>
          </div>

          <div className={`px-2.5 py-1 rounded-lg border font-mono text-xs font-bold shrink-0 ${badgeColor}`}>
            {scorePercent}% Similarity
          </div>
        </div>

        {/* Failure Description */}
        <p className="text-xs text-slate-300 leading-relaxed mt-2">
          {incident.failure_description}
        </p>

        {/* Root Cause Callout */}
        <div className="mt-3.5 p-3 rounded-xl bg-space-850 border border-space-750 space-y-1.5">
          <div className="flex items-center gap-1.5 text-rose-400 text-xs font-semibold">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Documented Root Cause</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {incident.root_cause}
          </p>
        </div>

        {/* Mission Impact & Corrective Action */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3 text-[11px]">
          {incident.mission_impact && (
            <div className="p-2.5 rounded-lg bg-space-950/60 border border-space-800">
              <span className="text-slate-500 block text-[10px] uppercase font-mono">Mission Impact</span>
              <span className="text-slate-200 font-medium">{incident.mission_impact}</span>
            </div>
          )}
          {incident.corrective_action && (
            <div className="p-2.5 rounded-lg bg-space-950/60 border border-space-800">
              <span className="text-emerald-400 block text-[10px] uppercase font-mono">Prescribed Fix</span>
              <span className="text-slate-200 font-medium">{incident.corrective_action}</span>
            </div>
          )}
        </div>
      </div>

      {/* Supporting Document & Page Citations */}
      {incident.citations && incident.citations.length > 0 && (
        <div className="pt-3 border-t border-space-800 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-1.5 truncate mr-2">
            <FileText className="w-3.5 h-3.5 text-cosmic-purple shrink-0" />
            <span className="truncate text-slate-300">
              {incident.citations[0].document_title} (Page {incident.citations[0].page_number})
            </span>
          </div>
          {onInspectCitation && incident.citations[0].document_id && (
            <button
              onClick={() => onInspectCitation(incident.citations![0].document_id, incident.citations![0].page_number)}
              className="text-cosmic-cyan hover:text-white font-medium text-xs flex items-center gap-1 shrink-0"
            >
              Verify Evidence <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>
      )}
    </div>
  );
};
