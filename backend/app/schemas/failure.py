from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class FailureQueryRequest(BaseModel):
    problem_description: str
    subsystem: Optional[str] = None
    agency: Optional[str] = None
    top_k: Optional[int] = 5

class FailureIncidentOut(BaseModel):
    id: int
    mission_name: str
    space_agency: str
    subsystem: str
    failure_description: str
    failure_mode: Optional[str] = None
    trigger: Optional[str] = None
    root_cause: str
    mission_phase: Optional[str] = None
    mission_impact: Optional[str] = None
    corrective_action: Optional[str] = None
    source_page: Optional[int] = None
    document_id: Optional[int] = None
    document_title: Optional[str] = None
    similarity_score: Optional[float] = None
    citations: Optional[List[Dict[str, Any]]] = []

    class Config:
        from_attributes = True

class FailureEventOut(BaseModel):
    id: int
    incident_id: int
    event_order: int
    event_title: str
    event_description: str
    event_type: str
    relationship_type: str
    event_timestamp: Optional[str] = None
    source_page: Optional[int] = None
    evidence_chunk_id: Optional[int] = None

    class Config:
        from_attributes = True

class FailureChainReconstruction(BaseModel):
    mission_name: str
    space_agency: str
    subsystem: str
    incident_id: int
    root_cause: str
    mission_impact: Optional[str] = None
    events: List[FailureEventOut]
    methodology_note: str = "Sequence reconstructed exclusively from official investigation board findings."
