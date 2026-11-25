import React, { useState, useEffect } from 'react';
import { FileBarChart, Download, Plus, CheckCircle2, FileText, Calendar, Clock, RefreshCw } from 'lucide-react';
import { reportService, chatService } from '../services/api';
import { GeneratedReportItem, ResearchSession } from '../types';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { Loader } from '../components/common/Loader';
import { ErrorMessage } from '../components/common/ErrorMessage';

export const ResearchReportsPage: React.FC = () => {
  const [reports, setReports] = useState<GeneratedReportItem[]>([]);
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [loading, setLoading] = useState(true);

  // Generate modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);
  const [reportTitle, setReportTitle] = useState('Aerospace Mishap Lessons-Learned Technical Report');
  const [includeChain, setIncludeChain] = useState(true);
  const [includeSimilar, setIncludeSimilar] = useState(true);
  const [notes, setNotes] = useState('Official synthesis for pre-flight readiness review.');
  const [isGenerating, setIsGenerating] = useState(false);
  const [genError, setGenError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [reps, sess] = await Promise.all([
        reportService.listReports(),
        chatService.getSessions()
      ]);
      setReports(reps);
      setSessions(sess);
      if (sess.length > 0) {
        setSelectedSessionId(sess[0].id);
      }
    } catch (err) {
      console.warn("Failed loading reports:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSessionId) {
      setGenError("Please select a valid research session.");
      return;
    }
    setGenError('');
    setIsGenerating(true);

    try {
      const newReport = await reportService.generate({
        session_id: selectedSessionId,
        report_title: reportTitle,
        include_failure_chain: includeChain,
        include_similar_failures: includeSimilar,
        custom_notes: notes
      });
      setReports([newReport, ...reports]);
      setIsModalOpen(false);
    } catch (err: any) {
      setGenError(err.response?.data?.detail || "ReportLab PDF generation failed.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Top Banner */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <FileBarChart className="w-4 h-4 text-cosmic-purple" />
            <span className="text-xs font-mono font-bold text-cosmic-purple uppercase tracking-wider">
              SMART PDF REPORT GENERATOR
            </span>
          </div>
          <h2 className="text-2xl font-black text-white">
            My Research & Executive PDF Reports
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Generate formal, publication-grade aerospace technical investigation reports using ReportLab. Retains questions, cited answers, failure mode analyses, and chronological timelines.
          </p>
        </div>

        <Button
          variant="primary"
          onClick={() => setIsModalOpen(true)}
          icon={<Plus className="w-4 h-4" />}
          className="text-xs font-bold px-4 py-2.5"
        >
          Generate New PDF Report
        </Button>
      </div>

      {/* Reports Grid */}
      {loading ? (
        <Loader message="Loading generated aerospace reports..." />
      ) : reports.length === 0 ? (
        <div className="p-12 text-center rounded-3xl bg-space-900 border border-space-700 text-xs text-slate-400 space-y-3">
          <FileBarChart className="w-8 h-8 text-slate-500 mx-auto" />
          <p className="text-slate-300 font-semibold">No reports generated yet.</p>
          <p className="text-slate-500 text-[11px]">
            Run an inquiry in the AI Research Assistant, then click "Generate New PDF Report" to export.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {reports.map((r) => (
            <div
              key={r.id}
              className="p-5 rounded-2xl bg-space-900 border border-space-700 hover:border-cosmic-purple/50 transition-all flex flex-col justify-between space-y-4 shadow-lg group"
            >
              <div>
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-2">
                  <span className="flex items-center gap-1.5 text-cosmic-purple font-bold">
                    <FileBarChart className="w-3.5 h-3.5" /> REPORT #{r.id}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" /> {new Date(r.created_at).toLocaleDateString()}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-white group-hover:text-cosmic-purple transition-colors">
                  {r.report_title}
                </h4>

                <p className="mt-2 text-xs text-slate-400 font-mono">
                  Session Reference: #{r.session_id || 'Active'}
                </p>

                <div className="mt-3 p-2.5 rounded-xl bg-space-850 border border-space-800 text-[11px] text-slate-300 space-y-1">
                  <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>ReportLab Publication-Grade PDF</span>
                  </div>
                  <p className="text-[10px] text-slate-500 font-mono">
                    Full page-level citations & failure chain analysis embedded
                  </p>
                </div>
              </div>

              <div className="pt-3 border-t border-space-800">
                <a
                  href={reportService.getDownloadUrl(r.id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full py-2.5 rounded-xl bg-space-800 hover:bg-space-750 text-white border border-space-700 text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer shadow-sm"
                >
                  <Download className="w-4 h-4 text-cosmic-purple" /> Download Report PDF
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Generate Report Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Generate Technical PDF Report"
        subtitle="ReportLab creates a formal aerospace briefing with cited evidence and failure chains."
      >
        <form onSubmit={handleGenerate} className="space-y-4">
          {genError && <ErrorMessage message={genError} />}

          <div>
            <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
              REPORT TITLE *
            </label>
            <input
              type="text"
              required
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple"
            />
          </div>

          <div>
            <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
              SELECT RESEARCH SESSION *
            </label>
            <select
              value={selectedSessionId || ''}
              onChange={(e) => setSelectedSessionId(Number(e.target.value))}
              required
              className="w-full px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple cursor-pointer"
            >
              {sessions.map((s) => (
                <option key={s.id} value={s.id}>
                  #{s.id} - {s.title}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2 pt-2">
            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={includeChain}
                onChange={(e) => setIncludeChain(e.target.checked)}
                className="rounded border-space-700 text-cosmic-purple focus:ring-0 cursor-pointer"
              />
              <span>Include Reconstructed Failure Chain & Chronological Timelines</span>
            </label>
            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={includeSimilar}
                onChange={(e) => setIncludeSimilar(e.target.checked)}
                className="rounded border-space-700 text-cosmic-purple focus:ring-0 cursor-pointer"
              />
              <span>Include Similar Historical Failure Precedent Comparison</span>
            </label>
          </div>

          <div>
            <label className="block text-xs font-mono font-bold text-slate-300 mb-1">
              INVESTIGATOR NOTES & SCOPE
            </label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple"
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-space-800">
            <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={isGenerating}>
              Compile & Export PDF
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
