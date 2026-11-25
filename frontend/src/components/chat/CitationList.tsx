import React from 'react';
import { FileText, ExternalLink, BookmarkCheck } from 'lucide-react';
import { CitationItem } from '../../types';

interface CitationListProps {
  citations: CitationItem[];
  onSelectCitation: (citation: CitationItem) => void;
}

export const CitationList: React.FC<CitationListProps> = ({ citations, onSelectCitation }) => {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-space-700/60">
      <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-slate-400">
        <BookmarkCheck className="w-3.5 h-3.5 text-cosmic-purple" />
        <span>Grounded Document Citations ({citations.length}):</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {citations.map((cit, idx) => (
          <div
            key={idx}
            onClick={() => onSelectCitation(cit)}
            className="p-2.5 rounded-xl bg-space-850/80 border border-space-700 hover:border-cosmic-purple/60 hover:bg-space-800 transition-all cursor-pointer group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between text-[11px] font-mono text-cosmic-purple mb-1">
                <span className="font-bold flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-cosmic-purple" />
                  {cit.space_agency} • Page {cit.page_number}
                </span>
                {cit.score && (
                  <span className="text-[10px] text-slate-400 font-sans">
                    {Math.round(cit.score * 100)}% match
                  </span>
                )}
              </div>
              <p className="text-xs font-medium text-slate-200 line-clamp-1 group-hover:text-white transition-colors">
                {cit.document_title}
              </p>
              <p className="text-[11px] text-slate-400 line-clamp-2 mt-1 italic">
                "{cit.snippet}"
              </p>
            </div>
            <div className="mt-2 pt-1.5 border-t border-space-750 flex items-center justify-between text-[10px] text-slate-400">
              <span className="text-cosmic-cyan flex items-center gap-1">
                Click to inspect cited page →
              </span>
              {cit.source_url && (
                <a
                  href={cit.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="hover:text-slate-200 flex items-center gap-0.5"
                  title="Open source URL"
                >
                  Source <ExternalLink className="w-2.5 h-2.5" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
