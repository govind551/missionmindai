import React, { useState, useEffect } from 'react';
import { Layers, Search, Sparkles, AlertCircle, FileText, ArrowRight, ShieldCheck } from 'lucide-react';
import { failureService } from '../services/api';
import { FailureIncident } from '../types';
import { FailureCard } from '../components/failure/FailureCard';
import { PDFViewer } from '../components/documents/PDFViewer';
import { Loader } from '../components/common/Loader';
import { Button } from '../components/common/Button';

export const SimilarFailuresPage: React.FC = () => {
  const [problemDescription, setProblemDescription] = useState(
    "Our spacecraft is experiencing unexpected temperature fluctuations in the thermal control subsystem."
  );
  const [subsystemFilter, setSubsystemFilter] = useState('');
  const [agencyFilter, setAgencyFilter] = useState('');
  const [results, setResults] = useState<FailureIncident[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<{ docId: number; pageNum: number } | null>(null);

  // Initial load
  useEffect(() => {
    handleSearch();
  }, []);

  const handleSearch = async () => {
    if (!problemDescription.trim()) return;
    setIsSearching(true);
    try {
      const data = await failureService.findSimilar({
        problem_description: problemDescription,
        subsystem: subsystemFilter || undefined,
        agency: agencyFilter || undefined,
        top_k: 5
      });
      setResults(data);
    } catch (err) {
      console.warn("Failed retrieving similar failures:", err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleInspect = (docId: number, pageNum: number) => {
    setSelectedCitation({ docId, pageNum });
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Header Banner */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Layers className="w-4 h-4 text-cosmic-cyan" />
            <span className="text-xs font-mono font-bold text-cosmic-cyan uppercase tracking-wider">
              FAILURE INTELLIGENCE ENGINE
            </span>
          </div>
          <h2 className="text-2xl font-black text-white">
            Similar Past Failures & Precedent Matching
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Describe a current aerospace anomaly or design challenge. The system searches historical mission mishap investigation records and ranks matching incidents by vector similarity.
          </p>
        </div>

        <div className="p-3 rounded-xl bg-space-850 border border-space-750 text-xs font-mono text-slate-400 shrink-0">
          <div className="text-cosmic-purple font-bold">ACTUAL SIMILARITY SCORING</div>
          <p className="text-[10px] text-slate-500">Dense Cosine Similarity + Subsystem Overlap</p>
        </div>
      </div>

      {/* Query Input Box */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 space-y-4 shadow-xl">
        <div>
          <label className="block text-xs font-mono font-bold text-slate-300 mb-2 uppercase tracking-wider">
            Current Engineering Issue / Anomaly Description
          </label>
          <textarea
            rows={3}
            value={problemDescription}
            onChange={(e) => setProblemDescription(e.target.value)}
            placeholder="Describe the technical symptom (e.g., 'Our spacecraft is experiencing unexpected temperature fluctuations in the thermal control subsystem')..."
            className="w-full p-4 rounded-2xl bg-space-850 border border-space-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cosmic-cyan transition-colors"
          />
        </div>

        {/* Filters and Action Button */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
          <div className="flex flex-wrap items-center gap-3">
            <div>
              <select
                value={subsystemFilter}
                onChange={(e) => setSubsystemFilter(e.target.value)}
                className="px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-slate-300 focus:outline-none focus:border-cosmic-cyan transition-colors cursor-pointer"
              >
                <option value="">All Subsystems</option>
                <option value="Thermal">Thermal Control</option>
                <option value="Propulsion">Propulsion / Cryogenic</option>
                <option value="Guidance">Guidance, Navigation & Software</option>
                <option value="Structures">Structures & Fairings</option>
                <option value="Electrical">Electrical & Avionics</option>
              </select>
            </div>

            <div>
              <select
                value={agencyFilter}
                onChange={(e) => setAgencyFilter(e.target.value)}
                className="px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-slate-300 focus:outline-none focus:border-cosmic-cyan transition-colors cursor-pointer"
              >
                <option value="">All Space Agencies</option>
                <option value="NASA">NASA</option>
                <option value="ISRO">ISRO</option>
              </select>
            </div>
          </div>

          <Button
            type="button"
            variant="primary"
            onClick={handleSearch}
            isLoading={isSearching}
            icon={<Search className="w-4 h-4" />}
            className="text-xs font-bold px-6 py-2.5"
          >
            Analyze Historical Precedents
          </Button>
        </div>
      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-white">
            Ranked Historical Incident Matches ({results.length})
          </h3>
          <p className="text-xs text-slate-400">
            Sorted strictly by computed vector and semantic relevance score
          </p>
        </div>
      </div>

      {/* Results Grid */}
      {isSearching ? (
        <Loader message="Searching historical failure records & calculating similarity..." />
      ) : results.length === 0 ? (
        <div className="p-12 text-center rounded-3xl bg-space-900 border border-space-700 text-xs text-slate-400 space-y-2">
          <AlertCircle className="w-8 h-8 text-slate-500 mx-auto" />
          <p className="text-slate-300 font-semibold">No similar historical failures found.</p>
          <p className="text-slate-500 text-[11px]">Try adjusting your search terms or subsystem filter.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {results.map((inc) => (
            <FailureCard
              key={inc.id}
              incident={inc}
              onInspectCitation={handleInspect}
            />
          ))}
        </div>
      )}

      {/* Embedded PDF Inspector Modal */}
      {selectedCitation && (
        <PDFViewer
          citation={null}
          documentId={selectedCitation.docId}
          initialPage={selectedCitation.pageNum}
          onClose={() => setSelectedCitation(null)}
        />
      )}
    </div>
  );
};
