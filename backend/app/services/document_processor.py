from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.pdf_extractor import PDFExtractor
from app.services.chunking_service import ChunkingService
from app.providers.embedding_provider import embedding_provider
from app.core.logging import logger

class DocumentProcessor:
    @staticmethod
    def process_pdf_document(
        db: Session,
        document_id: int
    ) -> Dict[str, Any]:
        """
        Executes end-to-end ingestion pipeline:
        1. PyMuPDF extraction
        2. Text cleaning & page preservation
        3. Semantic chunking
        4. Dense vector embedding generation
        5. Atomic database commit
        """
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document ID {document_id} not found")

        doc.processing_status = "processing"
        db.commit()

        try:
            # 1. Extract pages
            pages_data = PDFExtractor.extract_document(doc.file_path)
            doc.total_pages = len(pages_data)

            # 2. Chunk pages
            chunks_data = ChunkingService.chunk_document_pages(pages_data)

            # 3. Clean any existing chunks if re-processing
            db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()

            # 4. Generate embeddings and store
            for c_data in chunks_data:
                embedding_vector = embedding_provider.get_embedding(c_data["chunk_text"])
                
                meta = c_data.get("chunk_metadata") or {}
                meta.update({
                    "page_number": c_data["page_number"],
                    "physical_page": c_data["page_number"],
                    "document_title": doc.title,
                    "mission_name": doc.mission_name,
                    "space_agency": doc.space_agency,
                    "source_url": doc.source_url,
                    "section_heading": c_data.get("section_heading")
                })

                chunk_record = DocumentChunk(
                    document_id=doc.id,
                    page_number=c_data["page_number"],
                    section_heading=c_data["section_heading"],
                    chunk_text=c_data["chunk_text"],
                    chunk_metadata=meta
                )
                chunk_record.embedding = embedding_vector
                db.add(chunk_record)

            doc.processing_status = "completed"
            doc.error_message = None
            db.commit()
            db.refresh(doc)

            # Auto-generate Failure Chain for newly ingested document
            try:
                from app.services.failure_chain_service import FailureChainService
                FailureChainService.generate_chain_for_document(db, doc.id)
            except Exception as fc_err:
                logger.warning(f"Could not auto-generate failure chain for Document #{doc.id}: {fc_err}")

            logger.info(f"Successfully processed Document #{doc.id}: {len(chunks_data)} chunks created.")
            return {
                "document_id": doc.id,
                "status": "completed",
                "total_pages": doc.total_pages,
                "total_chunks": len(chunks_data)
            }
        except Exception as e:
            logger.error(f"Failed processing document #{doc.id}: {e}")
            doc.processing_status = "failed"
            doc.error_message = str(e)
            db.commit()
            return {
                "document_id": doc.id,
                "status": "failed",
                "total_pages": doc.total_pages or 0,
                "total_chunks": 0,
                "error": str(e)
            }
