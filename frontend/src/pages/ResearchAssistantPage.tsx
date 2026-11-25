import React, { useState, useEffect, useRef } from 'react';
import {
  Send, Brain, Sparkles, MessageSquare, Plus, Trash2,
  FileText, ShieldCheck, Gauge, AlertCircle, RefreshCw
} from 'lucide-react';
import { chatService } from '../services/api';
import { ResearchSession, ResearchMessage, CitationItem } from '../types';
import { ConfidenceIndicator } from '../components/chat/ConfidenceIndicator';
import { CitationList } from '../components/chat/CitationList';
import { VoiceRecorder } from '../components/voice/VoiceRecorder';
import { PDFViewer } from '../components/documents/PDFViewer';
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load research sessions
  useEffect(() => {
    loadSessions();
  }, []);

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
        session_id: currentSessionId
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
        <div className="px-6 py-3 border-b border-space-800 bg-space-900/40 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-cosmic-purple/20 border border-cosmic-purple/40 flex items-center justify-center">
              <Brain className="w-4 h-4 text-cosmic-purple" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">AI Mission Investigation Assistant</h3>
              <p className="text-[10px] font-mono text-slate-400">RAG Grounded on NASA & ISRO Technical Documents</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <VoiceRecorder
              onTranscribedText={(t) => handleSend(t)}
              lastAssistantAnswer={lastAssistantMsg}
            />
          </div>
        </div>

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
                      <ConfidenceIndicator confidence={m.retrieval_confidence} />
                      <span className="text-[10px] font-mono text-slate-500">
                        Evidence Grounded
                      </span>
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
              placeholder="Ask technical question (e.g., 'What went wrong with thermal control on past space probes?')..."
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
    </div>
  );
};
