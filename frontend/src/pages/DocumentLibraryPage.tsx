import React, { useState, useEffect } from 'react';
import {
  FileText, Upload, Search, Filter, ExternalLink, RefreshCw,
  Trash2, CheckCircle2, AlertTriangle, Eye, Plus
} from 'lucide-react';
import { documentService } from '../services/api';
import { DocumentItem } from '../types';
import { PDFViewer } from '../components/documents/PDFViewer';
import { Modal } from '../components/common/Modal';
import { Button } from '../components/common/Button';
import { Loader } from '../components/common/Loader';
import { ErrorMessage } from '../components/common/ErrorMessage';

export const DocumentLibraryPage: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [agencyFilter, setAgencyFilter] = useState('');
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);

  // Upload modal state
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadMission, setUploadMission] = useState('');
  const [uploadAgency, setUploadAgency] = useState('NASA');
  const [uploadYear, setUploadYear] = useState<string>('2024');
  const [uploadDocType, setUploadDocType] = useState('Mishap Investigation Report');
  const [uploadSourceUrl, setUploadSourceUrl] = useState('');
  const [uploadLicence, setUploadLicence] = useState('Public Domain / Official Government Release');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await documentService.getDocuments({
        agency: agencyFilter || undefined,
        search: searchTerm || undefined
      });
      setDocuments(data);
    } catch (err) {
      console.warn("Error fetching documents:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) {
      setUploadError("Please select a PDF report to upload.");
      return;
    }
    setUploadError('');
    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('title', uploadTitle);
      formData.append('mission_name', uploadMission);
      formData.append('space_agency', uploadAgency);
      if (uploadYear) formData.append('publication_year', uploadYear);
      formData.append('document_type', uploadDocType);
      if (uploadSourceUrl) formData.append('source_url', uploadSourceUrl);
      formData.append('licence', uploadLicence);

      await documentService.uploadDocument(formData);
      setIsUploadModalOpen(false);
      resetUploadForm();
      loadDocuments();
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || "Upload or PDF ingestion failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const resetUploadForm = () => {
    setUploadFile(null);
    setUploadTitle('');
    setUploadMission('');
    setUploadAgency('NASA');
    setUploadYear('2024');
    setUploadSourceUrl('');
    setUploadError('');
  };

  const handleDelete = async (docId: number) => {
    if (!window.confirm("Are you sure you want to delete this indexed document and all its vector chunks?")) return;
    try {
      await documentService.deleteDocument(docId);
      setDocuments(documents.filter((d) => d.id !== docId));
    } catch (err) {
      console.warn("Delete failed:", err);
    }
  };

  const handleReprocess = async (docId: number) => {
    try {
      await documentService.reprocess(docId);
      loadDocuments();
    } catch (err) {
      console.warn("Reprocess failed:", err);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Top Banner */}
      <div className="p-6 rounded-3xl bg-space-900 border border-space-700 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <FileText className="w-4 h-4 text-cosmic-purple" />
            <span className="text-xs font-mono font-bold text-cosmic-purple uppercase tracking-wider">
              OFFICIAL INVESTIGATION REPOSITORY
            </span>
          </div>
          <h2 className="text-2xl font-black text-white">
            Mission Document Library
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Public NASA and ISRO technical mishap reports. PyMuPDF extracts text, preserves page bounds, and pgvector indexes 384-dimensional dense vectors.
          </p>
        </div>

        <Button
          variant="primary"
          onClick={() => setIsUploadModalOpen(true)}
          icon={<Plus className="w-4 h-4" />}
          className="text-xs font-bold px-4 py-2.5"
        >
          Upload PDF Report
        </Button>
      </div>

      {/* Search & Agency Filter */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-space-900 border border-space-750">
        <div className="flex-1 min-w-[240px] relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadDocuments()}
            placeholder="Search documents by mission, anomaly, or title..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cosmic-purple transition-colors"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={agencyFilter}
            onChange={(e) => setAgencyFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-slate-300 focus:outline-none focus:border-cosmic-purple transition-colors cursor-pointer"
          >
            <option value="">All Space Agencies</option>
            <option value="NASA">NASA Reports</option>
            <option value="ISRO">ISRO Reports</option>
          </select>

          <Button variant="secondary" onClick={loadDocuments} icon={<RefreshCw className="w-3.5 h-3.5" />}>
            Refresh
          </Button>
        </div>
      </div>

      {/* Document Grid */}
      {loading ? (
        <Loader message="Loading document repository..." />
      ) : documents.length === 0 ? (
        <div className="p-12 text-center rounded-3xl bg-space-900 border border-space-700 text-xs text-slate-400 space-y-2">
          <FileText className="w-8 h-8 text-slate-500 mx-auto" />
          <p className="text-slate-300 font-semibold">No technical documents match your criteria.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="p-5 rounded-2xl bg-space-900 border border-space-700 hover:border-cosmic-purple/50 transition-all flex flex-col justify-between space-y-4 shadow-lg group"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-space-800 text-cosmic-purple border border-space-700 font-bold uppercase">
                    {doc.space_agency}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    {doc.publication_year || 'Historical'}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-white group-hover:text-cosmic-purple transition-colors line-clamp-2">
                  {doc.title}
                </h4>

                <div className="mt-2 text-xs font-mono text-cosmic-cyan">
                  Mission: {doc.mission_name}
                </div>

                <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono">
                  <div className="p-2 rounded-lg bg-space-850 border border-space-800">
                    <span className="text-slate-500 block text-[9px] uppercase">PAGES</span>
                    <span className="text-slate-200 font-bold">{doc.total_pages}</span>
                  </div>
                  <div className="p-2 rounded-lg bg-space-850 border border-space-800">
                    <span className="text-slate-500 block text-[9px] uppercase">CHUNKS</span>
                    <span className="text-slate-200 font-bold">{doc.chunk_count}</span>
                  </div>
                </div>

                {doc.licence && (
                  <p className="mt-3 text-[10px] text-slate-500 italic truncate">
                    Licence: {doc.licence}
                  </p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="pt-3 border-t border-space-800 flex items-center justify-between text-xs">
                <button
                  onClick={() => setSelectedDocId(doc.id)}
                  className="px-3 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 text-cosmic-purple hover:text-white flex items-center gap-1.5 font-semibold transition-all cursor-pointer"
                >
                  <Eye className="w-3.5 h-3.5" /> Inspect PDF
                </button>

                <div className="flex items-center space-x-1">
                  {doc.source_url && (
                    <a
                      href={doc.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-space-800 transition-colors"
                      title="Open Official Web Source"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-space-800 transition-colors"
                    title="Delete Document"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* PDF Viewer Modal */}
      {selectedDocId && (
        <PDFViewer
          citation={null}
          documentId={selectedDocId}
          initialPage={1}
          onClose={() => setSelectedDocId(null)}
        />
      )}

      {/* Upload PDF Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload NASA / ISRO Technical Report"
        subtitle="Extracts text with PyMuPDF, chunks pages, and indexes vectors into PostgreSQL/pgvector"
      >
        <form onSubmit={handleUploadSubmit} className="space-y-4">
          {uploadError && <ErrorMessage message={uploadError} />}

          <div>
            <label className="block text-xs font-mono font-bold text-slate-300 mb-1">PDF FILE *</label>
            <input
              type="file"
              accept=".pdf"
              required
              onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
              className="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-cosmic-purple/20 file:text-cosmic-purple hover:file:bg-cosmic-purple/30 cursor-pointer"
            />
          </div>

          <div>
            <label className="block text-xs font-mono font-bold text-slate-300 mb-1">DOCUMENT TITLE *</label>
            <input
              type="text"
              required
              value={uploadTitle}
              onChange={(e) => setUploadTitle(e.target.value)}
              placeholder="e.g., Mars Climate Orbiter Mishap Investigation Board Report"
              className="w-full px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-mono font-bold text-slate-300 mb-1">MISSION NAME *</label>
              <input
                type="text"
                required
                value={uploadMission}
                onChange={(e) => setUploadMission(e.target.value)}
                placeholder="e.g., Mars Climate Orbiter"
                className="w-full px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple"
              />
            </div>
            <div>
              <label className="block text-xs font-mono font-bold text-slate-300 mb-1">SPACE AGENCY *</label>
              <select
                value={uploadAgency}
                onChange={(e) => setUploadAgency(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple cursor-pointer"
              >
                <option value="NASA">NASA</option>
                <option value="ISRO">ISRO</option>
                <option value="ESA">ESA</option>
                <option value="JAXA">JAXA</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-mono font-bold text-slate-300 mb-1">PUBLICATION YEAR</label>
              <input
                type="number"
                value={uploadYear}
                onChange={(e) => setUploadYear(e.target.value)}
                placeholder="1999"
                className="w-full px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple"
              />
            </div>
            <div>
              <label className="block text-xs font-mono font-bold text-slate-300 mb-1">DOCUMENT TYPE</label>
              <input
                type="text"
                value={uploadDocType}
                onChange={(e) => setUploadDocType(e.target.value)}
                placeholder="Mishap Investigation Report"
                className="w-full px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono font-bold text-slate-300 mb-1">ORIGINAL SOURCE URL</label>
            <input
              type="url"
              value={uploadSourceUrl}
              onChange={(e) => setUploadSourceUrl(e.target.value)}
              placeholder="https://ntrs.nasa.gov/citations/..."
              className="w-full px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple"
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-space-800">
            <Button variant="secondary" onClick={() => setIsUploadModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={isUploading}>
              Ingest & Index Report
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
