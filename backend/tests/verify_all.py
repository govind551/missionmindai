import os
import sys
import asyncio
from pathlib import Path

# Override print to always flush
old_print = print
def print(*args, **kwargs):
    kwargs["flush"] = True
    old_print(*args, **kwargs)

# Add backend directory
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database.connection import SessionLocal, init_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.failure_incident import FailureIncident
from app.models.failure_event import FailureEvent
from app.providers.embedding_provider import embedding_provider
from app.services.retrieval_service import RetrievalService
from app.services.rag_service import RAGService
from app.services.failure_intelligence_service import FailureIntelligenceService
from app.services.failure_chain_service import FailureChainService
from app.services.report_service import ReportService

async def run_verifications():
    print("=" * 75)
    print("  MISSIONMIND AI - COMPREHENSIVE INTEGRATION & DEMO VERIFICATION")
    print("=" * 75)

    init_db()
    db = SessionLocal()

    try:
        # 1. Verify Ingestion & Knowledge Base
        doc_count = db.query(Document).count()
        chunk_count = db.query(DocumentChunk).count()
        incident_count = db.query(FailureIncident).count()
        event_count = db.query(FailureEvent).count()
        print(f"\n[PASS] Database Integrity Verified:")
        print(f"       - Indexed Documents: {doc_count} (NASA & ISRO)")
        print(f"       - Vector Chunks:     {chunk_count}")
        print(f"       - Failure Incidents: {incident_count}")
        print(f"       - Causal Events:     {event_count}")
        assert doc_count >= 6, "Expected at least 6 seed documents"
        assert chunk_count >= 15, "Expected chunks indexed in database"

        # 2. Verify Embeddings Generation & Dimension
        emb = embedding_provider.get_embedding("Thermal protection system failure during atmospheric entry")
        print(f"\n[PASS] Dense Vector Embedding:")
        print(f"       - Dimensions: {len(emb)} (Expected 384)")
        print(f"       - Vector Sample: [{emb[0]:.4f}, {emb[1]:.4f}, {emb[2]:.4f}, ...]")
        assert len(emb) == 384

        # 3. Demo 1 Verification: AI Research Assistant (Grounded Q&A with Citations)
        print("\n--- TEST: Demo 1 - Grounded Q&A with Citations ---")
        q1 = "What went wrong with thermal control on past space probes?"
        ans1 = await RAGService.answer_question(db=db, question=q1, user_id=1)
        print(f"Question:   \"{q1}\"")
        print(f"Confidence: {ans1['retrieval_confidence'] * 100:.1f}% (Threshold: 45%)")
        print(f"Grounded:   {ans1['is_grounded']}")
        print(f"Citations:  {len(ans1['citations'])} cited sources")
        for cit in ans1['citations'][:2]:
            print(f"  -> Cited: {cit.document_title} | Page {cit.page_number} ({cit.space_agency})")
        assert ans1["is_grounded"] is True
        assert ans1["retrieval_confidence"] >= 0.45
        assert len(ans1["citations"]) > 0
        assert ans1["citations"][0].page_number > 0

        # 4. Demo 6 Verification: Reliability / Low-Confidence Rejection ("Not Found")
        print("\n--- TEST: Demo 6 - Low-Confidence Anti-Hallucination Rejection ---")
        q_unsupported = "What are the quantum physics effects on interstellar warp drives?"
        ans_unsupported = await RAGService.answer_question(db=db, question=q_unsupported, user_id=1)
        print(f"Question:   \"{q_unsupported}\"")
        print(f"Confidence: {ans_unsupported['retrieval_confidence'] * 100:.1f}%")
        print(f"Answer:     \"{ans_unsupported['answer'][:120]}...\"")
        assert "Not Found in the available documents" in ans_unsupported["answer"]
        assert ans_unsupported["is_grounded"] is False

        # 5. Demo 2 Verification: Similar Past Failures
        print("\n--- TEST: Demo 2 - Similar Past Failures Matching ---")
        prob_desc = "Our spacecraft is experiencing unexpected temperature fluctuations in the thermal control subsystem."
        similar_matches = FailureIntelligenceService.find_similar_failures(
            db=db,
            problem_description=prob_desc,
            top_k=3
        )
        print(f"Problem: \"{prob_desc}\"")
        print(f"Ranked Incident Matches Found: {len(similar_matches)}")
        for idx, match in enumerate(similar_matches, 1):
            print(f"  #{idx} {match['mission_name']} ({match['space_agency']}) - Similarity: {match['similarity_score'] * 100:.1f}%")
            print(f"      Subsystem:  {match['subsystem']}")
            print(f"      Root Cause: {match['root_cause'][:90]}...")
        assert len(similar_matches) > 0
        assert similar_matches[0]["similarity_score"] > 0.50

        # 6. Demo 3 Verification: Failure Chain Reconstruction
        print("\n--- TEST: Demo 3 - Failure Chain Reconstruction ---")
        incident = db.query(FailureIncident).first()
        chain = FailureChainService.get_failure_chain_by_incident(db=db, incident_id=incident.id)
        print(f"Mission: {chain['mission_name']} ({chain['space_agency']})")
        print(f"Root Cause: {chain['root_cause'][:80]}...")
        print(f"Documented Chronological Events ({len(chain['events'])}):")
        for ev in chain["events"]:
            print(f"  Node #{ev['event_order']}: {ev['event_title']} [{ev['relationship_type']}] - Page {ev['source_page']}")
        assert len(chain["events"]) >= 3

        # 7. Demo 5 Verification: PDF Report Generation (ReportLab)
        print("\n--- TEST: Demo 5 - Smart PDF Research Report Generation ---")
        report = ReportService.generate_research_pdf(
            db=db,
            user_id=1,
            session_id=ans1["session_id"],
            report_title="Aerospace Mishap Lessons-Learned Technical Report",
            include_failure_chain=True,
            include_similar_failures=True,
            custom_notes="Automated flight verification audit run."
        )
        print(f"[PASS] ReportLab PDF Generated: {report.file_path}")
        print(f"       File Size: {os.path.getsize(report.file_path):,} bytes")
        assert os.path.exists(report.file_path)
        assert os.path.getsize(report.file_path) > 1000

        print("\n" + "=" * 75)
        print("  ALL 7 HACKATHON VERIFICATION CRITERIA PASSED WITH 100% SUCCESS!")
        print("=" * 75)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_verifications())
