import React, { useState, useEffect } from 'react';
import { ShieldCheck, Database, Users, Activity, FileText, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { adminService } from '../services/api';
import { SystemStats } from '../types';
import { Loader } from '../components/common/Loader';
import { Button } from '../components/common/Button';

export const AdminPage: React.FC = () => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [docs, setDocs] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [statsData, docsData, usersData, logsData] = await Promise.all([
        adminService.getStats(),
        adminService.getAdminDocs(),
        adminService.getUsers(),
        adminService.getLogs()
      ]);
      setStats(statsData);
      setDocs(docsData);
      setUsers(usersData);
      setLogs(logsData);
    } catch (err) {
      console.warn("Failed loading admin operations data:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8"><Loader message="Loading flight operations audit telemetry..." /></div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Top Banner */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">
              MISSION OPERATIONS HEADQUARTERS
            </span>
          </div>
          <h2 className="text-2xl font-black text-white">
            System Administration & Ingestion Logs
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Manage indexed aerospace technical reports, monitor vector pipeline health, and review audit logs.
          </p>
        </div>

        <Button variant="secondary" onClick={loadAdminData} icon={<RefreshCw className="w-3.5 h-3.5" />}>
          Refresh Telemetry
        </Button>
      </div>

      {/* Active Pipeline Engine Specs */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
          Active AI Engine Architecture
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-4 rounded-2xl bg-space-850 border border-space-800 space-y-1">
            <span className="text-slate-500 block text-[10px] uppercase">DENSE VECTOR EMBEDDER</span>
            <span className="text-cosmic-purple font-bold block">{stats?.active_models?.embedding}</span>
            <span className="text-[10px] text-slate-400">384 Dimensions • L2 Normalized</span>
          </div>
          <div className="p-4 rounded-2xl bg-space-850 border border-space-800 space-y-1">
            <span className="text-slate-500 block text-[10px] uppercase">GROUNDED REASONING MODEL</span>
            <span className="text-cosmic-cyan font-bold block">{stats?.active_models?.llm}</span>
            <span className="text-[10px] text-slate-400">Strict Evidence Constraint</span>
          </div>
          <div className="p-4 rounded-2xl bg-space-850 border border-space-800 space-y-1">
            <span className="text-slate-500 block text-[10px] uppercase">DOCUMENT PARSING PIPELINE</span>
            <span className="text-emerald-400 font-bold block">{stats?.active_models?.pdf_extractor}</span>
            <span className="text-[10px] text-slate-400">Page-Bounded Text & OCR Fallback</span>
          </div>
        </div>
      </div>

      {/* Ingestion & Audit Logs */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
          Ingestion & Processing Audit Logs
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-space-850 text-slate-400 text-[10px] uppercase border-b border-space-750">
              <tr>
                <th className="py-2.5 px-4">Doc ID</th>
                <th className="py-2.5 px-4">Mission / Report Title</th>
                <th className="py-2.5 px-4">Pages</th>
                <th className="py-2.5 px-4">Chunks</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-space-800 text-slate-300">
              {logs.map((log, idx) => (
                <tr key={idx} className="hover:bg-space-850/50">
                  <td className="py-2.5 px-4 text-cosmic-purple font-bold">#{log.document_id}</td>
                  <td className="py-2.5 px-4 truncate max-w-sm text-white">{log.title}</td>
                  <td className="py-2.5 px-4 text-slate-400">{log.pages}</td>
                  <td className="py-2.5 px-4 text-slate-400">{log.chunks_generated}</td>
                  <td className="py-2.5 px-4">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/30">
                      <CheckCircle2 className="w-3 h-3" /> Completed
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-slate-500 text-[10px]">
                    {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'Recent'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Users & Roles Management */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 shadow-xl space-y-4">
        <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
          Registered Flight Crew & Researchers ({users.length})
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-space-850 text-slate-400 font-mono text-[10px] uppercase border-b border-space-750">
              <tr>
                <th className="py-2.5 px-4">Callsign</th>
                <th className="py-2.5 px-4">Official Email</th>
                <th className="py-2.5 px-4">Role Clearance</th>
                <th className="py-2.5 px-4">Account Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-space-800 text-slate-300">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-space-850/50">
                  <td className="py-2.5 px-4 font-bold text-white">{u.name}</td>
                  <td className="py-2.5 px-4 font-mono text-slate-400">{u.email}</td>
                  <td className="py-2.5 px-4 font-mono">
                    <span className="px-2 py-0.5 rounded bg-space-800 text-cosmic-purple border border-space-700 uppercase text-[10px] font-bold">
                      {u.role}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 font-mono text-slate-500 text-[10px]">
                    {new Date(u.created_at).toLocaleDateString()}
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
