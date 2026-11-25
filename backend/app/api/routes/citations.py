from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.schemas.citation import CitationDetail

router = APIRouter(prefix="/citations", tags=["Citation Viewer"])

@router.get("/{chunk_id}", response_model=CitationDetail)
def get_citation_detail(chunk_id: int, db: Session = Depends(get_db)):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Citation chunk not found")
    
    doc = db.query(Document).filter(Document.id == chunk.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Parent document not found")

    return CitationDetail(
        chunk_id=chunk.id,
        document_id=doc.id,
        document_title=doc.title,
        mission_name=doc.mission_name,
        space_agency=doc.space_agency,
        page_number=chunk.page_number,
        section_heading=chunk.section_heading,
        chunk_text=chunk.chunk_text,
        source_url=doc.source_url,
        licence=doc.licence,
        metadata=chunk.chunk_metadata
    )
