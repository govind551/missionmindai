from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.schemas.citation import CitationItem

class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[int] = None
    subsystem_filter: Optional[str] = None
    agency_filter: Optional[str] = None

class AnswerResponse(BaseModel):
    answer: str
    retrieval_confidence: float
    is_grounded: bool
    citations: List[CitationItem]
    relevant_missions: List[str]
    session_id: int
    message_id: int
    created_at: datetime

class ResearchMessageOut(BaseModel):
    id: int
    session_id: int
    role: str
    message_text: str
    citations: Optional[List[Dict[str, Any]]] = None
    retrieval_confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ResearchSessionCreate(BaseModel):
    title: Optional[str] = "New Aerospace Investigation"

class ResearchSessionOut(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[ResearchMessageOut]] = []

    class Config:
        from_attributes = True

class QAPairSummary(BaseModel):
    query_number: int
    question: str
    answer: str
    citations: List[Dict[str, Any]] = []
    retrieval_confidence: float = 0.0
    timestamp: Optional[datetime] = None

class SessionSummaryOut(BaseModel):
    session_id: int
    session_title: str
    total_queries: int
    total_answers: int
    missions_covered: List[str] = []
    agencies_covered: List[str] = []
    total_citations: int
    average_confidence: float
    executive_summary: str
    qa_pairs: List[QAPairSummary] = []
