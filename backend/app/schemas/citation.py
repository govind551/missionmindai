from typing import Optional, Dict, Any
from pydantic import BaseModel

class CitationItem(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    mission_name: str
    space_agency: str
    page_number: int
    section_heading: Optional[str] = None
    snippet: str
    score: Optional[float] = None
    source_url: Optional[str] = None

class CitationDetail(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    mission_name: str
    space_agency: str
    page_number: int
    section_heading: Optional[str] = None
    chunk_text: str
    source_url: Optional[str] = None
    licence: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
