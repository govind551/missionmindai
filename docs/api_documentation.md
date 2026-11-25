# MISSIONMIND AI – REST API Specification

## Base URL
`/api`

## Authentication
Bearer JWT Token in header: `Authorization: Bearer <token>`

### Auth Endpoints
- `POST /api/auth/register` - Create user account
- `POST /api/auth/login` - Authenticate & obtain JWT
- `GET /api/auth/me` - Get current user profile
- `POST /api/auth/logout` - Invalidate session

### Documents Endpoints
- `GET /api/documents` - List all indexed documents with metadata
- `GET /api/documents/{document_id}` - Get single document details
- `POST /api/documents/upload` - Upload PDF and trigger ingestion pipeline
- `POST /api/documents/{document_id}/process` - Manually trigger / re-index PDF
- `GET /api/documents/{document_id}/status` - Check chunking & embedding status
- `GET /api/documents/{document_id}/pdf` - Stream original PDF file
- `GET /api/documents/{document_id}/pages/{page_number}` - Get page text & metadata

### Research Assistant (Chat & RAG)
- `POST /api/chat/ask` - Submit query, retrieve chunks, generate grounded answer with citations
- `GET /api/chat/sessions` - List user research sessions
- `POST /api/chat/sessions` - Create new research session
- `GET /api/chat/sessions/{session_id}` - Retrieve chat history & citations
- `DELETE /api/chat/sessions/{session_id}` - Delete session

### Citation Viewer
- `GET /api/citations/{chunk_id}` - Get full citation chunk details, bounding info, source doc & page
- `GET /api/citations/verify` - Validate citation claims against retrieved evidence

### Similar Past Failures
- `POST /api/failures/similar` - Input an engineering problem description; returns ranked historical failures with similarity scores, subsystem, root cause, and citations
- `GET /api/failures` - List all indexed historical failure incidents
- `GET /api/failures/{incident_id}` - Get specific incident breakdown

### Failure Chain Analyzer
- `POST /api/failure-chain/analyze` - Request causal chain reconstruction for a selected mission
- `GET /api/failure-chain/{incident_id}` - Get structured chronological failure events and relationship types

### Voice Assistant
- `POST /api/voice/transcribe` - Transcribe uploaded audio file to text
- `POST /api/voice/synthesize` - Synthesize text answer to speech audio

### Research Reports (Smart PDF Generation)
- `POST /api/reports/generate` - Generate professional ReportLab PDF report from research session
- `GET /api/reports` - List user generated reports
- `GET /api/reports/{report_id}` - Get report metadata
- `GET /api/reports/{report_id}/download` - Download generated PDF

### Admin Endpoints
- `GET /api/admin/documents` - Detailed document index administration
- `GET /api/admin/stats` - System-wide stats (total docs, chunks, missions, queries)
- `GET /api/admin/ingestion-logs` - Document processing logs
