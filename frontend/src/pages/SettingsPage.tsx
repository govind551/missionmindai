import React, { useState } from 'react';
import { Settings, Shield, User as UserIcon, Key, Radio, Save, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/common/Button';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const [retrievalThreshold, setRetrievalThreshold] = useState('0.45');
  const [topK, setTopK] = useState('5');
  const [llmProvider, setLlmProvider] = useState('gemini');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-8">
      {/* Header Banner */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 shadow-xl">
        <div className="flex items-center gap-2 mb-1.5">
          <Settings className="w-4 h-4 text-cosmic-purple" />
          <span className="text-xs font-mono font-bold text-cosmic-purple uppercase tracking-wider">
            FLIGHT DECK CONFIGURATION
          </span>
        </div>
        <h2 className="text-2xl font-black text-white">
          System Preferences & Retrieval Thresholds
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Tune confidence rejection margins, vector search top-K, and provider adapters.
        </p>
      </div>

      {savedSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>Investigation parameters updated successfully.</span>
        </div>
      )}

      {/* Profile Card */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 space-y-4 shadow-xl">
        <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
          Active Researcher Profile
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-3.5 rounded-2xl bg-space-850 border border-space-800">
            <span className="text-slate-500 block text-[10px] uppercase">CALLSIGN / NAME</span>
            <span className="text-white font-bold">{user?.name || "Dr. Vikram Sarabhai"}</span>
          </div>
          <div className="p-3.5 rounded-2xl bg-space-850 border border-space-800">
            <span className="text-slate-500 block text-[10px] uppercase">OFFICIAL EMAIL</span>
            <span className="text-white font-bold">{user?.email || "researcher@missionmind.ai"}</span>
          </div>
          <div className="p-3.5 rounded-2xl bg-space-850 border border-space-800">
            <span className="text-slate-500 block text-[10px] uppercase">SECURITY CLEARANCE</span>
            <span className="text-cosmic-purple font-bold uppercase">{user?.role || "analyst"}</span>
          </div>
        </div>
      </div>

      {/* Retrieval Tuning Form */}
      <form onSubmit={handleSave} className="p-6 rounded-3xl bg-space-900 border border-space-700 space-y-6 shadow-xl">
        <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
          Retrieval & Verification Thresholds
        </h3>

        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between text-xs font-mono mb-1.5">
              <label className="text-slate-300 font-bold">
                LOW-CONFIDENCE REJECTION THRESHOLD: <span className="text-cosmic-purple">{retrievalThreshold}</span>
              </label>
              <span className="text-slate-500 text-[11px]">(Default 0.45)</span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.80"
              step="0.05"
              value={retrievalThreshold}
              onChange={(e) => setRetrievalThreshold(e.target.value)}
              className="w-full accent-cosmic-purple cursor-pointer"
            />
            <p className="text-[11px] text-slate-500 mt-1">
              Queries scoring below this threshold strictly return: <i>"Not Found in the available documents"</i> to prevent hallucination.
            </p>
          </div>

          <div>
            <div className="flex items-center justify-between text-xs font-mono mb-1.5">
              <label className="text-slate-300 font-bold">
                TOP-K RETRIEVED CHUNKS: <span className="text-cosmic-cyan">{topK}</span>
              </label>
              <span className="text-slate-500 text-[11px]">(Chunks per Query)</span>
            </div>
            <input
              type="range"
              min="2"
              max="10"
              step="1"
              value={topK}
              onChange={(e) => setTopK(e.target.value)}
              className="w-full accent-cosmic-cyan cursor-pointer"
            />
          </div>

          <div>
            <label className="block text-xs font-mono font-bold text-slate-300 mb-1.5 uppercase">
              LLM SYNTHESIS ADAPTER
            </label>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple cursor-pointer font-mono"
            >
              <option value="gemini">Google Gemini 1.5 Flash (Default Cloud Provider)</option>
              <option value="openai">OpenAI GPT-4o-Mini Adapter</option>
              <option value="grounded_engine">Deterministic Aerospace Grounded Engine (Offline Safe)</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end pt-4 border-t border-space-800">
          <Button type="submit" variant="primary" icon={<Save className="w-4 h-4" />}>
            Save Investigation Config
          </Button>
        </div>
      </form>
    </div>
  );
};
