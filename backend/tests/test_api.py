import os
import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.database.connection import SessionLocal, init_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.failure_incident import FailureIncident
from app.providers.embedding_provider import embedding_provider
from app.services.pdf_extractor import PDFExtractor
from app.services.chunking_service import ChunkingService

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    init_db()

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_user_registration_and_login():
    email = f"flight_test_{os.getpid()}@missionmind.ai"
    reg_payload = {
        "name": "Commander John Young",
        "email": email,
        "password": "FlightPassword2026!",
        "role": "analyst"
    }
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code in (201, 400)

    # Login
    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "FlightPassword2026!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert token is not None

    # Test protected /api/auth/me
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == email

def test_invalid_file_rejection():
    # Attempt to upload non-PDF file
    files = {"file": ("malicious.txt", b"Invalid content", "text/plain")}
    data = {
        "title": "Invalid Document",
        "mission_name": "Test Mission",
        "space_agency": "NASA"
    }
    resp = client.post("/api/documents/upload", files=files, data=data)
    assert resp.status_code == 400

def test_embedding_generation_consistency():
    vec1 = embedding_provider.get_embedding("Thermal control failure on Mars probe")
    vec2 = embedding_provider.get_embedding("Spacecraft temperature fluctuation in thermal subsystem")
    
    assert len(vec1) == 384
    assert len(vec2) == 384
    
    # Check normalized L2 magnitude ~ 1.0
    import numpy as np
    norm = np.linalg.norm(vec1)
    assert abs(norm - 1.0) < 1e-3

def test_rag_question_answering_thermal_control():
    # Hackathon Demo 1 Question: "What went wrong with thermal control on past space probes?"
    payload = {
        "question": "What went wrong with thermal control on past space probes?"
    }
    resp = client.post("/api/chat/ask", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_grounded"] is True
    assert data["retrieval_confidence"] > 0.40
    assert len(data["citations"]) > 0
    # Citations must preserve exact page numbers
    assert data["citations"][0]["page_number"] > 0
    assert "Mars Climate Orbiter" in str(data) or "Thermal" in str(data) or "Columbia" in str(data)

def test_low_confidence_not_found_rejection():
    # Hackathon Demo 6 Reliability Question: Unsupported query that must return Not Found
    payload = {
        "question": "What are the quantum physics mechanisms of interstellar warp drives in hyperspace?"
    }
    resp = client.post("/api/chat/ask", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # Must NOT hallucinate an answer
    assert "Not Found in the available documents" in data["answer"]
    assert data["is_grounded"] is False

def test_similar_past_failures_ranking():
    # Hackathon Demo 2: Similar Past Failures
    payload = {
        "problem_description": "Our spacecraft is experiencing unexpected temperature fluctuations in its thermal control subsystem."
    }
    resp = client.post("/api/failures/similar", json=payload)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) > 0
    # Must be sorted descending by similarity score
    scores = [r["similarity_score"] for r in results]
    assert scores == sorted(scores, reverse=True)
    # Check subsystem and root cause presence
    assert results[0]["root_cause"] is not None
    assert results[0]["subsystem"] is not None

def test_failure_chain_reconstruction():
    # Hackathon Demo 3: Failure Chain
    # List missions
    list_resp = client.get("/api/failure-chain/missions")
    assert list_resp.status_code == 200
    missions = list_resp.json()
    assert len(missions) > 0
    
    incident_id = missions[0]["incident_id"]
    chain_resp = client.get(f"/api/failure-chain/{incident_id}")
    assert chain_resp.status_code == 200
    chain_data = chain_resp.json()
    assert len(chain_data["events"]) > 0
    # Verify chronological event ordering
    orders = [e["event_order"] for e in chain_data["events"]]
    assert orders == sorted(orders)
    assert chain_data["events"][0]["relationship_type"] in ["Confirmed Causal", "Documented Sequence", "Suspected"]

def test_report_generation_pdf():
    # Hackathon Demo 5: PDF Research Report Generation
    # Create session and ask question first
    session_resp = client.post("/api/chat/sessions", json={"title": "Test Report Session"})
    session_id = session_resp.json()["id"]

    client.post("/api/chat/ask", json={
        "question": "What went wrong with thermal control on past space probes?",
        "session_id": session_id
    })

    gen_payload = {
        "session_id": session_id,
        "report_title": "Investigation Report on Probe Thermal Anomalies",
        "include_failure_chain": True,
        "include_similar_failures": True
    }
    rep_resp = client.post("/api/reports/generate", json=gen_payload)
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()
    assert rep_data["file_path"].endswith(".pdf")
    assert os.path.exists(rep_data["file_path"])

    # Test download endpoint
    dl_resp = client.get(f"/api/reports/{rep_data['id']}/download")
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] == "application/pdf"
    assert len(dl_resp.content) > 1000  # Valid non-empty PDF binary
