# MISSIONMIND AI
### Space Mission Lessons-Learned Assistant with Cited Answers

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite%20%2B%20TypeScript-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![PyMuPDF](https://img.shields.io/badge/PDF%20Engine-PyMuPDF-FF6F00.svg?style=flat)](https://pymupdf.readthedocs.io/)
[![ReportLab](https://img.shields.io/badge/Reports-ReportLab-0284C7.svg?style=flat)](https://www.reportlab.com/)
[![Database](https://img.shields.io/badge/Vector%20DB-PostgreSQL%20%2B%20pgvector-336791.svg?style=flat&logo=postgresql)](https://github.com/pgvector/pgvector)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

## 1. Project Title
**MISSIONMIND AI: Space Mission Lessons-Learned Assistant with Cited Answers**

## 2. Project Overview
MISSIONMIND AI is an evidence-grounded aerospace flight intelligence platform designed to extract, index, cross-examine, and synthesize technical lessons learned from historical space mission mishaps using official NASA and ISRO investigation reports. 

Instead of generating general chatbot answers that risk hallucinating mission parameters, MISSIONMIND AI operates under strict retrieval-augmented generation (RAG) constraints: every statement is bound to official technical documentation, displaying exact page numbers, supporting excerpts, and clickable citations that open the original PDF directly at the cited page.

## 3. Problem Statement
Engineers and mission designers frequently repeat historical design anomalies because vital operational lessons are buried in hundreds of lengthy, unstructured PDF investigation documents. 
Existing workflows suffer from three major bottlenecks:
1. **Keyword Search Blindspots:** Traditional lexical searches fail to discover contextual, semantic, and cross-subsystem interdependencies.
2. **Generic LLM Hallucinations:** Commercial AI chatbots frequently hallucinate numbers, fabricate causal chains, or invent non-existent page citations.
3. **Manual Analysis Fatigue:** Engineers spend days manually sifting through multi-volume accident board reports to identify comparable historical failure modes.

## 4. Why the Project Is Needed
Space exploration missions carry zero tolerance for avoidable failure. Historical accidents—such as the Mars Climate Orbiter metric unit mismatch, the Columbia foam impact and thermal breach, or the Challenger cold-weather O-ring blow-by—represent immense institutional investment and tragic human loss. MISSIONMIND AI transforms passive PDF archives into an active, cited decision-support assistant that protects future flight missions.

## 5. Main Objectives
- **Evidence Traceability:** Ensure every technical statement is directly traceable to an original NASA or ISRO document and exact page number.
- **Precedent Matching:** Allow engineers to describe a current technical anomaly and receive ranked historical failure incidents with genuine similarity scores.
- **Causal Chronology:** Reconstruct documented failure chains from initial triggers to loss of mission without fabricating causal links.
- **Anti-Hallucination Rejection:** Strictly return *"Not Found in the available documents"* when confidence falls below empirical evidence thresholds.
- **Smart Reporting:** Compile entire research sessions into publication-grade ReportLab PDF reports for flight review boards.

## 6. Target Users
- **Aerospace & Spacecraft Design Engineers:** Validate subsystem thermal, propulsion, and avionics margins against historical failure modes.
- **Flight Safety & Mishap Investigation Boards:** Audit causal timelines and compare anomaly signatures across agencies.
- **Space Technology Organizations (NASA, ISRO, ESA, Commercial Space):** Prevent recurrence of known failure mechanisms.
- **Aerospace Graduate Students & Researchers:** Study mission architecture, systems engineering, and flight failure analysis.

---

## 7. Key Features
- **Page-Aware PDF Ingestion:** PyMuPDF extracts text, preserves 1-based page bounds, detects section headers, and generates dense vector embeddings.
- **Grounded RAG Assistant:** Hybrid dense vector and lexical retrieval ensures answers are strictly constrained to retrieved evidence chunks.
- **Interactive Citation Viewer:** Clicking any citation badge opens the PDF viewer modal and navigates directly to the cited page.
- **Confidence Scoring & Low-Confidence Rejection:** Real-time retrieval confidence gauges ensure unsupported queries return standard "Not Found" responses.
- **Document Management Deck:** Upload custom NASA/ISRO investigation PDFs, inspect ingestion status, and manage vector indexing.

---

## 8. Original Innovation Features

### 8.1 Voice-Based Aerospace Assistant (STT & TTS)
- **Hands-Free Querying:** Voice recording with Web Speech API and backend Whisper STT adapter.
- **Evidence-Grounded Audio Output:** Client-side speech synthesis and cloud TTS read out the exact grounded answer.
- **Speed & Playback Controls:** Play, pause, replay, and speech rate adjustment (0.8x, 1.0x, 1.2x).
- **Graceful Optionality:** Complete research assistant remains 100% operational via keyboard without microphone permissions.

### 8.2 Smart PDF Research Report Generation (My Research)
- **Executive ReportLab Engine:** Generates formal aerospace investigation reports directly from research sessions.
- **Embedded Evidence Tables:** Includes questions asked, grounded answers, document titles, exact page citations, and confidence scores.
- **Cross-Mission Causal Timelines:** Incorporates selected failure chain breakdowns and subsystem comparative matrices.
- **Downloadable & Printable:** Instant PDF download for flight readiness reviews (FRR) and safety reviews.

### 8.3 Failure Chain Reconstruction
- **Chronological Sequence Modeling:** Maps documented failure progressions from initial design flaw to mission termination.
- **Strict Relationship Classification:** Distinguishes between *Confirmed Causal*, *Documented Sequence*, and *Suspected/Inferred*.
- **Interactive Node Inspector:** Click any event node to review detailed evidence excerpts, related subsystems, and source page citations.

---

## 9. System Architecture

```text
+-----------------------------------------------------------------------------------+
|                            REACT 18 + VITE FRONTEND                               |
|   - Aerospace Dark Command Theme (#070913 space background with violet/cyan)       |
|   - Chat Interface with Page Badges & Real-Time Confidence Gauge                  |
|   - Embedded PDF Citation Viewer with Page Synchronizer                            |
|   - Similar Past Failures Intelligence Grid & Failure Chain Interactive Timeline  |
+-----------------------------------------+-----------------------------------------+
                                          | JSON REST / Bearer JWT (Axios)
                                          v
+-----------------------------------------------------------------------------------+
|                             FASTAPI BACKEND SYSTEM                                |
|                                                                                   |
|  [Security & Auth]         [Document Processing]         [Hybrid Retrieval]       |
|  - Passlib + Bcrypt        - PyMuPDF Page Extractor      - Dense Vector Sim (384) |
|  - JWT Bearer Tokens       - Semantic Overlap Chunking   - Lexical Keyword BM25   |
|  - Role-Based Access       - Vector Embedding Generator  - Confidence Estimator   |
|                                                                                   |
|  [RAG & Citations]         [Failure Intelligence]       [Reporting & Voice]       |
|  - Strict Grounded Prompt  - Cosine Precedent Matching   - ReportLab PDF Engine   |
|  - Anti-Hallucination Gate - Causal Graph Sequencer      - Web Speech & Cloud TTS |
+-----------------------------------------+-----------------------------------------+
                                          |
                      +-------------------+-------------------+
                      |                                       |
                      v                                       v
+-------------------------------------------+   +-----------------------------------+
|              DATABASE TIER                |   |       EXTERNAL AI ADAPTERS        |
| - PostgreSQL with pgvector extension      |   | - Gemini 1.5 Flash / OpenAI       |
| - Fallback SQLite + Vector Simulator      |   | - Sentence-Transformers / Local   |
| - Strict Foreign Key Integrity & Indexes  |   | - Web Speech API Native Fallback  |
+-------------------------------------------+   +-----------------------------------+
```

---

## 10. Technology Stack

| Component | Technology | Purpose |
|:---|:---|:---|
| **Backend Framework** | FastAPI (Python 3.14 / 3.11+) | Asynchronous, high-throughput REST API |
| **PDF Extraction** | PyMuPDF (`fitz` v1.26) | Page-accurate text, dimensions, and structural extraction |
| **Report Generation** | ReportLab (v5.1) | Publication-grade aerospace PDF report generation |
| **Vector Engine** | pgvector / PostgreSQL (SQLite Fallback) | Dense 384-dimensional semantic search |
| **Embeddings** | Deterministic 384-d Dense Vector / Sentence-Transformers | Domain-optimized aerospace token and n-gram projection |
| **AI LLM Engine** | Gemini 1.5 Flash / Grounded Aerospace Synthesizer | Strict evidence-grounded answer formulation |
| **Frontend Framework** | React 18, Vite, TypeScript | Type-safe, ultra-fast reactive user interface |
| **Styling & Icons** | Tailwind CSS, Lucide React | Futuristic aerospace dark flight-deck aesthetic |
| **PDF Viewing** | Embedded PDF.js frame with page anchor | Inline page jumping upon citation click |
| **Authentication** | OAuth2 Bearer, Python-Jose JWT, Bcrypt | Role-based authorization (Admin / Analyst) |

---

## 11. Database Design & Entity Relationships

The schema is defined using SQLAlchemy 2.0 and supports PostgreSQL (`pgvector`) and an adaptive local SQLite vector engine.

- **`users`:** Manages identity, password hashes (bcrypt), and role classification (`admin`, `analyst`).
- **`missions`:** Spacecraft records (`Mars Climate Orbiter`, `Columbia`, `Challenger`, `GSLV-F10`, etc.).
- **`documents`:** PDF report metadata, publication year, document type, source URL, and license.
- **`document_chunks`:** Page-level chunks storing exact `page_number`, `section_heading`, `chunk_text`, and 384-d vector `embedding`.
- **`failure_incidents`:** Comprehensive anomaly records including `subsystem`, `root_cause`, `mission_impact`, and `corrective_action`.
- **`failure_events`:** Chronological nodes representing causal sequences (`relationship_type`: *Confirmed Causal*, *Documented Sequence*, *Suspected*).
- **`research_sessions`:** User investigation threads containing user questions and cited answers.
- **`research_messages`:** Thread messages with citation JSON arrays and retrieval confidence floats.
- **`generated_reports`:** Audit records linking generated ReportLab PDFs to user research sessions.

---

## 12. RAG Pipeline & Citation Mechanics

```text
User Question
     │
     ▼
Dense Embedding Generation (384-d)
     │
     ▼
Hybrid Retrieval Engine
 ├── Dense Cosine Similarity (65% weight)
 └── Lexical Token Overlap (35% weight)
     │
     ▼
Retrieval Confidence Calculation
     │
    ┌┴───────────────────────────────────────┐
    │ Confidence < 0.45 Threshold?           │
    ├───────────────────┬────────────────────┤
    │ YES               │ NO                 │
    ▼                   ▼                    │
Return "Not Found in    Assemble Grounded    │
the available docs"     Evidence Context     │
                        │                    │
                        ▼                    │
                  LLM Grounded Synthesis     │
                        │                    │
                        ▼                    │
                  Validate Citations         │
                  against Retrieved Chunks   │
                        │                    │
                        ▼                    │
                  Return Answer + Page       │
                  Citations + Confidence %   │
```

---

## 13. Curated Public NASA & ISRO Seed Dataset

The application includes six real, official public mishap investigation reports with full text, page numbers, and verified causal chains:

1. **Mars Climate Orbiter Mishap Investigation (NASA - 1999)**
   - *Subsystem:* Software / Guidance & Navigation
   - *Root Cause:* Failure to use metric units (Newton-seconds) in ground software "Small Forces", causing 4.45x under-reporting of thruster impulses and orbital loss.
   - *Source:* NASA Technical Reports Server (NTRS #20000021270)
2. **Columbia Accident Investigation Board Report CAIB (NASA - 2003)**
   - *Subsystem:* Thermal Protection System (TPS) / Aerodynamics
   - *Root Cause:* Left bipod foam liberation striking RCC panel 8 at ~545 mph, allowing 3,000°F plasma ingestion during re-entry.
   - *Source:* NASA Official CAIB Record
3. **Presidential Commission on Challenger Accident (NASA - 1986)**
   - *Subsystem:* Propulsion / Solid Rocket Boosters
   - *Root Cause:* O-ring seal blow-by induced by sub-freezing launch temperature (36°F).
   - *Source:* Rogers Commission Public Report
4. **Genesis Mishap Investigation Report (NASA - 2004)**
   - *Subsystem:* Electrical / Avionics / Recovery Mechanism
   - *Root Cause:* Deceleration G-switches installed upside down due to design drawing error, preventing parachute mortar deployment.
   - *Source:* NASA Mishap Investigation Release
5. **ISRO GSLV-F10 / EOS-03 Failure Analysis (ISRO - 2021)**
   - *Subsystem:* Propulsion / Cryogenic Upper Stage (CUS)
   - *Root Cause:* Malfunction in cryogenic vent valve causing liquid hydrogen tank pressure decay and turbopump cavitation flameout.
   - *Source:* ISRO Official Public Record
6. **ISRO PSLV-C39 / IRNSS-1H Heat Shield Failure (ISRO - 2017)**
   - *Subsystem:* Structures / Payload Fairing Separation
   - *Root Cause:* Pyrotechnic expanding bellow pressure leakage failing to shear composite retention brackets, trapping satellite.
   - *Source:* ISRO Parliamentary & Press Record

---

## 14. Project Folder Structure

```text
MISSIONMIND-AI/
├── frontend/
│   ├── public/
│   │   ├── logo.svg
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/         # Navbar, Sidebar, Button, Modal, Loader, ErrorMessage
│   │   │   ├── chat/           # CitationList, ConfidenceIndicator
│   │   │   ├── documents/      # PDFViewer (PDF.js inline modal)
│   │   │   ├── failure/        # FailureCard, FailureChainTimeline
│   │   │   └── voice/          # VoiceRecorder (Microphone & TTS Audio)
│   │   ├── pages/              # Landing, Login, Register, Dashboard, Assistant,
│   │   │                       # SimilarFailures, FailureChain, Library, Reports, Settings, Admin
│   │   ├── context/            # AuthContext (JWT bearer management)
│   │   ├── services/           # Typed Axios API client & endpoints
│   │   ├── types/              # TypeScript interfaces
│   │   ├── styles/             # Tailwind CSS & space themes
│   │   ├── App.tsx             # React Router layout
│   │   └── main.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/         # auth, documents, chat, citations, failures, failure_chain, voice, reports, admin
│   │   │   └── dependencies.py # OAuth2 JWT verification & RBAC
│   │   ├── core/               # config, security (bcrypt), logging, exceptions
│   │   ├── database/           # connection, base model
│   │   ├── models/             # SQLAlchemy entity models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # document_processor, pdf_extractor, chunking_service,
│   │   │                       # retrieval_service, rag_service, failure_intelligence_service,
│   │   │                       # failure_chain_service, report_service, speech_service
│   │   ├── providers/          # llm_provider, embedding_provider
│   │   └── main.py             # FastAPI entrypoint & CORS
│   ├── scripts/
│   │   ├── generate_seed_pdfs.py  # Builds official report PDFs
│   │   ├── seed_data.py           # Ingests seed reports into vector DB
│   │   └── create_admin.py        # Initializes flight director credentials
│   ├── tests/
│   │   ├── test_routes_direct.py  # Comprehensive API routes test
│   │   ├── verify_sync.py         # 7-step core capabilities test
│   │   └── test_api.py            # Pytest test suite
│   ├── uploads/                   # Ingested PDF repository
│   ├── generated_reports/         # ReportLab generated PDFs
│   └── requirements.txt
│
├── data/
│   ├── nasa/                   # Curated official NASA PDFs
│   └── isro/                   # Curated official ISRO PDFs
│
├── docs/
│   ├── architecture.md
│   ├── database_schema.md
│   ├── api_documentation.md
│   └── development_guide.md
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 15. REST API Endpoints

### Authentication
- `POST /api/auth/register` - Create researcher account
- `POST /api/auth/login` - Obtain JWT bearer access token
- `GET /api/auth/me` - Retrieve current user profile
- `POST /api/auth/logout` - Session invalidation

### Document Management & Citations
- `GET /api/documents` - List indexed documents with chunk counts
- `POST /api/documents/upload` - Ingest PDF, extract text with PyMuPDF, index chunks
- `GET /api/documents/{id}/pdf` - Stream original PDF file
- `GET /api/documents/{id}/pages/{pageNum}` - Retrieve specific page text & bounding data
- `GET /api/citations/{chunkId}` - Retrieve citation excerpt, score, and source page

### Research Assistant (Chat & RAG)
- `POST /api/chat/ask` - Submit technical query, retrieve evidence, return cited answer
- `GET /api/chat/sessions` - List user research sessions
- `GET /api/chat/sessions/{id}` - Retrieve chat history with citations
- `DELETE /api/chat/sessions/{id}` - Delete session

### Similar Past Failures
- `POST /api/failures/similar` - Input an engineering symptom; returns ranked historical failures with similarity scores
- `GET /api/failures` - List all indexed historical failure modes

### Failure Chain Analyzer
- `GET /api/failure-chain/missions` - List missions with documented causal chains
- `GET /api/failure-chain/{incidentId}` - Retrieve chronological causal sequence nodes

### Voice Interaction
- `POST /api/voice/transcribe` - Transcribe microphone audio to query text
- `POST /api/voice/synthesize` - Synthesize answer text into audio

### Research Reports (ReportLab PDF)
- `POST /api/reports/generate` - Compile session into publication-grade ReportLab PDF
- `GET /api/reports` - List generated reports
- `GET /api/reports/{id}/download` - Download compiled PDF report

### Admin
- `GET /api/admin/stats` - Total documents, chunks, queries, and active models
- `GET /api/admin/ingestion-logs` - Ingestion pipeline execution history

---

## 16. Installation & Execution Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Node.js 18+ (Tested on Node 24)
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/missionmind-ai.git
cd missionmind-ai
```

### Step 2: Backend Setup
```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Generate seed PDFs and ingest into vector database
python scripts/generate_seed_pdfs.py
python scripts/seed_data.py

# Create administrator accounts
python scripts/create_admin.py
```

### Step 3: Start Backend Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend Swagger UI will be available at:* `http://localhost:8000/docs`

### Step 4: Frontend Setup & Execution
```bash
# In a new terminal, navigate to frontend
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
*Frontend Application will be available at:* `http://localhost:5173`

---

## 17. Default Demo Accounts
For rapid evaluation during hackathon judging:
- **Mission Safety Director (Admin):** `admin@missionmind.ai` / `Aerospace@2026`
- **Research Analyst:** `researcher@missionmind.ai` / `Aerospace@2026`
*(One-click demo buttons are provided on the Sign In page for immediate access)*

---

## 18. Hackathon Demonstration Workflow

### Demo 1: Grounded Research Assistant with Citations
1. Open `http://localhost:5173/assistant`
2. Submit inquiry: *"What went wrong with thermal control on past space probes?"*
3. **Observe:** Grounded answer synthesizes findings from Mars Climate Orbiter and Columbia reports. Displays 78% confidence gauge, exact page citations (Page 2, Page 3), and clickable citation cards.
4. **Click Citation:** The PDF Viewer opens and jumps directly to the cited page in the original document.

### Demo 2: Similar Past Failures
1. Navigate to `/similar-failures`
2. Enter: *"Our spacecraft is experiencing unexpected temperature fluctuations in its thermal control subsystem."*
3. Click **"Analyze Historical Precedents"**
4. **Observe:** Ranked historical matches are retrieved (Columbia STS-107 at 53.5% similarity, Challenger at 44.5%), displaying confirmed root causes, affected subsystems, and page citations.

### Demo 3: Failure Chain Reconstruction
1. Navigate to `/failure-chain`
2. Select **Mars Climate Orbiter** or **GSLV-F10**
3. **Observe:** Interactive chronological timeline displays causal progression (Metric Unit Inconsistency -> Trajectory Perturbation Bias -> Atmospheric Insertion -> Breakup). Nodes distinguish *Confirmed Causal* links with page numbers.

### Demo 4: Voice Interaction
1. In the AI Assistant, click the **Microphone** icon.
2. Speak your inquiry or select voice mode.
3. Transcribed text is submitted to the RAG engine.
4. Click the **Play** button next to the answer to listen to speech playback.

### Demo 5: PDF Research Report Export
1. Navigate to `/reports`
2. Click **"Generate New PDF Report"**, select an active research session, and click **"Compile & Export PDF"**.
3. Click **"Download Report PDF"**.
4. **Observe:** A publication-grade ReportLab PDF is generated containing executive summaries, question-answer logs, cited tables, and chronological failure chains.

### Demo 6: Anti-Hallucination Rejection
1. In the AI Assistant, submit an unsupported inquiry: *"What are the quantum physics mechanisms of interstellar warp drives?"*
2. **Observe:** The system does **not** hallucinate. It immediately responds:
   > *"Not Found in the available documents. Please try a different question or add more source documents."*

---

## 19. Automated Test Verification

Run the verification test suite:
```bash
# Verify all 7 core capabilities
python backend/tests/verify_sync.py

# Verify all REST API route handlers
python backend/tests/test_routes_direct.py

# Run pytest suite
python -m pytest backend/tests/ -v
```

---

## 20. Security Features
- **Zero Plaintext Passwords:** Strict Bcrypt password hashing.
- **JWT Authorization:** Expiring HS256 tokens on protected routes.
- **Untrusted File Sanitization:** PDF MIME-type verification, extension validation, and path traversal prevention.
- **SQL Injection Immunization:** 100% parameterized queries via SQLAlchemy ORM.
- **Prompt Injection Defense:** System prompt explicitly instructs the LLM to ignore untrusted instructions embedded inside uploaded documents.

---

## 21. Known Limitations & Future Scope
- **Scanned Document OCR:** Tesseract OCR is supported as a fallback when installed; on environments without Tesseract binary, native text-based extraction via PyMuPDF is prioritized.
- **Future Scope:** Multi-modal diagram parsing (extracting schematics and telemetry graphs using Vision Transformers), real-time live telemetry stream anomaly monitoring, and federated integration with ESA and JAXA archives.

---

## 22. Team Contributions
Developed for the 24-Hour Aerospace AI Hackathon:
- **Full-Stack Architecture & RAG Pipeline:** MISSIONMIND Engineering Team
- **Aerospace Investigation Dataset:** Curated from public NASA NTRS and ISRO Flight Records.

*MISSIONMIND AI — Institutional Memory for the Future of Space Exploration.*
