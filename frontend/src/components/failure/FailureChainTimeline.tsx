import React, { useState } from 'react';
import { GitFork, ArrowDown, ShieldAlert, CheckCircle2, Clock, FileText, HelpCircle } from 'lucide-react';
import { FailureChain, FailureEvent } from '../../types';

interface FailureChainTimelineProps {
  chain: FailureChain;
  onSelectEvidence?: (docTitle?: string, page?: number) => void;
}

export const FailureChainTimeline: React.FC<FailureChainTimelineProps> = ({
  chain,
  onSelectEvidence
}) => {
  const [selectedEvent, setSelectedEvent] = useState<FailureEvent>(chain.events[0]);

  const getRelationshipBadge = (type: string) => {
    switch (type) {
      case 'Confirmed Causal':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <CheckCircle2 className="w-3 h-3" /> Confirmed Causal Link
          </span>
        );
      case 'Documented Sequence':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
            <Clock className="w-3 h-3" /> Documented Chronology
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <HelpCircle className="w-3 h-3" /> Inferred / Suspected
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="p-4 rounded-2xl bg-space-900 border border-space-700 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-space-800 text-cosmic-purple border border-space-700 font-bold">
              {chain.space_agency}
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              Subsystem: {chain.subsystem}
            </span>
          </div>
          <h3 className="text-lg font-extrabold text-white">
            {chain.mission_name} – Causal Breakdown
          </h3>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="text-right">
            <span className="text-slate-500 block text-[10px]">TOTAL SEQUENCE EVENTS</span>
            <span className="text-cosmic-cyan font-bold">{chain.events.length} Documented Nodes</span>
          </div>
        </div>
      </div>

      {/* Main Interactive Diagram & Event Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Timeline Column (Left) */}
        <div className="lg:col-span-7 space-y-4">
          <p className="text-xs font-semibold text-slate-400 uppercase font-mono tracking-wider">
            Documented Causal Progression
          </p>

          <div className="space-y-3 relative before:absolute before:inset-0 before:left-5 before:w-0.5 before:bg-space-700 before:-z-0">
            {chain.events.map((ev, idx) => {
              const isSelected = selectedEvent?.id === ev.id;
              return (
                <div key={ev.id} className="relative z-10 flex items-start gap-4">
                  {/* Step Number Dot */}
                  <div
                    onClick={() => setSelectedEvent(ev)}
                    className={`w-10 h-10 rounded-xl flex items-center justify-center font-mono font-bold text-xs shrink-0 cursor-pointer transition-all shadow-md ${
                      isSelected
                        ? 'bg-cosmic-purple text-white ring-4 ring-purple-500/20 scale-105'
                        : 'bg-space-850 border border-space-700 text-slate-400 hover:border-slate-500 hover:text-white'
                    }`}
                  >
                    #{ev.event_order}
                  </div>

                  {/* Event Card */}
                  <div
                    onClick={() => setSelectedEvent(ev)}
                    className={`flex-1 p-4 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-space-850 border-cosmic-purple/60 shadow-lg shadow-purple-500/10'
                        : 'bg-space-900 border-space-750 hover:border-space-600 hover:bg-space-850'
                    }`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                      <span className="text-xs font-bold text-white tracking-wide">
                        {ev.event_title}
                      </span>
                      {getRelationshipBadge(ev.relationship_type)}
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed line-clamp-2">
                      {ev.event_description}
                    </p>

                    <div className="mt-2.5 pt-2 border-t border-space-750 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                      <span>{ev.event_timestamp || `Phase ${ev.event_order}`}</span>
                      <span className="text-cosmic-cyan flex items-center gap-1">
                        Page {ev.source_page || 1}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Event Details Inspector (Right) */}
        <div className="lg:col-span-5">
          <div className="p-6 rounded-2xl bg-space-900 border border-space-700 sticky top-24 space-y-5">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                <span>EVENT DETAILS INSPECTOR</span>
                <span className="text-cosmic-purple font-bold">Node #{selectedEvent?.event_order}</span>
              </div>
              <h4 className="text-base font-bold text-white">
                {selectedEvent?.event_title}
              </h4>
            </div>

            <div className="p-3.5 rounded-xl bg-space-850 border border-space-750 space-y-2">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Official Documented Description
              </span>
              <p className="text-xs text-slate-200 leading-relaxed">
                {selectedEvent?.event_description}
              </p>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between py-2 border-b border-space-800">
                <span className="text-slate-400">Causal Classification:</span>
                {getRelationshipBadge(selectedEvent?.relationship_type || "")}
              </div>
              <div className="flex items-center justify-between py-2 border-b border-space-800">
                <span className="text-slate-400">Timestamp / Telemetry:</span>
                <span className="font-mono text-slate-200">{selectedEvent?.event_timestamp || "Nominal Flight"}</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-space-800">
                <span className="text-slate-400">Investigation Document:</span>
                <span className="text-slate-200 font-medium truncate max-w-[180px]">
                  {selectedEvent?.document_title || "Official Board Report"}
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-space-800">
                <span className="text-slate-400">Evidence Citation:</span>
                <span className="font-mono text-amber-400 font-bold">
                  Page {selectedEvent?.source_page || 1}
                </span>
              </div>
            </div>

            {onSelectEvidence && (
              <button
                onClick={() => onSelectEvidence(selectedEvent?.document_title, selectedEvent?.source_page)}
                className="w-full py-2.5 rounded-xl bg-space-800 hover:bg-space-750 text-cosmic-cyan hover:text-white border border-space-700 text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                <FileText className="w-4 h-4" /> Inspect Original PDF Evidence
              </button>
            )}

            <p className="text-[10px] text-slate-500 italic text-center font-mono">
              {chain.methodology_note}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
