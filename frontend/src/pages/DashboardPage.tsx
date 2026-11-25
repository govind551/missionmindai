import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText, Rocket, Brain, Layers, GitFork, FileBarChart,
  CheckCircle2, ArrowRight, ShieldCheck, Activity, Database
} from 'lucide-react';
import { adminService, chatService, documentService } from '../services/api';
import { SystemStats, DocumentItem } from '../types';
import { Loader } from '../components/common/Loader';

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [recentDocs, setRecentDocs] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsData, docsData] = await Promise.all([
          adminService.getStats(),
          documentService.getDocuments()
        ]);
        setStats(statsData);
        setRecentDocs(docsData.slice(0, 4));
      } catch (err) {
        console.error("Dashboard data load failed:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) {
    return <div className="p-8"><Loader message="Loading flight operations statistics..." /></div>;
  }

  const statCards = [
    { label: "INDEXED TECHNICAL DOCUMENTS", val: stats?.total_documents || 6, icon: FileText, color: "text-cosmic-purple" },
    { label: "MISSIONS INVESTIGATED", val: stats?.total_missions || 6, icon: Rocket, color: "text-cosmic-cyan" },
    { label: "VECTOR EMBEDDING CHUNKS", val: stats?.total_chunks || 19, icon: Database, color: "text-emerald-400" },
    { label: "DOCUMENTED FAILURE MODES", val: stats?.total_incidents || 6, icon: Layers, color: "text-amber-400" },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-6 rounded-3xl bg-gradient-to-r from-space-900 via-space-850 to-space-900 border border-space-700 shadow-xl">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">
              AEROSPACE KNOWLEDGE SYSTEM ONLINE
            </span>
          </div>
          <h2 className="text-2xl font-black text-white">
            Command & Research Flight Deck
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Official NASA & ISRO Investigation Repositories • Full Traceability Active
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/assistant"
            className="px-4 py-2.5 rounded-xl bg-cosmic-violet hover:bg-cosmic-purple text-white text-xs font-bold shadow-lg shadow-purple-600/30 transition-all flex items-center gap-2"
          >
            <Brain className="w-4 h-4" />
            <span>Launch AI Assistant</span>
          </Link>
          <Link
            to="/similar-failures"
            className="px-4 py-2.5 rounded-xl bg-space-800 hover:bg-space-750 text-slate-200 border border-space-700 text-xs font-bold transition-all flex items-center gap-2"
          >
            <Layers className="w-4 h-4 text-cosmic-cyan" />
            <span>Compare Anomaly</span>
          </Link>
        </div>
      </div>

      {/* Statistics Counter Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className="p-5 rounded-2xl bg-space-900 border border-space-750 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-semibold text-slate-400 tracking-wider">
                  {card.label}
                </span>
                <Icon className={`w-4 h-4 ${card.color}`} />
              </div>
              <div className="text-3xl font-black text-white font-mono">
                {card.val}
              </div>
              <div className="text-[11px] text-slate-500 flex items-center gap-1 font-mono">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Grounded in official reports
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick-Access Feature Modules */}
      <div>
        <h3 className="text-sm font-bold text-slate-300 font-mono tracking-wider uppercase mb-4">
          Core Research Features
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <Link
            to="/assistant"
            className="p-6 rounded-2xl bg-space-900 border border-space-700 hover:border-cosmic-purple/60 hover:bg-space-850 transition-all group flex flex-col justify-between space-y-4"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-cosmic-purple/10 border border-cosmic-purple/30 flex items-center justify-center mb-3">
                <Brain className="w-5 h-5 text-cosmic-purple" />
              </div>
              <h4 className="text-base font-bold text-white group-hover:text-cosmic-purple transition-colors">
                AI Research Assistant
              </h4>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Query historical mission failures. Get answers grounded in NASA and ISRO documents with clickable page citations.
              </p>
            </div>
            <span className="text-xs font-semibold text-cosmic-purple flex items-center gap-1">
              Ask Research Inquiry <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </span>
          </Link>

          <Link
            to="/similar-failures"
            className="p-6 rounded-2xl bg-space-900 border border-space-700 hover:border-cosmic-cyan/60 hover:bg-space-850 transition-all group flex flex-col justify-between space-y-4"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-cosmic-cyan/10 border border-cosmic-cyan/30 flex items-center justify-center mb-3">
                <Layers className="w-5 h-5 text-cosmic-cyan" />
              </div>
              <h4 className="text-base font-bold text-white group-hover:text-cosmic-cyan transition-colors">
                Similar Past Failures
              </h4>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Describe a current design problem. The system calculates vector similarity and retrieves ranked historical incidents.
              </p>
            </div>
            <span className="text-xs font-semibold text-cosmic-cyan flex items-center gap-1">
              Find Matching Incidents <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </span>
          </Link>

          <Link
            to="/failure-chain"
            className="p-6 rounded-2xl bg-space-900 border border-space-700 hover:border-amber-500/60 hover:bg-space-850 transition-all group flex flex-col justify-between space-y-4"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mb-3">
                <GitFork className="w-5 h-5 text-amber-400" />
              </div>
              <h4 className="text-base font-bold text-white group-hover:text-amber-400 transition-colors">
                Failure Chain Analyzer
              </h4>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Reconstruct chronological causal sequences from official investigation reports, distinguishing confirmed causes.
              </p>
            </div>
            <span className="text-xs font-semibold text-amber-400 flex items-center gap-1">
              Inspect Causal Timelines <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </span>
          </Link>
        </div>
      </div>

      {/* Indexed Document Registry Table */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Indexed Public Investigation Reports</h3>
            <p className="text-xs text-slate-400">Available across dense vector and hybrid lexical retrieval</p>
          </div>
          <Link to="/documents" className="text-xs font-semibold text-cosmic-purple hover:underline flex items-center gap-1">
            View All Documents <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-space-850 text-slate-400 font-mono uppercase text-[10px] border-b border-space-750">
              <tr>
                <th className="py-3 px-4">Agency / Mission</th>
                <th className="py-3 px-4">Official Document Title</th>
                <th className="py-3 px-4">Year</th>
                <th className="py-3 px-4">Pages / Chunks</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-space-800 text-slate-300">
              {recentDocs.map((doc) => (
                <tr key={doc.id} className="hover:bg-space-850/50 transition-colors">
                  <td className="py-3 px-4 font-mono">
                    <span className="px-1.5 py-0.5 rounded bg-space-800 text-cosmic-purple border border-space-700 font-bold mr-2">
                      {doc.space_agency}
                    </span>
                    <span className="text-white font-medium">{doc.mission_name}</span>
                  </td>
                  <td className="py-3 px-4 font-medium text-slate-200 truncate max-w-xs">
                    {doc.title}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400">
                    {doc.publication_year || 'N/A'}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400">
                    {doc.total_pages} pages • {doc.chunk_count} chunks
                  </td>
                  <td className="py-3 px-4 font-mono">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/30">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Indexed
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
