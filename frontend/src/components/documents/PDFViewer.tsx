import React, { useState, useEffect } from 'react';
import {
  X, ExternalLink, ChevronLeft, ChevronRight, FileText, CheckCircle2,
  BookmarkCheck, Sparkles, Layout, Eye, Download
} from 'lucide-react';
import { CitationItem } from '../../types';
import { documentService } from '../../services/api';
import { Loader } from '../common/Loader';

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
  const [activeTab, setActiveTab] = useState<'evidence' | 'pdf'>(citation ? 'evidence' : 'pdf');
  const [pageData, setPageData] = useState<any>(null);
  const [loadingPage, setLoadingPage] = useState<boolean>(true);

  // Sync state if citation prop changes
  useEffect(() => {
    if (citation) {
      setCurrentPage(citation.page_number);
    }
  }, [citation]);

  // Load page text & extracted chunks for instant highlight
  useEffect(() => {
    if (!docId) return;
    const fetchPage = async () => {
      setLoadingPage(true);
      try {
        const data = await documentService.getPageContent(docId, currentPage);
        setPageData(data);
      } catch (err) {
        console.warn("Could not fetch page text:", err);
      } finally {
        setLoadingPage(false);
      }
    };
    fetchPage();
  }, [docId, currentPage]);

  if (!docId) return null;

  const pdfUrl = documentService.getPdfUrl(docId);
  // view=FitH and page= anchor instructs PDF viewers to navigate without download
  const pdfViewUrlWithPage = `${pdfUrl}#page=${currentPage}&view=FitH`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-5 bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-6xl h-[94vh] bg-space-900 border border-space-700 rounded-3xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header Bar */}
        <div className="px-6 py-3.5 border-b border-space-700 bg-space-850 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-9 h-9 rounded-xl bg-cosmic-purple/20 border border-cosmic-purple/40 flex items-center justify-center shrink-0">
              <FileText className="w-5 h-5 text-cosmic-purple" />
            </div>
            <div className="truncate">
              <h3 className="text-sm sm:text-base font-bold text-white truncate">
                {citation?.document_title || pageData?.document_title || "Official Investigation Report"}
              </h3>
              <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                <span className="font-mono text-cosmic-cyan font-semibold">
                  {citation?.space_agency || pageData?.space_agency || "AEROSPACE ARCHIVE"} • {citation?.mission_name || pageData?.mission_name || "Space Mission"}
                </span>
                <span>•</span>
                <span className="text-amber-400 font-mono font-bold px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">
                  {citation ? `Page ${currentPage} Cited` : `Page ${currentPage}`}
                </span>
              </div>
            </div>
          </div>

          {/* Mode Switcher & Close */}
          <div className="flex items-center space-x-3 shrink-0">
            {/* View Mode Tabs */}
            <div className="hidden sm:flex items-center p-1 bg-space-950 rounded-xl border border-space-750 text-xs">
              <button
                type="button"
                onClick={() => setActiveTab('evidence')}
                className={`px-3 py-1.5 rounded-lg font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'evidence'
                    ? 'bg-cosmic-purple text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <BookmarkCheck className="w-3.5 h-3.5" />
                <span>Cited Page & Highlight</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('pdf')}
                className={`px-3 py-1.5 rounded-lg font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'pdf'
                    ? 'bg-cosmic-purple text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Original PDF Stream</span>
              </button>
            </div>

            {citation?.source_url && (
              <a
                href={citation.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-space-800 hover:bg-space-750 text-xs text-slate-300 hover:text-white transition-colors border border-space-700"
                title="Open Source URL"
              >
                <span>NTRS / Web</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}

            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-space-800 transition-colors cursor-pointer"
              title="Close Inspector"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Highlighted Evidence Anchor Header */}
        <div className="px-6 py-2.5 bg-gradient-to-r from-space-850 via-space-900 to-space-850 border-b border-space-750 flex flex-wrap items-center justify-between gap-2 shrink-0 text-xs">
          <div className="flex items-center gap-2 text-slate-200">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span className="font-mono text-emerald-400 font-bold uppercase text-[11px]">
              EVIDENCE VERIFIED & ANCHORED:
            </span>
            <span className="text-slate-300 line-clamp-1 italic">
              "{citation?.snippet || "Official technical finding extracted on this page."}"
            </span>
          </div>

          <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400">
            <span className="px-2 py-0.5 rounded bg-space-800 border border-space-700 text-cosmic-purple font-semibold">
              Section: {citation?.section_heading || "Technical Investigation Findings"}
            </span>
          </div>
        </div>

        {/* Content Display Body */}
        <div className="flex-1 overflow-y-auto bg-space-950 p-4 sm:p-6 relative">
          {activeTab === 'evidence' ? (
            <div className="max-w-4xl mx-auto space-y-6">
              {loadingPage ? (
                <div className="py-20">
                  <Loader message={`Loading and rendering official page ${currentPage}...`} />
                </div>
              ) : pageData && pageData.chunks && pageData.chunks.length > 0 ? (
                <div className="space-y-6">
                  {/* Page Banner */}
                  <div className="flex items-center justify-between pb-3 border-b border-space-800 text-xs font-mono">
                    <span className="text-slate-400 uppercase tracking-widest font-bold">
                      OFFICIAL DOCUMENT PAGE {currentPage} // REPORT EXCERPTS
                    </span>
                    <span className="text-cosmic-cyan">
                      {pageData.chunks.length} Section Chunk(s) on Page
                    </span>
                  </div>

                  {/* Chunks rendering with automated highlight of the cited claim */}
                  {pageData.chunks.map((chunk: any, idx: number) => {
                    // Check if this chunk contains the cited evidence snippet
                    const isDirectCitation = citation && (
                      chunk.id === citation.chunk_id ||
                      (citation.snippet && chunk.text.toLowerCase().includes(citation.snippet.slice(0, 30).toLowerCase()))
                    );

                    return (
                      <div
                        key={idx}
                        className={`p-6 rounded-2xl transition-all ${
                          isDirectCitation
                            ? 'bg-amber-500/10 border-2 border-amber-400/80 shadow-xl shadow-amber-500/10 ring-4 ring-amber-400/10'
                            : 'bg-space-900 border border-space-750'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-3">
                          <span className={`text-xs font-mono font-bold tracking-wider uppercase ${
                            isDirectCitation ? 'text-amber-400' : 'text-slate-400'
                          }`}>
                            {chunk.section_heading || `Page ${currentPage} - Section ${idx + 1}`}
                          </span>

                          {isDirectCitation && (
                            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-400/20 text-amber-300 font-mono text-[10px] font-bold border border-amber-400/40 animate-pulse">
                              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                              CITED EVIDENCE ON THIS PAGE
                            </span>
                          )}
                        </div>

                        {/* Chunk Text */}
                        <div className="text-sm leading-relaxed whitespace-pre-line text-slate-200 font-sans">
                          {chunk.text}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="p-12 text-center text-xs text-slate-400">
                  <p>Page text loaded. Switch to "Original PDF Stream" tab to view scanned layout.</p>
                </div>
              )}
            </div>
          ) : (
            /* Original PDF Stream Frame (without triggering download) */
            <div className="w-full h-full min-h-[500px] rounded-2xl overflow-hidden border border-space-800 bg-space-900 relative">
              <iframe
                src={pdfViewUrlWithPage}
                title="Official Investigation PDF"
                className="w-full h-full border-0 absolute inset-0"
              />
            </div>
          )}
        </div>

        {/* Footer Navigation Bar */}
        <div className="px-6 py-3 border-t border-space-800 bg-space-850 flex items-center justify-between text-xs text-slate-400 shrink-0">
          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="px-3 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 text-slate-300 hover:text-white flex items-center gap-1 font-mono transition-colors cursor-pointer"
            >
              <ChevronLeft className="w-3.5 h-3.5" /> Prev Page
            </button>
            <span className="font-mono text-slate-200 px-3 py-1 rounded bg-space-900 border border-space-750">
              Page {currentPage}
            </span>
            <button
              type="button"
              onClick={() => setCurrentPage((p) => p + 1)}
              className="px-3 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 text-slate-300 hover:text-white flex items-center gap-1 font-mono transition-colors cursor-pointer"
            >
              Next Page <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="flex items-center space-x-3">
            <span className="font-mono text-[11px] text-slate-500 hidden sm:inline">
              Instant Citation Anchor Active • No Download Required
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
