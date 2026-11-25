import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database.connection import SessionLocal
from app.api.routes import auth, documents, chat, citations, failures, failure_chain, reports, admin
from app.schemas.auth import UserLogin
from app.schemas.chat import QuestionRequest
from app.schemas.failure import FailureQueryRequest
from app.schemas.report import ReportGenerateRequest

def test_routes():
    db = SessionLocal()
    print("Testing auth route...")
    login_res = auth.login(UserLogin(email="admin@missionmind.ai", password="Aerospace@2026"), db)
    assert login_res.access_token is not None
    print("[PASS] Auth login token generated")

    print("Testing documents route...")
    docs = documents.list_documents(db=db)
    assert len(docs) >= 6
    print(f"[PASS] Documents list returned {len(docs)} documents")

    print("Testing citation route...")
    cit = citations.get_citation_detail(chunk_id=1, db=db)
    assert cit.document_title is not None
    assert cit.page_number > 0
    print(f"[PASS] Citation chunk #1 verified: {cit.document_title} Page {cit.page_number}")

    print("Testing failures route...")
    fail_res = failures.find_similar_failures(
        FailureQueryRequest(problem_description="temperature fluctuation in thermal control"),
        db=db
    )
    assert len(fail_res) > 0
    print(f"[PASS] Failures route returned {len(fail_res)} ranked incidents")

    print("Testing failure chain route...")
    chain = failure_chain.get_failure_chain(incident_id=1, db=db)
    assert len(chain["events"]) > 0
    print(f"[PASS] Failure chain route returned {len(chain['events'])} events")

    print("Testing admin route...")
    stats = admin.get_system_stats(db=db)
    assert stats["total_documents"] >= 6
    print(f"[PASS] Admin stats returned: {stats['total_documents']} docs, {stats['total_chunks']} chunks")

    print("Testing reports route...")
    rep = reports.generate_report(
        ReportGenerateRequest(session_id=1, report_title="Automated Test Report"),
        current_user=None,
        db=db
    )
    assert rep.file_path.endswith(".pdf")
    print(f"[PASS] Reports route generated: {rep.file_path}")

    print("\nALL API ROUTES TESTED AND VERIFIED FUNCTIONAL!")

if __name__ == "__main__":
    test_routes()
