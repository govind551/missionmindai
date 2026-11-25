import React, { useState } from 'react';
import { X, ExternalLink, ChevronLeft, ChevronRight, FileText, CheckCircle2 } from 'lucide-react';
import { CitationItem } from '../../types';
import { documentService } from '../../services/api';

interface PDFViewerProps {
  citation: CitationItem | null;
  documentId?: number;
  initialPage?: number;
  onClose: () => void;
}

export const PDFViewer: React.FC<PDFViewerProps> = ({
  citation,
  documentId,
  initialPage = 1,
  onClose
}) => {
  const docId = citation ? citation.document_id : documentId;
  const targetPage = citation ? citation.page_number : initialPage;
  const [currentPage, setCurrentPage] = useState<number>(targetPage);

  if (!docId) return null;

  const pdfUrl = documentService.getPdfUrl(docId);
  const pdfViewUrlWithPage = `${pdfUrl}#page=${currentPage}`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-6xl h-[92vh] bg-space-900 border border-space-700 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header Bar */}
        <div className="px-6 py-3.5 border-b border-space-700 bg-space-850/90 flex items-center justify-between">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-cosmic-purple/20 border border-cosmic-purple/30 flex items-center justify-center shrink-0">
              <FileText className="w-4 h-4 text-cosmic-purple" />
            </div>
            <div className="truncate">
              <h3 className="text-sm font-bold text-white truncate">
                {citation?.document_title || "Official Aerospace Investigation Report"}
              </h3>
              <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                <span className="font-mono text-cosmic-cyan">Mission: {citation?.mission_name || "NASA / ISRO"}</span>
                <span>•</span>
                <span className="text-amber-400 font-semibold">Active Cited Page: {currentPage}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            {citation?.source_url && (
              <a
                href={citation.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 text-xs text-slate-300 hover:text-white transition-colors border border-space-700"
              >
                <span>Original Source</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-space-800 transition-colors"
              title="Close Viewer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Cited Evidence Callout Banner */}
        {citation && (
          <div className="px-6 py-2.5 bg-cosmic-purple/10 border-b border-cosmic-purple/20 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>
                <b>Verified Finding:</b> "{citation.snippet}"
              </span>
            </div>
            <div className="flex items-center gap-2 text-slate-400 font-mono text-[11px] shrink-0 ml-4">
              <span>Section: {citation.section_heading || "Technical Findings"}</span>
            </div>
          </div>
        )}

        {/* Main PDF Frame */}
        <div className="flex-1 w-full bg-space-950 relative">
          <iframe
            src={pdfViewUrlWithPage}
            title="NASA/ISRO Technical Document"
            className="w-full h-full border-0"
          />
        </div>

        {/* Footer Page Navigation */}
        <div className="px-6 py-2.5 border-t border-space-800 bg-space-850 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="px-2.5 py-1 rounded bg-space-800 hover:bg-space-700 text-slate-300 flex items-center gap-1"
            >
              <ChevronLeft className="w-3.5 h-3.5" /> Prev
            </button>
            <span className="font-mono text-slate-200">Page {currentPage}</span>
            <button
              onClick={() => setCurrentPage((p) => p + 1)}
              className="px-2.5 py-1 rounded bg-space-800 hover:bg-space-700 text-slate-300 flex items-center gap-1"
            >
              Next <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <span className="font-mono text-[11px] text-slate-500">
            MISSIONMIND Evidence Inspector // Page Sync Active
          </span>
        </div>
      </div>
    </div>
  );
};
