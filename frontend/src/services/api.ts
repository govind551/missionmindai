import axios from 'axios';
import {
  User, CitationItem, ResearchMessage, ResearchSession,
  DocumentItem, FailureIncident, FailureChain,
  GeneratedReportItem, SystemStats, SessionSummaryData
} from '../types';

const API_BASE = '/api';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token if present
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('missionmind_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Authentication
export const authService = {
  async register(data: any) {
    const res = await apiClient.post('/auth/register', data);
    return res.data;
  },
  async login(data: any) {
    const res = await apiClient.post('/auth/login', data);
    return res.data;
  },
  async getMe(): Promise<User> {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },
  logout() {
    localStorage.removeItem('missionmind_token');
    localStorage.removeItem('missionmind_user');
  }
};

// Research Assistant & Chat
export const chatService = {
  async askQuestion(data: {
    question: string;
    session_id?: number;
    subsystem_filter?: string;
    agency_filter?: string;
    document_id?: number;
    is_all_reports?: boolean;
  }) {
    const res = await apiClient.post('/chat/ask', data);
    return res.data;
  },
  async getSessions(): Promise<ResearchSession[]> {
    const res = await apiClient.get('/chat/sessions');
    return res.data;
  },
  async createSession(title?: string): Promise<ResearchSession> {
    const res = await apiClient.post('/chat/sessions', { title });
    return res.data;
  },
  async getSession(id: number): Promise<ResearchSession> {
    const res = await apiClient.get(`/chat/sessions/${id}`);
    return res.data;
  },
  async getSessionSummary(id: number): Promise<SessionSummaryData> {
    const res = await apiClient.get(`/chat/sessions/${id}/summary`);
    return res.data;
  },
  async deleteSession(id: number) {
    const res = await apiClient.delete(`/chat/sessions/${id}`);
    return res.data;
  }
};

// Document Library
export const documentService = {
  async getDocuments(params?: { agency?: string; mission?: string; search?: string }): Promise<DocumentItem[]> {
    const res = await apiClient.get('/documents', { params });
    return res.data;
  },
  async getDocument(id: number): Promise<DocumentItem> {
    const res = await apiClient.get(`/documents/${id}`);
    return res.data;
  },
  async uploadDocument(formData: FormData): Promise<DocumentItem> {
    const res = await apiClient.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  async reprocess(id: number) {
    const res = await apiClient.post(`/documents/${id}/process`);
    return res.data;
  },
  async deleteDocument(id: number) {
    const res = await apiClient.delete(`/documents/${id}`);
    return res.data;
  },
  getPdfUrl(id: number) {
    return `/api/documents/${id}/pdf`;
  },
  async getPageContent(docId: number, pageNum: number) {
    const res = await apiClient.get(`/documents/${docId}/pages/${pageNum}`);
    return res.data;
  }
};

// Citations
export const citationService = {
  async getCitation(chunkId: number) {
    const res = await apiClient.get(`/citations/${chunkId}`);
    return res.data;
  }
};

// Similar Past Failures
export const failureService = {
  async findSimilar(data: {
    problem_description: string;
    subsystem?: string;
    agency?: string;
    top_k?: number;
  }): Promise<FailureIncident[]> {
    const res = await apiClient.post('/failures/similar', data);
    return res.data;
  },
  async listFailures(): Promise<FailureIncident[]> {
    const res = await apiClient.get('/failures');
    return res.data;
  },
  async getFailure(id: number): Promise<FailureIncident> {
    const res = await apiClient.get(`/failures/${id}`);
    return res.data;
  }
};

// Failure Chain Analyzer
export const failureChainService = {
  async listMissions(): Promise<any[]> {
    const res = await apiClient.get('/failure-chain/missions');
    return res.data;
  },
  async getChain(incidentId: number): Promise<FailureChain> {
    const res = await apiClient.get(`/failure-chain/${incidentId}`);
    return res.data;
  }
};

// Research Reports
export const reportService = {
  async generate(data: {
    session_id: number;
    report_title?: string;
    include_failure_chain?: boolean;
    include_similar_failures?: boolean;
    custom_notes?: string;
  }): Promise<GeneratedReportItem> {
    const res = await apiClient.post('/reports/generate', data);
    return res.data;
  },
  async listReports(): Promise<GeneratedReportItem[]> {
    const res = await apiClient.get('/reports');
    return res.data;
  },
  getDownloadUrl(reportId: number) {
    return `/api/reports/${reportId}/download`;
  },
  getLatestSessionDownloadUrl(sessionId: number) {
    return `/api/reports/session/${sessionId}/download-latest`;
  }
};

// Voice
export const voiceService = {
  async transcribe(blob: Blob): Promise<{ text: string }> {
    const formData = new FormData();
    formData.append('file', blob, 'recording.wav');
    const res = await apiClient.post('/voice/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  async synthesize(text: string): Promise<any> {
    const res = await apiClient.post('/voice/synthesize', { text });
    return res.data;
  }
};

// Admin Operations
export const adminService = {
  async getStats(): Promise<SystemStats> {
    const res = await apiClient.get('/admin/stats');
    return res.data;
  },
  async getAdminDocs() {
    const res = await apiClient.get('/admin/documents');
    return res.data;
  },
  async getUsers() {
    const res = await apiClient.get('/admin/users');
    return res.data;
  },
  async getLogs() {
    const res = await apiClient.get('/admin/ingestion-logs');
    return res.data;
  }
};
