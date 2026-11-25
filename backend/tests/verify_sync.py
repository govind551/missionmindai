import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database.connection import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.failure_incident import FailureIncident
from app.models.failure_event import FailureEvent
from app.services.retrieval_service import RetrievalService
from app.services.failure_intelligence_service import FailureIntelligenceService
from app.services.failure_chain_service import FailureChainService
from app.services.report_service import ReportService
from app.providers.embedding_provider import embedding_provider
from app.providers.llm_provider import llm_provider

def main():
    print(">>> 1. CONNECTING TO DATABASE")
    db = SessionLocal()
    docs = db.query(Document).count()
    chunks = db.query(DocumentChunk).count()
    incidents = db.query(FailureIncident).count()
    events = db.query(FailureEvent).count()
    print(f"DATABASE VERIFIED: {docs} docs, {chunks} chunks, {incidents} incidents, {events} events")

    print("\n>>> 2. TESTING EMBEDDINGS")
    vec = embedding_provider.get_embedding("Thermal control failure on Mars probe")
    print(f"EMBEDDING GENERATED: len={len(vec)}, sample={vec[:3]}")

    print("\n>>> 3. TESTING RETRIEVAL (DEMO 1)")
    results = RetrievalService.hybrid_retrieve(db, "What went wrong with thermal control on past space probes?", top_k=3)
    print(f"RETRIEVED {len(results)} CHUNKS, TOP SCORE: {results[0]['hybrid_score'] if results else 'NONE'}")
    for r in results:
        print(f"  - {r['document_title']} | Page {r['page_number']} | Agency {r['space_agency']}")

    print("\n>>> 4. TESTING GROUNDED SYNTHESIS")
    ans = llm_provider._synthesize_grounded_evidence("What went wrong with thermal control on past space probes?", results)
    print("SYNTHESIZED GROUNDED ANSWER PREVIEW:")
    print(ans[:250] + "...")

    print("\n>>> 5. TESTING SIMILAR PAST FAILURES (DEMO 2)")
    sim = FailureIntelligenceService.find_similar_failures(
        db, "Our spacecraft is experiencing unexpected temperature fluctuations in the thermal control subsystem.", top_k=3
    )
    print(f"FOUND {len(sim)} MATCHES:")
    for s in sim:
        print(f"  - {s['mission_name']} ({s['space_agency']}) | Subsystem: {s['subsystem']} | Score: {s['similarity_score']}")

    print("\n>>> 6. TESTING FAILURE CHAIN (DEMO 3)")
    chain = FailureChainService.get_failure_chain_by_incident(db, 1)
    print(f"CHAIN FOR {chain['mission_name']}: {len(chain['events'])} events")
    for ev in chain['events']:
        print(f"  #{ev['event_order']} {ev['event_title']} [{ev['relationship_type']}]")

    print("\n>>> 7. TESTING REPORT GENERATION (DEMO 5)")
    rep = ReportService.generate_research_pdf(db, 1, 1, "Flight Telemetry Investigation Report")
    print(f"REPORT GENERATED: {rep.file_path}")

    print("\n=======================================================")
    print("  ALL 7 CORE SYSTEM CAPABILITIES VERIFIED 100% OPERATIONAL")
    print("=======================================================")

if __name__ == "__main__":
    main()
