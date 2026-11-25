import React, { useState, useEffect } from 'react';
import {
  X, Download, FileText, CheckCircle2, ShieldCheck,
  Brain, ExternalLink, Calendar, Layers, Sparkles, Loader2
} from 'lucide-react';
import { chatService, reportService } from '../../services/api';
import { SessionSummaryData, CitationItem } from '../../types';
import { ConfidenceIndicator } from './ConfidenceIndicator';

interface ChatSummaryModalProps {
  sessionId?: number;
  isOpen: boolean;
  onClose: () => void;
  onSelectCitation: (citation: CitationItem) => void;
}

export const ChatSummaryModal: React.FC<ChatSummaryModalProps> = ({
  sessionId,
  isOpen,
  onClose,
  onSelectCitation
}) => {
  const [summaryData, setSummaryData] = useState<SessionSummaryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && sessionId) {
      loadSummary();
    }
  }, [isOpen, sessionId]);

  const loadSummary = async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await chatService.getSessionSummary(sessionId);
      setSummaryData(data);
    } catch (err: any) {
      console.error('Failed to load session summary:', err);
      setError('Unable to load session summary. Make sure inquiries have been submitted.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!sessionId || downloading) return;
    setDownloading(true);
    try {
      // Trigger dynamic generation and download
      const report = await reportService.generate({
        session_id: sessionId,
        report_title: summaryData?.session_title
          ? `MISSIONMIND AI – ${summaryData.session_title}`
          : 'MISSIONMIND AI – Aerospace Technical Investigation Report',
        include_failure_chain: true,
        include_similar_failures: true
      });

      // Trigger browser download via direct download link
      const downloadUrl = reportService.getDownloadUrl(report.id);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', `missionmind_session_${sessionId}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to generate/download PDF report:', err);
      // Fallback: direct streaming endpoint
      window.open(reportService.getLatestSessionDownloadUrl(sessionId), '_blank');
    } finally {
      setDownloading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-space-900 border border-space-700 w-full max-w-4xl max-h-[90vh] rounded-2xl flex flex-col shadow-2xl overflow-hidden">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-space-750 bg-space-850/80 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cosmic-purple/20 border border-cosmic-purple/40 flex items-center justify-center">
              <FileText className="w-5 h-5 text-cosmic-purple" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-white">Investigation Session Summary</h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cosmic-purple/20 text-cosmic-purple border border-cosmic-purple/30">
                  Live Technical Audit
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Synthesized record of all inquiries, AI findings, and verified NASA / ISRO document citations
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadPdf}
              disabled={downloading || loading || !summaryData || summaryData.total_queries === 0}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-cosmic-violet hover:bg-cosmic-purple text-white text-xs font-semibold shadow-lg shadow-purple-600/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all cursor-pointer"
              title="Download publication-ready PDF report"
            >
              {downloading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generating PDF...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Download PDF Report</span>
                </>
              )}
            </button>

            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-space-800 transition-colors"
              title="Close Summary"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="py-20 text-center space-y-3">
              <Loader2 className="w-8 h-8 text-cosmic-purple animate-spin mx-auto" />
              <p className="text-xs text-slate-400 font-mono">Compiling technical inquiry summary & citations...</p>
            </div>
          ) : error ? (
            <div className="py-12 text-center space-y-3">
              <p className="text-sm text-rose-400">{error}</p>
              <button
                onClick={loadSummary}
                className="px-4 py-2 rounded-xl bg-space-800 text-xs text-slate-300 hover:text-white"
              >
                Retry
              </button>
            </div>
          ) : summaryData ? (
            <>
              {/* Executive Summary Card */}
              <div className="p-4 rounded-xl bg-space-850/70 border border-space-750 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-mono font-bold text-cosmic-cyan">
                    <Sparkles className="w-4 h-4 text-cosmic-cyan" />
                    <span>EXECUTIVE SESSION SYNTHESIS</span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">
                    Session ID: #{summaryData.session_id}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {summaryData.executive_summary}
                </p>
              </div>

              {/* Statistics Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-space-850 border border-space-750">
                  <span className="text-[10px] font-mono text-slate-400 block uppercase">Inquiries Asked</span>
                  <span className="text-xl font-bold text-white mt-1 block">
                    {summaryData.total_queries}
                  </span>
                  <span className="text-[10px] text-slate-500">User prompts</span>
                </div>

                <div className="p-3 rounded-xl bg-space-850 border border-space-750">
                  <span className="text-[10px] font-mono text-slate-400 block uppercase">Answers Generated</span>
                  <span className="text-xl font-bold text-white mt-1 block">
                    {summaryData.total_answers}
                  </span>
                  <span className="text-[10px] text-slate-500">RAG synthesized</span>
                </div>

                <div className="p-3 rounded-xl bg-space-850 border border-space-750">
                  <span className="text-[10px] font-mono text-slate-400 block uppercase">Cited Documents</span>
                  <span className="text-xl font-bold text-cosmic-cyan mt-1 block">
                    {summaryData.total_citations}
                  </span>
                  <span className="text-[10px] text-slate-500">Page-level sources</span>
                </div>

                <div className="p-3 rounded-xl bg-space-850 border border-space-750">
                  <span className="text-[10px] font-mono text-slate-400 block uppercase">Avg Grounding</span>
                  <span className="text-xl font-bold text-emerald-400 mt-1 block">
                    {Math.round(summaryData.average_confidence * 100)}%
                  </span>
                  <span className="text-[10px] text-slate-500">Evidence confidence</span>
                </div>
              </div>

              {/* Missions & Agencies Index */}
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="text-[11px] font-mono text-slate-400 font-semibold">Missions Covered:</span>
                {summaryData.missions_covered.map((m, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 rounded-lg bg-space-800 text-slate-300 border border-space-700 text-[11px]"
                  >
                    {m}
                  </span>
                ))}
              </div>

              {/* Complete Chronological Q&A Log */}
              <div className="space-y-4 pt-2">
                <div className="flex items-center justify-between border-b border-space-800 pb-2">
                  <h4 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider">
                    Chronological Q&A Investigation Log ({summaryData.qa_pairs.length})
                  </h4>
                  <span className="text-[10px] text-slate-500 font-mono">
                    All Questions & Cited Answers Included in PDF
                  </span>
                </div>

                {summaryData.qa_pairs.length === 0 ? (
                  <div className="py-8 text-center text-xs text-slate-500">
                    No questions recorded in this session yet.
                  </div>
                ) : (
                  summaryData.qa_pairs.map((qa) => (
                    <div
                      key={qa.query_number}
                      className="p-4 rounded-xl bg-space-850/90 border border-space-750 space-y-3"
                    >
                      {/* Query Header */}
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-2">
                          <span className="px-2 py-0.5 rounded-md bg-cosmic-purple/20 text-cosmic-purple font-mono font-bold text-[10px] mt-0.5 shrink-0">
                            Q{qa.query_number}
                          </span>
                          <h5 className="text-xs font-bold text-white">
                            {qa.question}
                          </h5>
                        </div>
                        <ConfidenceIndicator confidence={qa.retrieval_confidence} />
                      </div>

                      {/* Answer Body */}
                      <div className="p-3 rounded-lg bg-space-900 border border-space-800 text-xs text-slate-300 leading-relaxed whitespace-pre-line">
                        {qa.answer}
                      </div>

                      {/* Citations List */}
                      {qa.citations && qa.citations.length > 0 && (
                        <div className="space-y-1.5 pt-1">
                          <span className="text-[10px] font-mono font-semibold text-slate-400 block uppercase">
                            Verified Source Citations ({qa.citations.length}):
                          </span>
                          <div className="flex flex-wrap gap-2">
                            {qa.citations.map((cit, cIdx) => (
                              <button
                                key={cIdx}
                                onClick={() => {
                                  onSelectCitation(cit);
                                  onClose();
                                }}
                                className="group flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-space-800 hover:bg-space-750 border border-space-700 hover:border-cosmic-purple/50 text-[11px] text-slate-300 hover:text-white transition-all cursor-pointer text-left"
                                title="Click to view exact cited page in high-resolution PDF viewer"
                              >
                                <span className="font-semibold text-cosmic-purple group-hover:text-cosmic-cyan">
                                  {cit.mission_name || 'Investigation'}
                                </span>
                                <span className="text-slate-500">|</span>
                                <span className="text-slate-400 truncate max-w-[180px]">
                                  {cit.document_title}
                                </span>
                                <span className="px-1.5 py-0.2 rounded bg-space-900 text-[10px] font-mono text-cosmic-cyan">
                                  Page {cit.page_number}
                                </span>
                                <ExternalLink className="w-3 h-3 text-slate-500 group-hover:text-white" />
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </>
          ) : null}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 border-t border-space-750 bg-space-850/80 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-mono">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Dynamic Report: updates automatically when new questions are sent</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs text-slate-300 hover:text-white hover:bg-space-800 transition-colors"
            >
              Close
            </button>
            <button
              onClick={handleDownloadPdf}
              disabled={downloading || loading || !summaryData || summaryData.total_queries === 0}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cosmic-violet hover:bg-cosmic-purple text-white text-xs font-semibold shadow-lg shadow-purple-600/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all cursor-pointer"
            >
              {downloading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generating PDF...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Download Session PDF</span>
                </>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
