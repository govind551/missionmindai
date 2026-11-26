import React, { useState, useEffect, useRef } from 'react';
import {
  Send, Brain, Sparkles, MessageSquare, Plus, Trash2,
  FileText, ShieldCheck, Gauge, AlertCircle, RefreshCw,
  Download, Loader2, ChevronDown, Check, Search, Layers,
  BookOpen, X
} from 'lucide-react';
import { chatService, reportService, documentService } from '../services/api';
import { ResearchSession, ResearchMessage, CitationItem, DocumentItem } from '../types';
import { ConfidenceIndicator } from '../components/chat/ConfidenceIndicator';
import { CitationList } from '../components/chat/CitationList';
import { VoiceRecorder } from '../components/voice/VoiceRecorder';
import { PDFViewer } from '../components/documents/PDFViewer';
import { ChatSummaryModal } from '../components/chat/ChatSummaryModal';
import { Loader } from '../components/common/Loader';

const SUGGESTED_QUESTIONS = [
  "What went wrong with thermal control on past space probes?",
  "How did software unit mismatches affect the Mars Climate Orbiter?",
  "Why did the Challenger O-rings fail at cold temperatures?",
  "What caused the cryogenic upper stage shutdown on ISRO GSLV-F10?",
  "Explain the thermal protection system breach on Columbia STS-107",
  "What caused the heat shield separation failure on ISRO PSLV-C39?",
  "What are the quantum physics mechanisms of interstellar warp drives?" // Test Demo 6: Not Found
];

export const ResearchAssistantPage: React.FC = () => {
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<number | undefined>(undefined);
  const [messages, setMessages] = useState<ResearchMessage[]>([]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [isAnswering, setIsAnswering] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<CitationItem | null>(null);
  const [isSummaryOpen, setIsSummaryOpen] = useState(false);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [availableReports, setAvailableReports] = useState<DocumentItem[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<number | 'all'>('all');
  const [isReportDropdownOpen, setIsReportDropdownOpen] = useState(false);
  const [reportSearchQuery, setReportSearchQuery] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleQuickDownloadPdf = async () => {
    if (!currentSessionId || messages.length === 0 || isDownloadingPdf) return;
    setIsDownloadingPdf(true);
    try {
      const report = await reportService.generate({
        session_id: currentSessionId,
        report_title: 'MISSIONMIND AI – Aerospace Technical Investigation Report',
        include_failure_chain: true,
        include_similar_failures: true
      });
      const downloadUrl = reportService.getDownloadUrl(report.id);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', `missionmind_session_${currentSessionId}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to quick download PDF report:', err);
      window.open(reportService.getLatestSessionDownloadUrl(currentSessionId), '_blank');
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  // Load research sessions and uploaded reports
  useEffect(() => {
    loadSessions();
    loadReports();
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsReportDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const loadReports = async () => {
    try {
      const data = await documentService.getDocuments();
      setAvailableReports(data);
    } catch (err) {
      console.warn("Could not load reports for selector:", err);
    }
  };

  const loadSessions = async () => {
    try {
      const data = await chatService.getSessions();
      setSessions(data);
      if (data.length > 0 && !currentSessionId) {
        loadSessionDetails(data[0].id);
      }
    } catch (err) {
      console.warn("Could not load sessions:", err);
    }
  };

  const loadSessionDetails = async (id: number) => {
    try {
      const s = await chatService.getSession(id);
      setCurrentSessionId(s.id);
      setMessages(s.messages || []);
    } catch (err) {
      console.warn("Could not load session details:", err);
    }
  };

  const handleNewSession = async () => {
    try {
      const s = await chatService.createSession("New Aerospace Investigation");
      setSessions([s, ...sessions]);
      setCurrentSessionId(s.id);
      setMessages([]);
    } catch (err) {
      console.warn("Error creating session:", err);
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    try {
      await chatService.deleteSession(id);
      const filtered = sessions.filter((s) => s.id !== id);
      setSessions(filtered);
      if (currentSessionId === id) {
        if (filtered.length > 0) {
          loadSessionDetails(filtered[0].id);
        } else {
          setCurrentSessionId(undefined);
          setMessages([]);
        }
      }
    } catch (err) {
      console.warn("Error deleting session:", err);
    }
  };

  const handleSend = async (qToSend?: string) => {
    const q = (qToSend || inputQuestion).trim();
    if (!q || isAnswering) return;

    setInputQuestion('');
    setIsAnswering(true);

    // Optimistically show user message
    const tempUserMsg: ResearchMessage = {
      id: Date.now(),
      session_id: currentSessionId || 0,
      role: 'user',
      message_text: q,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await chatService.askQuestion({
        question: q,
        session_id: currentSessionId,
        document_id: selectedReportId !== 'all' ? selectedReportId : undefined,
        is_all_reports: selectedReportId === 'all'
      });

      if (!currentSessionId) {
        setCurrentSessionId(res.session_id);
        loadSessions();
      }

      const assistantMsg: ResearchMessage = {
        id: res.message_id,
        session_id: res.session_id,
        role: 'assistant',
        message_text: res.answer,
        citations: res.citations,
        retrieval_confidence: res.retrieval_confidence,
        confidence_details: res.confidence_details,
        active_mission: res.active_mission,
        created_at: res.created_at
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errMsg: ResearchMessage = {
        id: Date.now(),
        session_id: currentSessionId || 0,
        role: 'assistant',
        message_text: "Not Found in the available documents. Please try a different question or add more source documents.",
        retrieval_confidence: 0.1,
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsAnswering(false);
    }
  };

  // Filter available reports based on search query
  const filteredReports = availableReports.filter((doc) => {
    if (!reportSearchQuery.trim()) return true;
    const q = reportSearchQuery.toLowerCase();
    return (
      (doc.title && doc.title.toLowerCase().includes(q)) ||
      (doc.mission_name && doc.mission_name.toLowerCase().includes(q)) ||
      (doc.space_agency && doc.space_agency.toLowerCase().includes(q))
    );
  });

  const selectedReport = selectedReportId === 'all'
    ? null
    : availableReports.find((r) => r.id === selectedReportId);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isAnswering]);

  // Extract last assistant message for Voice Output
  const lastAssistantMsg = [...messages].reverse().find((m) => m.role === 'assistant')?.message_text;

  return (
    <div className="h-[calc(100vh-4rem)] flex overflow-hidden">
      {/* Sessions Sidebar (Left) */}
      <div className="w-72 border-r border-space-700 bg-space-900/40 p-4 flex flex-col justify-between hidden md:flex shrink-0">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
              Research Sessions
            </span>
            <button
              onClick={handleNewSession}
              className="p-1.5 rounded-lg bg-space-850 hover:bg-space-800 text-cosmic-purple border border-space-700 hover:border-cosmic-purple transition-all"
              title="New Investigation"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-1.5 overflow-y-auto max-h-[calc(100vh-14rem)] pr-1">
            {sessions.map((s) => (
              <div
                key={s.id}
                onClick={() => loadSessionDetails(s.id)}
                className={`group flex items-center justify-between p-2.5 rounded-xl text-xs transition-all cursor-pointer ${
                  currentSessionId === s.id
                    ? 'bg-cosmic-purple/15 text-white border border-cosmic-purple/40 font-semibold'
                    : 'text-slate-400 hover:bg-space-850 hover:text-slate-200 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <MessageSquare className="w-3.5 h-3.5 shrink-0 text-cosmic-purple" />
                  <span className="truncate">{s.title}</span>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(e, s.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 transition-opacity"
                  title="Delete Session"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="p-3 rounded-xl bg-space-850 border border-space-750 text-[11px] text-slate-400 font-mono">
          <div className="flex items-center gap-1.5 text-cosmic-cyan mb-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span className="font-bold">EVIDENCE GROUNDING</span>
          </div>
          <p className="text-[10px] text-slate-500 leading-tight">
            Unsupported queries trigger standard "Not Found" response to prevent hallucination.
          </p>
        </div>
      </div>

      {/* Main Research Chat Window */}
      <div className="flex-1 flex flex-col bg-space-950 overflow-hidden relative">
        {/* Chat Header */}
        <div className="px-6 py-3 border-b border-space-800 bg-space-900/40 flex items-center justify-between shrink-0 relative z-30">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-cosmic-purple/20 border border-cosmic-purple/40 flex items-center justify-center">
              <Brain className="w-4 h-4 text-cosmic-purple" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">AI Mission Investigation Assistant</h3>
              <p className="text-[10px] font-mono text-slate-400">RAG Grounded on NASA & ISRO Technical Documents</p>
            </div>

            {/* Slide-Down Report Scope Selector Button & Menu */}
            <div className="relative ml-3" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setIsReportDropdownOpen(!isReportDropdownOpen)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all cursor-pointer shadow-sm ${
                  selectedReportId === 'all'
                    ? 'bg-space-850 hover:bg-space-800 text-slate-200 border-space-700 hover:border-cosmic-purple/60'
                    : 'bg-cosmic-purple/15 text-white border-cosmic-purple/50 hover:bg-cosmic-purple/25'
                }`}
                title="Select a specific report to query or choose 'Select All Reports'"
              >
                <Layers className={`w-3.5 h-3.5 ${selectedReportId === 'all' ? 'text-cosmic-cyan' : 'text-cosmic-purple'}`} />
                <span className="max-w-[190px] truncate font-semibold">
                  {selectedReportId === 'all'
                    ? 'Select All Reports'
                    : (selectedReport?.mission_name || selectedReport?.title || `Report #${selectedReportId}`)}
                </span>
                {selectedReportId !== 'all' && selectedReport?.space_agency && (
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-space-800 text-cosmic-purple font-mono uppercase font-bold border border-cosmic-purple/30">
                    {selectedReport.space_agency}
                  </span>
                )}
                <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${isReportDropdownOpen ? 'rotate-180 text-cosmic-purple' : ''}`} />
              </button>

              {/* Slide-Down Reports Dropdown Menu */}
              {isReportDropdownOpen && (
                <div className="absolute left-0 mt-2 w-96 rounded-2xl bg-space-900 border border-space-700 shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
                  {/* Header & Filter Search Input */}
                  <div className="p-3 border-b border-space-800 bg-space-950/80">
                    <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                      <span>Investigation Document Scope</span>
                      <span className="text-cosmic-cyan font-bold">{availableReports.length} Reports</span>
                    </div>
                    <div className="relative">
                      <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
                      <input
                        type="text"
                        value={reportSearchQuery}
                        onChange={(e) => setReportSearchQuery(e.target.value)}
                        placeholder="Search reports by mission, title, agency..."
                        className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-space-850 border border-space-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cosmic-purple"
                        autoFocus
                      />
                    </div>
                  </div>

                  {/* Scrollable Reports List */}
                  <div className="max-h-72 overflow-y-auto p-1.5 space-y-1">
                    {/* Primary Option: "Select All Reports" */}
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedReportId('all');
                        setIsReportDropdownOpen(false);
                      }}
                      className={`w-full flex items-center justify-between p-2.5 rounded-xl text-left transition-all cursor-pointer ${
                        selectedReportId === 'all'
                          ? 'bg-cosmic-purple/20 border border-cosmic-purple/50 text-white'
                          : 'hover:bg-space-850 text-slate-300 border border-transparent'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <div className="w-7 h-7 rounded-lg bg-cosmic-cyan/15 border border-cosmic-cyan/30 flex items-center justify-center shrink-0">
                          <Layers className="w-3.5 h-3.5 text-cosmic-cyan" />
                        </div>
                        <div>
                          <div className="text-xs font-bold text-white flex items-center gap-1.5">
                            <span>Select All Reports</span>
                            <span className="text-[9px] font-mono text-cosmic-cyan px-1.5 py-0.2 rounded bg-cosmic-cyan/10 border border-cosmic-cyan/20">
                              Global RAG
                            </span>
                          </div>
                          <p className="text-[10px] text-slate-400 leading-tight mt-0.5">
                            Search across all uploaded NASA & ISRO mission reports simultaneously
                          </p>
                        </div>
                      </div>
                      {selectedReportId === 'all' && (
                        <Check className="w-4 h-4 text-cosmic-cyan shrink-0 ml-2" />
                      )}
                    </button>

                    <div className="my-1 border-t border-space-800" />

                    {/* Individual Uploaded Reports */}
                    {filteredReports.map((report) => (
                      <button
                        key={report.id}
                        type="button"
                        onClick={() => {
                          setSelectedReportId(report.id);
                          setIsReportDropdownOpen(false);
                        }}
                        className={`w-full flex items-start justify-between p-2.5 rounded-xl text-left transition-all cursor-pointer ${
                          selectedReportId === report.id
                            ? 'bg-cosmic-purple/20 border border-cosmic-purple/50 text-white'
                            : 'hover:bg-space-850 text-slate-300 border border-transparent'
                        }`}
                      >
                        <div className="flex items-start gap-2.5 min-w-0">
                          <div className="w-7 h-7 rounded-lg bg-space-800 border border-space-700 flex items-center justify-center shrink-0 mt-0.5">
                            <FileText className="w-3.5 h-3.5 text-cosmic-purple" />
                          </div>
                          <div className="min-w-0">
                            <div className="flex items-center gap-1.5">
                              <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-space-750 text-slate-300">
                                {report.space_agency}
                              </span>
                              <span className="text-xs font-semibold text-slate-200 truncate">
                                {report.mission_name || report.title}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-400 truncate mt-0.5" title={report.title}>
                              {report.title}
                            </p>
                            <div className="flex items-center gap-2 mt-1 text-[10px] font-mono text-slate-500">
                              <span>{report.chunk_count || 0} chunks</span>
                              <span>•</span>
                              <span>{report.total_pages || 1} pages</span>
                            </div>
                          </div>
                        </div>
                        {selectedReportId === report.id && (
                          <Check className="w-4 h-4 text-cosmic-purple shrink-0 ml-2 mt-1" />
                        )}
                      </button>
                    ))}

                    {filteredReports.length === 0 && (
                      <div className="p-4 text-center text-xs text-slate-500 font-mono">
                        No matching reports found
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Chat Summary Modal Button */}
            <button
              onClick={() => setIsSummaryOpen(true)}
              disabled={messages.length === 0}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-space-850 hover:bg-space-800 text-xs font-medium text-slate-300 hover:text-white border border-space-700 hover:border-cosmic-purple/60 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
              title={messages.length === 0 ? "Ask questions to view session summary" : "View complete session inquiry summary & audit"}
            >
              <FileText className="w-3.5 h-3.5 text-cosmic-purple" />
              <span>Chat Summary</span>
              {messages.length > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-cosmic-purple/20 text-cosmic-purple text-[10px] font-mono font-bold">
                  {messages.filter(m => m.role === 'user').length}
                </span>
              )}
            </button>

            {/* Quick Download PDF Button */}
            <button
              onClick={handleQuickDownloadPdf}
              disabled={messages.length === 0 || isDownloadingPdf}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cosmic-violet/20 hover:bg-cosmic-violet text-cosmic-purple hover:text-white border border-cosmic-purple/40 hover:border-cosmic-purple text-xs font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer shadow-sm"
              title={messages.length === 0 ? "Ask questions to generate PDF report" : "Download comprehensive PDF report with all inquiries, answers and citations"}
            >
              {isDownloadingPdf ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Exporting...</span>
                </>
              ) : (
                <>
                  <Download className="w-3.5 h-3.5" />
                  <span>Download PDF</span>
                </>
              )}
            </button>

            <VoiceRecorder
              onTranscribedText={(t) => handleSend(t)}
              lastAssistantAnswer={lastAssistantMsg}
            />
          </div>
        </div>

        {/* Active Scope Notification Banner if a specific report is chosen */}
        {selectedReportId !== 'all' && selectedReport && (
          <div className="px-6 py-2 bg-cosmic-purple/10 border-b border-cosmic-purple/30 flex items-center justify-between text-xs text-slate-300 animate-in fade-in">
            <div className="flex items-center gap-2 min-w-0">
              <span className="w-2 h-2 rounded-full bg-cosmic-purple animate-pulse shrink-0" />
              <span className="font-bold text-white shrink-0">Active Report Scope:</span>
              <span className="text-cosmic-cyan font-semibold truncate max-w-lg">
                {selectedReport.title} {selectedReport.mission_name ? `(${selectedReport.mission_name})` : ''}
              </span>
              <span className="text-[10px] font-mono text-slate-400 px-2 py-0.5 rounded bg-space-850 border border-space-700 shrink-0">
                {selectedReport.chunk_count || 0} chunks • {selectedReport.total_pages || 1} pages
              </span>
            </div>
            <button
              onClick={() => setSelectedReportId('all')}
              className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 px-2.5 py-1 rounded-lg bg-space-850 hover:bg-space-800 border border-space-700 hover:border-cosmic-purple/50 transition-colors cursor-pointer shrink-0 ml-3"
              title="Reset scope to search all reports"
            >
              <span>Reset to All Reports</span>
              <X className="w-3 h-3 text-slate-400 hover:text-rose-400" />
            </button>
          </div>
        )}

        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="max-w-2xl mx-auto py-12 text-center space-y-6 animate-in fade-in">
              <div className="w-16 h-16 rounded-3xl bg-cosmic-purple/10 border border-cosmic-purple/30 flex items-center justify-center mx-auto shadow-xl">
                <Sparkles className="w-8 h-8 text-cosmic-purple" />
              </div>
              <div>
                <h3 className="text-lg font-extrabold text-white">Aerospace Technical Inquiries</h3>
                <p className="text-xs text-slate-400 max-w-md mx-auto mt-1 leading-relaxed">
                  Ask technical questions regarding historical NASA and ISRO mission failures. Every claim is cited with the original document and page number.
                </p>
              </div>

              {/* Suggested Questions Grid */}
              <div className="text-left space-y-2 max-w-xl mx-auto">
                <p className="text-[10px] font-mono font-semibold text-slate-500 uppercase tracking-wider text-center mb-2">
                  Recommended Investigation Queries
                </p>
                <div className="grid grid-cols-1 gap-2">
                  {SUGGESTED_QUESTIONS.map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSend(q)}
                      className="p-3 rounded-xl bg-space-900 border border-space-750 hover:border-cosmic-purple/50 hover:bg-space-850 text-xs text-slate-300 hover:text-white transition-all text-left flex items-center justify-between group cursor-pointer"
                    >
                      <span>{q}</span>
                      <Send className="w-3.5 h-3.5 text-slate-500 group-hover:text-cosmic-purple transition-colors shrink-0 ml-2" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-3 max-w-4xl ${m.role === 'user' ? 'ml-auto justify-end' : 'mr-auto justify-start'}`}
              >
                {m.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-lg bg-cosmic-purple/20 border border-cosmic-purple/30 flex items-center justify-center shrink-0 mt-1">
                    <Brain className="w-4 h-4 text-cosmic-purple" />
                  </div>
                )}

                <div
                  className={`p-5 rounded-2xl ${
                    m.role === 'user'
                      ? 'bg-cosmic-violet text-white shadow-md shadow-purple-600/10 max-w-xl'
                      : 'bg-space-900 border border-space-750 text-slate-200 shadow-xl w-full'
                  }`}
                >
                  {/* Assistant Message Header with Confidence Indicator */}
                  {m.role === 'assistant' && m.retrieval_confidence !== undefined && (
                    <div className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-3 border-b border-space-800">
                      <ConfidenceIndicator
                        confidence={m.retrieval_confidence}
                        confidenceDetails={m.confidence_details}
                      />
                      {m.active_mission ? (
                        <span className="text-[10px] font-mono text-cosmic-cyan px-2 py-0.5 rounded bg-cosmic-purple/10 border border-cosmic-purple/30 font-bold">
                          Mission Context: {m.active_mission}
                        </span>
                      ) : (
                        <span className="text-[10px] font-mono text-slate-500">
                          Evidence Grounded
                        </span>
                      )}
                    </div>
                  )}

                  {/* Message Content */}
                  <div className="text-xs leading-relaxed whitespace-pre-line space-y-2">
                    {m.message_text}
                  </div>

                  {/* Grounded Citation Badges */}
                  {m.citations && m.citations.length > 0 && (
                    <CitationList
                      citations={m.citations}
                      onSelectCitation={(cit) => setSelectedCitation(cit)}
                    />
                  )}
                </div>
              </div>
            ))
          )}

          {isAnswering && (
            <div className="flex items-center gap-3 max-w-md">
              <div className="w-8 h-8 rounded-lg bg-cosmic-purple/20 border border-cosmic-purple/30 flex items-center justify-center shrink-0 animate-pulse">
                <Brain className="w-4 h-4 text-cosmic-purple" />
              </div>
              <div className="p-4 rounded-2xl bg-space-900 border border-space-750 flex items-center gap-3">
                <span className="w-3.5 h-3.5 border-2 border-cosmic-purple/30 border-t-cosmic-purple rounded-full animate-spin"></span>
                <span className="text-xs text-slate-400 font-mono">Retrieving evidence chunks & verifying citations...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-space-800 bg-space-900/60 shrink-0">
          <form
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            className="max-w-4xl mx-auto flex items-center gap-2"
          >
            <input
              type="text"
              value={inputQuestion}
              onChange={(e) => setInputQuestion(e.target.value)}
              placeholder={
                selectedReportId === 'all'
                  ? "Ask technical question across all uploaded reports (e.g., 'What went wrong with thermal control on past space probes?')..."
                  : `Ask question specifically from ${selectedReport?.mission_name || selectedReport?.title}...`
              }
              className="flex-1 px-4 py-3 rounded-xl bg-space-850 border border-space-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cosmic-purple transition-colors"
            />
            <button
              type="submit"
              disabled={!inputQuestion.trim() || isAnswering}
              className="p-3 rounded-xl bg-cosmic-violet hover:bg-cosmic-purple text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all cursor-pointer shadow-md shadow-purple-600/20"
              title="Submit Inquiry"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="max-w-4xl mx-auto mt-2 flex items-center justify-between text-[10px] text-slate-500 font-mono">
            <span>NASA NTRS & ISRO FAC Document Index Active</span>
            <span>Page-Level Citations Mandated</span>
          </div>
        </div>
      </div>

      {/* PDF Citation Viewer Modal */}
      {selectedCitation && (
        <PDFViewer
          citation={selectedCitation}
          onClose={() => setSelectedCitation(null)}
        />
      )}

      {/* Investigation Session Chat Summary Modal */}
      <ChatSummaryModal
        sessionId={currentSessionId}
        isOpen={isSummaryOpen}
        onClose={() => setIsSummaryOpen(false)}
        onSelectCitation={(cit) => setSelectedCitation(cit)}
      />
    </div>
  );
};
