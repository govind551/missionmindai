export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  created_at: string;
}

export interface CitationItem {
  chunk_id: number;
  document_id: number;
  document_title: string;
  mission_name: string;
  space_agency: string;
  page_number: number;
  section_heading?: string;
  snippet: string;
  score?: number;
  source_url?: string;
}

export interface ResearchMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant' | 'system';
  message_text: string;
  citations?: CitationItem[];
  retrieval_confidence?: number;
  created_at: string;
}

export interface ResearchSession {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: ResearchMessage[];
}

export interface DocumentItem {
  id: number;
  title: string;
  mission_name: string;
  space_agency: string;
  publication_year?: number;
  document_type: string;
  source_url?: string;
  licence?: string;
  file_path: string;
  total_pages: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  created_at: string;
  chunk_count: number;
}

export interface FailureIncident {
  id: number;
  mission_name: string;
  space_agency: string;
  subsystem: string;
  failure_description: string;
  failure_mode?: string;
  trigger?: string;
  root_cause: string;
  mission_phase?: string;
  mission_impact?: string;
  corrective_action?: string;
  source_page?: number;
  document_id?: number;
  document_title?: string;
  similarity_score?: number;
  citations?: Array<{
    document_id: number;
    document_title: string;
    source_url?: string;
    page_number: number;
  }>;
}

export interface FailureEvent {
  id: number;
  incident_id: number;
  event_order: number;
  event_title: string;
  event_description: string;
  event_type: string;
  relationship_type: string;
  event_timestamp?: string;
  source_page?: number;
  evidence_chunk_id?: number;
  document_title?: string;
  source_url?: string;
}

export interface FailureChain {
  incident_id: number;
  document_id?: number;
  mission_name: string;
  space_agency: string;
  subsystem: string;
  root_cause: string;
  mission_impact?: string;
  events: FailureEvent[];
  methodology_note: string;
}

export interface GeneratedReportItem {
  id: number;
  user_id: number;
  session_id?: number;
  report_title: string;
  file_path: string;
  download_url: string;
  created_at: string;
}

export interface QAPairSummary {
  query_number: number;
  question: string;
  answer: string;
  citations: CitationItem[];
  retrieval_confidence: number;
  timestamp?: string;
}

export interface SessionSummaryData {
  session_id: number;
  session_title: string;
  total_queries: number;
  total_answers: number;
  missions_covered: string[];
  agencies_covered: string[];
  total_citations: number;
  average_confidence: number;
  executive_summary: string;
  qa_pairs: QAPairSummary[];
}

export interface SystemStats {
  total_documents: number;
  total_chunks: number;
  total_missions: number;
  total_incidents: number;
  total_users: number;
  total_queries: number;
  nasa_documents: number;
  isro_documents: number;
  active_models: {
    embedding: string;
    llm: string;
    pdf_extractor: string;
  };
}
