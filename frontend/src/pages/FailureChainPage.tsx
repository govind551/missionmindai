import React, { useState, useEffect } from 'react';
import { GitFork, ShieldCheck, FileText, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';
import { failureChainService } from '../services/api';
import { FailureChain } from '../types';
import { FailureChainTimeline } from '../components/failure/FailureChainTimeline';
import { PDFViewer } from '../components/documents/PDFViewer';
import { Loader } from '../components/common/Loader';

export const FailureChainPage: React.FC = () => {
  const [missionsList, setMissionsList] = useState<any[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<number | null>(null);
  const [activeChain, setActiveChain] = useState<FailureChain | null>(null);
  const [loading, setLoading] = useState(true);
  const [chainLoading, setChainLoading] = useState(false);
  const [pdfInspector, setPdfInspector] = useState<{ docTitle?: string; page?: number } | null>(null);

  useEffect(() => {
    loadMissions();
  }, []);

  const loadMissions = async () => {
    try {
      const data = await failureChainService.listMissions();
      setMissionsList(data);
      if (data.length > 0) {
        setSelectedIncidentId(data[0].incident_id);
        loadChain(data[0].incident_id);
      }
    } catch (err) {
      console.warn("Failed loading missions for failure chain:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadChain = async (incidentId: number) => {
    setChainLoading(true);
    try {
      const chain = await failureChainService.getChain(incidentId);
      setActiveChain(chain);
    } catch (err) {
      console.warn("Failed loading chain:", err);
    } finally {
      setChainLoading(false);
    }
  };

  const handleSelectMission = (incidentId: number) => {
    setSelectedIncidentId(incidentId);
    loadChain(incidentId);
  };

  if (loading) {
    return <div className="p-8"><Loader message="Loading documented failure chain registry..." /></div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Header Banner */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <GitFork className="w-4 h-4 text-amber-400" />
            <span className="text-xs font-mono font-bold text-amber-400 uppercase tracking-wider">
              FAILURE CHAIN RECONSTRUCTION
            </span>
          </div>
          <h2 className="text-2xl font-black text-white">
            Root Cause & Cascading Anomaly Breakdown
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Reconstruct how an initial technical defect cascades through spacecraft subsystems to terminate a mission. Every link is verified against official board event timelines.
          </p>
        </div>

        <div className="p-3 rounded-xl bg-space-850 border border-space-750 text-xs font-mono text-slate-400 shrink-0">
          <div className="text-emerald-400 font-bold">100% CITED EVIDENCE</div>
          <p className="text-[10px] text-slate-500">No Inferred Links Presented as Confirmed</p>
        </div>
      </div>

      {/* Mission Selector Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {missionsList.map((m) => {
          const isSelected = selectedIncidentId === m.incident_id;
          return (
            <button
              key={m.incident_id}
              onClick={() => handleSelectMission(m.incident_id)}
              className={`px-4 py-2.5 rounded-xl text-xs font-medium transition-all shrink-0 cursor-pointer flex items-center gap-2 ${
                isSelected
                  ? 'bg-cosmic-purple text-white shadow-lg shadow-purple-600/20 font-bold'
                  : 'bg-space-900 border border-space-750 text-slate-400 hover:text-white hover:bg-space-850'
              }`}
            >
              <span className="font-mono text-[10px] px-1.5 py-0.2 rounded bg-black/30">
                {m.space_agency}
              </span>
              <span>{m.mission_name}</span>
            </button>
          );
        })}
      </div>

      {/* Main Chain Visualizer */}
      {chainLoading ? (
        <Loader message="Reconstructing chronological causal sequence..." />
      ) : activeChain ? (
        <FailureChainTimeline
          chain={activeChain}
          onSelectEvidence={(title, page) => setPdfInspector({ docTitle: title, page })}
        />
      ) : (
        <div className="p-12 text-center rounded-3xl bg-space-900 border border-space-700 text-xs text-slate-400">
          No failure chain available for this incident.
        </div>
      )}

      {/* PDF Evidence Inspector */}
      {pdfInspector && (
        <PDFViewer
          citation={null}
          documentId={1} // Default Mars Climate Orbiter or active doc
          initialPage={pdfInspector.page || 1}
          onClose={() => setPdfInspector(null)}
        />
      )}
    </div>
  );
};
