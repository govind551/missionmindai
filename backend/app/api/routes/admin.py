from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.mission import Mission
from app.models.failure_incident import FailureIncident
from app.models.user import User
from app.models.research_message import ResearchMessage

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    total_docs = db.query(Document).count()
    total_chunks = db.query(DocumentChunk).count()
    total_missions = db.query(Mission).count()
    total_incidents = db.query(FailureIncident).count()
    total_users = db.query(User).count()
    total_queries = db.query(ResearchMessage).filter(ResearchMessage.role == "user").count()

    nasa_docs = db.query(Document).filter(Document.space_agency.ilike("%NASA%")).count()
    isro_docs = db.query(Document).filter(Document.space_agency.ilike("%ISRO%")).count()

    return {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "total_missions": total_missions,
        "total_incidents": total_incidents,
        "total_users": total_users,
        "total_queries": total_queries,
        "nasa_documents": nasa_docs,
        "isro_documents": isro_docs,
        "active_models": {
            "embedding": "Deterministic Dense 384-d (Aerospace Grounded)",
            "llm": "Gemini / Grounded Aerospace Synthesis",
            "pdf_extractor": "PyMuPDF (fitz) v1.26"
        }
    }

@router.get("/documents")
def get_admin_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    results = []
    for d in docs:
        chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).count()
        results.append({
            "id": d.id,
            "title": d.title,
            "mission_name": d.mission_name,
            "space_agency": d.space_agency,
            "publication_year": d.publication_year,
            "total_pages": d.total_pages,
            "chunk_count": chunk_count,
            "processing_status": d.processing_status,
            "error_message": d.error_message,
            "source_url": d.source_url,
            "licence": d.licence,
            "created_at": d.created_at
        })
    return results

@router.get("/users")
def get_admin_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at
        }
        for u in users
    ]

@router.get("/ingestion-logs")
def get_ingestion_logs(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).limit(15).all()
    logs = []
    for d in docs:
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).count()
        logs.append({
            "document_id": d.id,
            "title": d.title,
            "mission": d.mission_name,
            "status": d.processing_status,
            "pages": d.total_pages or 0,
            "chunks_generated": chunks,
            "timestamp": d.created_at.isoformat() if d.created_at else None,
            "error": d.error_message
        })
    return logs
