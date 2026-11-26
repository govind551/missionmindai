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

def resolve_or_generate_document_pdf(doc: Document, db: Session) -> Optional[str]:
    """
    Ensures that a valid PDF file exists for the document on the server.
    Tries multiple location candidates. If missing on disk but chunks exist in the DB,
    automatically constructs a clean, official PDF using ReportLab matching the exact
    page bounds and chunk text, guaranteeing the user can inspect the PDF without 404 errors.
    """
    if not doc:
        return None

    # Check candidates for existing file on disk
    candidates = []
    if doc.file_path:
        candidates.append(os.path.abspath(doc.file_path))
        candidates.append(os.path.abspath(os.path.join(settings.UPLOAD_DIRECTORY, os.path.basename(doc.file_path))))
        candidates.append(os.path.abspath(os.path.join(str(settings.BASE_DIR), doc.file_path)))
        candidates.append(os.path.abspath(os.path.join(str(settings.BASE_DIR.parent), doc.file_path)))

    for cand in candidates:
        if os.path.exists(cand) and os.path.isfile(cand):
            if doc.file_path != cand:
                doc.file_path = cand
                db.commit()
            return cand

    # If no file on disk, check if chunks exist to construct PDF
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == doc.id
    ).order_by(DocumentChunk.page_number, DocumentChunk.id).all()

    if not chunks:
        return None

    try:
        import re
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors

        clean_agency = re.sub(r'[^a-zA-Z0-9]', '_', doc.space_agency or 'agency')
        clean_mission = re.sub(r'[^a-zA-Z0-9]', '_', doc.mission_name or 'mission')
        safe_name = f"{clean_agency}_{doc.id}_{clean_mission}.pdf"
        out_path = os.path.join(settings.UPLOAD_DIRECTORY, safe_name)

        doc_tmpl = SimpleDocTemplate(
            out_path, pagesize=letter,
            leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle', parent=styles['Heading1'], fontSize=15, leading=19,
            textColor=colors.HexColor('#1e1b4b'), spaceAfter=8
        )
        meta_style = ParagraphStyle(
            'DocMeta', parent=styles['Normal'], fontSize=9, leading=12,
            textColor=colors.HexColor('#475569'), spaceAfter=12
        )
        heading_style = ParagraphStyle(
            'SecHead', parent=styles['Heading2'], fontSize=11, leading=14,
            textColor=colors.HexColor('#4338ca'), spaceBefore=8, spaceAfter=4
        )
        body_style = ParagraphStyle(
            'BodyTextCustom', parent=styles['Normal'], fontSize=9, leading=13,
            textColor=colors.HexColor('#1e293b'), spaceAfter=6
        )

        pages_dict = {}
        for c in chunks:
            pages_dict.setdefault(c.page_number, []).append((c.section_heading, c.chunk_text))

        story = []
        max_p = max(pages_dict.keys())
        for p_num in sorted(pages_dict.keys()):
            header_text = f"<b>OFFICIAL INVESTIGATION REPORT // {doc.space_agency} // {doc.mission_name} // PAGE {p_num}</b>"
            story.append(Paragraph(header_text, meta_style))
            if p_num == 1:
                story.append(Paragraph(f"<b>{doc.title}</b>", title_style))
                story.append(Spacer(1, 8))

            for s_head, text in pages_dict[p_num]:
                if s_head:
                    clean_head = s_head.replace('\n', ' ').strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(f"<b>{clean_head}</b>", heading_style))

                clean_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
                story.append(Paragraph(clean_text, body_style))
                story.append(Spacer(1, 4))

            if p_num != max_p:
                story.append(PageBreak())

        doc_tmpl.build(story)
        doc.file_path = out_path
        doc.total_pages = max_p
        db.commit()
        return out_path
    except Exception:
        return None

@router.get("/{document_id}/pdf")
def stream_pdf(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    valid_pdf_path = resolve_or_generate_document_pdf(doc, db)
    if not valid_pdf_path or not os.path.exists(valid_pdf_path):
        raise HTTPException(status_code=404, detail="Document PDF binary not found on server")
    # Return with Content-Disposition inline to prevent browser auto-downloading
    return FileResponse(
        valid_pdf_path,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"}
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
        "mission_name": doc.mission_name,
        "space_agency": doc.space_agency,
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
