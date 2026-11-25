# MISSIONMIND AI – Database Schema Documentation

## Database Engine
PostgreSQL with `pgvector` extension enabled.
Compatible fallback: SQLite with JSON/array vector similarity computation for isolated development.

## Tables & Relationships

### 1. `users`
- `id` (INTEGER, Primary Key)
- `name` (VARCHAR(150), Not Null)
- `email` (VARCHAR(255), Unique, Not Null)
- `password_hash` (VARCHAR(255), Not Null)
- `role` (VARCHAR(50), Default 'analyst')
- `created_at` (TIMESTAMP)

### 2. `missions`
- `id` (INTEGER, Primary Key)
- `mission_name` (VARCHAR(200), Unique, Not Null)
- `space_agency` (VARCHAR(100), Not Null) -- NASA, ISRO, ESA, etc.
- `launch_year` (INTEGER)
- `mission_description` (TEXT)
- `outcome` (VARCHAR(50)) -- Failure, Partial Failure, Mishap
- `created_at` (TIMESTAMP)

### 3. `documents`
- `id` (INTEGER, Primary Key)
- `title` (VARCHAR(300), Not Null)
- `mission_name` (VARCHAR(200), Not Null)
- `space_agency` (VARCHAR(100), Not Null)
- `publication_year` (INTEGER)
- `document_type` (VARCHAR(100)) -- Mishap Investigation Board Report, Lessons Learned, Technical Memo
- `source_url` (VARCHAR(1000))
- `licence` (VARCHAR(200)) -- Public Domain, NASA Open Access, ISRO Public Release
- `file_path` (VARCHAR(500), Not Null)
- `total_pages` (INTEGER)
- `processing_status` (VARCHAR(50)) -- pending, processing, completed, failed
- `error_message` (TEXT)
- `created_at` (TIMESTAMP)

### 4. `document_chunks`
- `id` (INTEGER, Primary Key)
- `document_id` (INTEGER, Foreign Key -> `documents.id`, CASCADE)
- `page_number` (INTEGER, Not Null)
- `section_heading` (VARCHAR(300))
- `chunk_text` (TEXT, Not Null)
- `embedding` (VECTOR(384) or JSON)
- `chunk_metadata` (JSON)
- `created_at` (TIMESTAMP)

### 5. `failure_incidents`
- `id` (INTEGER, Primary Key)
- `mission_id` (INTEGER, Foreign Key -> `missions.id`)
- `document_id` (INTEGER, Foreign Key -> `documents.id`)
- `failure_description` (TEXT, Not Null)
- `subsystem` (VARCHAR(150), Not Null) -- Thermal, Propulsion, Guidance/Software, Electrical, Aerodynamics
- `failure_mode` (VARCHAR(200))
- `trigger` (TEXT)
- `root_cause` (TEXT, Not Null)
- `mission_phase` (VARCHAR(100)) -- Ascent, Trajectory Insertion, Re-entry, Descent
- `mission_impact` (VARCHAR(150)) -- Total Vehicle Loss, Mission Termination
- `corrective_action` (TEXT)
- `source_page` (INTEGER)
- `created_at` (TIMESTAMP)

### 6. `failure_events`
- `id` (INTEGER, Primary Key)
- `incident_id` (INTEGER, Foreign Key -> `failure_incidents.id`, CASCADE)
- `event_order` (INTEGER, Not Null)
- `event_title` (VARCHAR(250), Not Null)
- `event_description` (TEXT, Not Null)
- `event_type` (VARCHAR(100)) -- Root Cause, Cascading Failure, Impact, Observation
- `relationship_type` (VARCHAR(100)) -- Confirmed Causal, Documented Sequence, Suspected
- `event_timestamp` (VARCHAR(100))
- `evidence_chunk_id` (INTEGER, Foreign Key -> `document_chunks.id`)
- `source_page` (INTEGER)

### 7. `research_sessions`
- `id` (INTEGER, Primary Key)
- `user_id` (INTEGER, Foreign Key -> `users.id`, CASCADE)
- `title` (VARCHAR(250), Not Null)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### 8. `research_messages`
- `id` (INTEGER, Primary Key)
- `session_id` (INTEGER, Foreign Key -> `research_sessions.id`, CASCADE)
- `role` (VARCHAR(50), Not Null) -- user, assistant, system
- `message_text` (TEXT, Not Null)
- `citations` (JSON) -- List of {document_id, document_title, page_number, chunk_id, snippet}
- `retrieval_confidence` (FLOAT)
- `created_at` (TIMESTAMP)

### 9. `generated_reports`
- `id` (INTEGER, Primary Key)
- `user_id` (INTEGER, Foreign Key -> `users.id`, CASCADE)
- `session_id` (INTEGER, Foreign Key -> `research_sessions.id`)
- `report_title` (VARCHAR(300), Not Null)
- `file_path` (VARCHAR(500), Not Null)
- `created_at` (TIMESTAMP)
