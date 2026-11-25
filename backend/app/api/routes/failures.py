from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.failure import FailureQueryRequest, FailureIncidentOut
from app.services.failure_intelligence_service import FailureIntelligenceService
from app.models.failure_incident import FailureIncident
from app.models.mission import Mission
from app.models.document import Document

router = APIRouter(prefix="/failures", tags=["Similar Past Failures"])

@router.post("/similar", response_model=List[FailureIncidentOut])
def find_similar_failures(req: FailureQueryRequest, db: Session = Depends(get_db)):
    results = FailureIntelligenceService.find_similar_failures(
        db=db,
        problem_description=req.problem_description,
        subsystem_filter=req.subsystem,
        agency_filter=req.agency,
        top_k=req.top_k or 5
    )
    return results

@router.get("", response_model=List[FailureIncidentOut])
def list_failures(db: Session = Depends(get_db)):
    incidents = db.query(FailureIncident, Mission, Document).\
        outerjoin(Mission, FailureIncident.mission_id == Mission.id).\
        outerjoin(Document, FailureIncident.document_id == Document.id).all()
    
    out = []
    for inc, mission, doc in incidents:
        citations = []
        if doc:
            citations.append({
                "document_id": doc.id,
                "document_title": doc.title,
                "source_url": doc.source_url,
                "page_number": inc.source_page or 1
            })
        out.append(FailureIncidentOut(
            id=inc.id,
            mission_name=mission.mission_name if mission else (doc.mission_name if doc else "Unknown"),
            space_agency=mission.space_agency if mission else (doc.space_agency if doc else "NASA/ISRO"),
            subsystem=inc.subsystem,
            failure_description=inc.failure_description,
            failure_mode=inc.failure_mode,
            trigger=inc.trigger,
            root_cause=inc.root_cause,
            mission_phase=inc.mission_phase,
            mission_impact=inc.mission_impact,
            corrective_action=inc.corrective_action,
            source_page=inc.source_page,
            document_id=doc.id if doc else None,
            document_title=doc.title if doc else None,
            similarity_score=1.0,
            citations=citations
        ))
    return out

@router.get("/{incident_id}", response_model=FailureIncidentOut)
def get_failure(incident_id: int, db: Session = Depends(get_db)):
    res = db.query(FailureIncident, Mission, Document).\
        outerjoin(Mission, FailureIncident.mission_id == Mission.id).\
        outerjoin(Document, FailureIncident.document_id == Document.id).\
        filter(FailureIncident.id == incident_id).first()
    
    if not res:
        raise HTTPException(status_code=404, detail="Failure incident not found")
    
    inc, mission, doc = res
    citations = []
    if doc:
        citations.append({
            "document_id": doc.id,
            "document_title": doc.title,
            "source_url": doc.source_url,
            "page_number": inc.source_page or 1
        })

    return FailureIncidentOut(
        id=inc.id,
        mission_name=mission.mission_name if mission else (doc.mission_name if doc else "Unknown"),
        space_agency=mission.space_agency if mission else (doc.space_agency if doc else "NASA/ISRO"),
        subsystem=inc.subsystem,
        failure_description=inc.failure_description,
        failure_mode=inc.failure_mode,
        trigger=inc.trigger,
        root_cause=inc.root_cause,
        mission_phase=inc.mission_phase,
        mission_impact=inc.mission_impact,
        corrective_action=inc.corrective_action,
        source_page=inc.source_page,
        document_id=doc.id if doc else None,
        document_title=doc.title if doc else None,
        similarity_score=1.0,
        citations=citations
    )
