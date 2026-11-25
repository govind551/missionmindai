import React from 'react';
import { Link } from 'react-router-dom';
import {
  Rocket, Shield, FileCheck, Layers, GitFork, FileBarChart,
  Mic, Search, BookOpen, ArrowRight, CheckCircle2, ChevronRight
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-space-950 text-slate-100 flex flex-col justify-between overflow-x-hidden">
      {/* Top Banner & Hero Section */}
      <div className="relative">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-cosmic-purple/10 rounded-full blur-[140px] pointer-events-none"></div>

        <main className="max-w-7xl mx-auto px-6 pt-20 pb-24 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-space-900 border border-space-700 text-xs font-mono text-cosmic-purple mb-8">
            <span className="w-2 h-2 rounded-full bg-cosmic-purple animate-ping"></span>
            <span>AEROSPACE RESEARCH & RETRIEVAL-AUGMENTED GENERATION</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-[1.15] max-w-4xl mx-auto">
            Stop Repeating Past Mission Failures. Learn From Every Documented Anomaly.
          </h1>

          <p className="mt-6 text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            MISSIONMIND AI indexes official <b className="text-slate-200">NASA</b> and <b className="text-slate-200">ISRO</b> mishap investigation reports, retrieving verified evidence, generating grounded answers, and providing exact page-level citations.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/assistant"
              className="px-6 py-3.5 rounded-xl bg-cosmic-violet hover:bg-cosmic-purple text-white text-sm font-semibold shadow-lg shadow-purple-600/30 transition-all flex items-center gap-2.5 group"
            >
              <span>Launch Research Assistant</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/similar-failures"
              className="px-6 py-3.5 rounded-xl bg-space-850 hover:bg-space-800 text-slate-200 hover:text-white border border-space-700 text-sm font-semibold transition-all flex items-center gap-2"
            >
              <span>Similar Past Failures</span>
            </Link>
          </div>

          {/* NASA & ISRO Public Document Badges */}
          <div className="mt-16 pt-10 border-t border-space-850 flex flex-wrap items-center justify-center gap-8 text-xs font-mono text-slate-500">
            <span className="uppercase tracking-widest text-[11px] font-semibold text-slate-400">Indexed Knowledge Repositories:</span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> NASA Technical Reports Server (NTRS)
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> ISRO Flight Anomaly Committee Reports
            </span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> NASA Lessons Learned Information System (LLIS)
            </span>
          </div>
        </main>
      </div>

      {/* Why MISSIONMIND AI Is Needed (Problem Statement) */}
      <section className="bg-space-900/60 border-y border-space-800 py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
              The Critical Aerospace Knowledge Problem
            </h2>
            <p className="mt-3 text-sm text-slate-400 leading-relaxed">
              Engineers often repeat past design errors because mission lessons are buried in hundreds of lengthy technical PDFs.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-space-950/70 border border-space-750 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 font-mono font-bold">
                01
              </div>
              <h3 className="text-base font-bold text-white">Keyword Search Blindspots</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Traditional keyword searches miss critical semantic context, synonyms, and cross-subsystem dependencies.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-space-950/70 border border-space-750 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 font-mono font-bold">
                02
              </div>
              <h3 className="text-base font-bold text-white">Generic AI Hallucinations</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Generic chatbots hallucinate mission facts, fabricate page numbers, or guess unverified technical numbers.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-space-950/70 border border-space-750 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-cosmic-purple/10 border border-cosmic-purple/20 flex items-center justify-center text-cosmic-purple font-mono font-bold">
                03
              </div>
              <h3 className="text-base font-bold text-white">Evidence-Grounded RAG Solution</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                MISSIONMIND strictly cites original NASA and ISRO investigation pages. If not documented, it says "Not Found".
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center max-w-xl mx-auto mb-16">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
            Core Engineering Architecture
          </h2>
          <p className="mt-2 text-xs sm:text-sm text-slate-400">
            Built for mission designers, flight safety directors, and aerospace research scholars.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-space-900 border border-space-700 space-y-3">
            <BookOpen className="w-6 h-6 text-cosmic-purple" />
            <h3 className="text-sm font-bold text-white">Page-Aware PDF Ingestion</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              PyMuPDF preserves exact page numbers and document titles across multi-volume mishap investigation reports.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-space-900 border border-space-700 space-y-3">
            <Shield className="w-6 h-6 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">Clickable Citation Viewer</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Clicking a citation automatically opens the embedded PDF and navigates straight to the cited page.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-space-900 border border-space-700 space-y-3">
            <Layers className="w-6 h-6 text-cosmic-cyan" />
            <h3 className="text-sm font-bold text-white">Similar Past Failures</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Describe an engineering design dilemma; receive ranked historical mission anomalies with real similarity scores.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-space-900 border border-space-700 space-y-3">
            <GitFork className="w-6 h-6 text-amber-400" />
            <h3 className="text-sm font-bold text-white">Failure Chain Reconstruction</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Interactive causal timeline distinguishing confirmed root causes, cascading events, and mission impacts.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-space-900 border border-space-700 space-y-3">
            <Mic className="w-6 h-6 text-rose-400" />
            <h3 className="text-sm font-bold text-white">Voice Interaction (STT & TTS)</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Speak complex questions hands-free and listen to grounded technical answers using speech synthesis.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-space-900 border border-space-700 space-y-3">
            <FileBarChart className="w-6 h-6 text-cosmic-violet" />
            <h3 className="text-sm font-bold text-white">Smart PDF Research Reports</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Export entire research sessions into publication-grade ReportLab PDF reports with citations and timelines.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-space-800 bg-space-950 py-8 px-6 text-center text-xs text-slate-500 font-mono">
        <p>MISSIONMIND AI // Space Mission Lessons-Learned Assistant with Cited Answers</p>
        <p className="mt-1 text-[11px] text-slate-600">Built for Aerospace Safety, Research, and Engineering Education.</p>
      </footer>
    </div>
  );
};
