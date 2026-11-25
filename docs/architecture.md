# MISSIONMIND AI – System Architecture

## Overview
MISSIONMIND AI is an evidence-grounded aerospace research assistant designed to extract, index, retrieve, and synthesize technical knowledge from historical NASA and ISRO mission investigation reports.

## System Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                 FRONTEND (React + Vite)                           |
|  - Aerospace Command UI (Dark violet/navy theme)                                  |
|  - AI Research Assistant with Inline Clickable Page Citations                     |
|  - Built-in PDF Citation Viewer (PDF.js page sync & bounding highlight)          |
|  - Similar Past Failures Intelligence (Ranked Vector & Hybrid Retrieval)         |
|  - Failure Chain Reconstruction (Interactive Causal Flow & Timelines)             |
|  - My Research & PDF Report Generator                                             |
|  - Voice Assistant (STT & TTS controls)                                           |
+-----------------------------------------+-----------------------------------------+
                                          | REST API / JSON (Axios + JWT Auth)
                                          v
+-----------------------------------------------------------------------------------+
|                                 BACKEND (FastAPI)                                 |
|                                                                                   |
|  [Auth & Security]         [Document Processing]         [Retrieval & RAG]       |
|  - Password Hashing (bcrypt) - PyMuPDF Page Extractor    - Dense Vector Search   |
|  - JWT Bearer Tokens       - Semantic Page Chunking     - Full-Text Keyword BM25|
|  - RBAC (Admin / Analyst)  - Embedding Generation        - Reciprocal Rank Fusion|
|                            - OCR Fallback Support       - Evidence Verification |
|                                                          - Grounded Prompt Eng.  |
|                                                                                   |
|  [Failure Intelligence]    [Failure Chain Engine]       [Reporting & Voice]       |
|  - Multi-factor Similarity - Causal Graph Extraction    - ReportLab PDF Engine  |
|  - Subsystem & Root Cause  - Chronological Sequencing   - STT/TTS Providers     |
+-----------------------------------------+-----------------------------------------+
                                          |
                     +--------------------+--------------------+
                     |                                         |
                     v                                         v
+---------------------------------------+   +---------------------------------------+
|          DATABASE TIER                |   |          EXTERNAL AI PROVIDERS        |
| - PostgreSQL with pgvector extension  |   | - LLM: Gemini / Groq / OpenAI        |
| - Fallback SQLite + Vector Simulator  |   | - Embeddings: Sentence-Transformers / |
| - Full ACID transactions & Alembic    |   |   HuggingFace / Provider APIs         |
| - Strict Foreign Key Integrity        |   | - STT/TTS: Web Speech API & Cloud     |
+---------------------------------------+   +---------------------------------------+
```

## Data Ingestion Flow
1. Official NASA/ISRO PDF reports are uploaded or ingested from seed collection.
2. `PyMuPDF` extracts text with precise page bounds, titles, and structural headings.
3. Text is segmented into page-aware semantic chunks with sliding overlap.
4. Embedding vectors (384-d or 768-d) are generated and stored with pgvector.
5. Ingestion logs, document status, and licence/source URLs are recorded.

## Question Answering Flow
1. User submits research question (text or voice STT).
2. Backend generates query embedding and executes hybrid retrieval (dense vector + lexical search).
3. Retrieved chunks are re-ranked, and a confidence score is calculated based on cosine similarity and token coverage.
4. If confidence < 0.45 threshold, the system returns: `"Not Found in the available documents. Please try a different question or add more source documents."`
5. If confidence >= 0.45, retrieved evidence is sent to LLM with strict grounding constraints.
6. Backend verifies that every cited fact corresponds to an actual chunk in the retrieved set.
7. Grounded answer is returned with clickable citation badges, document metadata, and page numbers.
