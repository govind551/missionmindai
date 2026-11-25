import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.document import DocumentOut, DocumentProcessingStatus
from app.services.document_processor import DocumentProcessor
from app.core.config import settings

router = APIRouter(prefix="/documents", tags=["Document Management"])

@router.get("", response_model=List[DocumentOut])
def list_documents(
    agency: Optional[str] = None,
    mission: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    if agency:
        query = query.filter(Document.space_agency.ilike(f"%{agency}%"))
    if mission:
        query = query.filter(Document.mission_name.ilike(f"%{mission}%"))
    if search:
        query = query.filter(Document.title.ilike(f"%{search}%"))

    docs = query.order_by(Document.created_at.desc()).all()
    results = []
    for d in docs:
        chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).count()
        out = DocumentOut(
            id=d.id,
            title=d.title,
            mission_name=d.mission_name,
            space_agency=d.space_agency,
            publication_year=d.publication_year,
            document_type=d.document_type,
            source_url=d.source_url,
            licence=d.licence,
            file_path=d.file_path,
            total_pages=d.total_pages or 0,
            processing_status=d.processing_status,
            error_message=d.error_message,
            created_at=d.created_at,
            chunk_count=chunk_count
        )
        results.append(out)
    return results

@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    mission_name: str = Form(...),
    space_agency: str = Form(...),
    publication_year: Optional[int] = Form(None),
    document_type: Optional[str] = Form("Mishap Investigation Report"),
    source_url: Optional[str] = Form(None),
    licence: Optional[str] = Form("Public Domain / Official Government Release"),
    db: Session = Depends(get_db)
):
    # Validate PDF extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are supported for aerospace technical ingestion."
        )

    # Check for duplicate document
    existing = db.query(Document).filter(
        Document.title == title,
        Document.mission_name == mission_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A document with this title and mission name has already been indexed."
        )

    # Save file
    safe_filename = f"{space_agency.lower()}_{file.filename.replace(' ', '_')}"
    target_path = Path(settings.UPLOAD_DIRECTORY) / safe_filename
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_doc = Document(
        title=title,
        mission_name=mission_name,
        space_agency=space_agency,
        publication_year=publication_year,
        document_type=document_type,
        source_url=source_url,
        licence=licence,
        file_path=str(target_path),
        processing_status="pending"
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Run processing pipeline synchronously for hackathon instant readiness
    DocumentProcessor.process_pdf_document(db, new_doc.id)
    db.refresh(new_doc)

    chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == new_doc.id).count()
    return DocumentOut(
        id=new_doc.id,
        title=new_doc.title,
        mission_name=new_doc.mission_name,
        space_agency=new_doc.space_agency,
        publication_year=new_doc.publication_year,
        document_type=new_doc.document_type,
        source_url=new_doc.source_url,
        licence=new_doc.licence,
        file_path=new_doc.file_path,
        total_pages=new_doc.total_pages or 0,
        processing_status=new_doc.processing_status,
        error_message=new_doc.error_message,
        created_at=new_doc.created_at,
        chunk_count=chunk_count
    )

@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    d = db.query(Document).filter(Document.id == document_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Document not found")
    chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).count()
    return DocumentOut(
        id=d.id,
        title=d.title,
        mission_name=d.mission_name,
        space_agency=d.space_agency,
        publication_year=d.publication_year,
        document_type=d.document_type,
        source_url=d.source_url,
        licence=d.licence,
        file_path=d.file_path,
        total_pages=d.total_pages or 0,
        processing_status=d.processing_status,
        error_message=d.error_message,
        created_at=d.created_at,
        chunk_count=chunk_count
    )

@router.post("/{document_id}/process", response_model=DocumentProcessingStatus)
def reprocess_document(document_id: int, db: Session = Depends(get_db)):
    result = DocumentProcessor.process_pdf_document(db, document_id)
    return DocumentProcessingStatus(
        document_id=result["document_id"],
        status=result["status"],
        total_pages=result["total_pages"],
        total_chunks=result["total_chunks"],
        error_message=result.get("error")
    )

@router.get("/{document_id}/status", response_model=DocumentProcessingStatus)
def get_document_status(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
    return DocumentProcessingStatus(
        document_id=doc.id,
        status=doc.processing_status,
        total_pages=doc.total_pages or 0,
        total_chunks=chunk_count,
        error_message=doc.error_message
    )

@router.get("/{document_id}/pdf")
def stream_pdf(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Document PDF binary not found on server")
    return FileResponse(
        doc.file_path,
        media_type="application/pdf",
        filename=Path(doc.file_path).name
    )

@router.get("/{document_id}/pages/{page_number}")
def get_page_content(document_id: int, page_number: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id,
        DocumentChunk.page_number == page_number
    ).all()
    
    return {
        "document_id": doc.id,
        "document_title": doc.title,
        "page_number": page_number,
        "source_url": doc.source_url,
        "chunks": [
            {
                "id": c.id,
                "section_heading": c.section_heading,
                "text": c.chunk_text
            }
            for c in chunks
        ]
    }

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass
    db.delete(doc)
    db.commit()
    return {"message": f"Document #{document_id} and associated indexed chunks deleted"}
