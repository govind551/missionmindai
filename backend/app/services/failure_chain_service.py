from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.failure_incident import FailureIncident
from app.models.failure_event import FailureEvent
from app.models.mission import Mission
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.core.logging import logger

class FailureChainService:
    @staticmethod
    def get_failure_chain_by_incident(db: Session, incident_id: int) -> Dict[str, Any]:
        """
        Retrieves the verified causal failure chain events for a specific incident.
        """
        incident = db.query(FailureIncident).filter(FailureIncident.id == incident_id).first()
        if not incident:
            return None

        mission = db.query(Mission).filter(Mission.id == incident.mission_id).first()
        doc = db.query(Document).filter(Document.id == incident.document_id).first()

        events = db.query(FailureEvent).filter(
            FailureEvent.incident_id == incident_id
        ).order_by(FailureEvent.event_order.asc()).all()

        formatted_events = []
        for e in events:
            formatted_events.append({
                "id": e.id,
                "incident_id": e.incident_id,
                "event_order": e.event_order,
                "event_title": e.event_title,
                "event_description": e.event_description,
                "event_type": e.event_type,
                "relationship_type": e.relationship_type,
                "event_timestamp": e.event_timestamp,
                "source_page": e.source_page or incident.source_page,
                "evidence_chunk_id": e.evidence_chunk_id,
                "document_title": doc.title if doc else "Official Mishap Report",
                "source_url": doc.source_url if doc else None
            })

        return {
            "incident_id": incident.id,
            "mission_name": mission.mission_name if mission else (doc.mission_name if doc else "Space Mission"),
            "space_agency": mission.space_agency if mission else (doc.space_agency if doc else "NASA/ISRO"),
            "subsystem": incident.subsystem,
            "root_cause": incident.root_cause,
            "mission_impact": incident.mission_impact,
            "events": formatted_events,
            "methodology_note": "Reconstructed from verified official investigation board event timelines."
        }

    @staticmethod
    def list_missions_with_chains(db: Session) -> List[Dict[str, Any]]:
        """Lists all missions and incidents that have documented failure chains"""
        incidents = db.query(FailureIncident, Mission, Document).\
            outerjoin(Mission, FailureIncident.mission_id == Mission.id).\
            outerjoin(Document, FailureIncident.document_id == Document.id).all()

        results = []
        for inc, mission, doc in incidents:
            event_count = db.query(FailureEvent).filter(FailureEvent.incident_id == inc.id).count()
            results.append({
                "incident_id": inc.id,
                "mission_name": mission.mission_name if mission else (doc.mission_name if doc else "Mission"),
                "space_agency": mission.space_agency if mission else (doc.space_agency if doc else "Agency"),
                "subsystem": inc.subsystem,
                "event_count": event_count,
                "root_cause": inc.root_cause,
                "mission_impact": inc.mission_impact
            })
        return results
