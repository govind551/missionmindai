from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class DocumentBase(BaseModel):
    title: str
    mission_name: str
    space_agency: str
    publication_year: Optional[int] = None
    document_type: Optional[str] = "Mishap Investigation Report"
    source_url: Optional[str] = None
    licence: Optional[str] = "Public Domain / Official Government Release"

class DocumentCreate(DocumentBase):
    pass

class DocumentChunkOut(BaseModel):
    id: int
    document_id: int
    page_number: int
    section_heading: Optional[str] = None
    chunk_text: str
    chunk_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class DocumentOut(DocumentBase):
    id: int
    file_path: str
    total_pages: int
    processing_status: str
    error_message: Optional[str] = None
    created_at: datetime
    chunk_count: Optional[int] = 0

    class Config:
        from_attributes = True

class DocumentProcessingStatus(BaseModel):
    document_id: int
    status: str
    total_pages: int
    total_chunks: int
    error_message: Optional[str] = None
