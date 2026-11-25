from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.failure_incident import FailureIncident
from app.models.mission import Mission
from app.models.document import Document
from app.providers.embedding_provider import embedding_provider
from app.services.retrieval_service import cosine_similarity
from app.utils.confidence import compute_lexical_overlap
from app.core.logging import logger

class FailureIntelligenceService:
    @staticmethod
    def find_similar_failures(
        db: Session,
        problem_description: str,
        subsystem_filter: Optional[str] = None,
        agency_filter: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Calculates similarity between incoming engineering problem description
        and historical mission failure incidents using:
        - Dense vector semantic matching between query and failure description / root cause
        - Subsystem domain matching
        - Keyword overlap
        """
        query_vec = embedding_provider.get_embedding(problem_description)

        query = db.query(FailureIncident, Mission, Document).\
            outerjoin(Mission, FailureIncident.mission_id == Mission.id).\
            outerjoin(Document, FailureIncident.document_id == Document.id)

        if agency_filter:
            query = query.filter(Mission.space_agency.ilike(f"%{agency_filter}%"))
        if subsystem_filter:
            query = query.filter(FailureIncident.subsystem.ilike(f"%{subsystem_filter}%"))

        incidents = query.all()
        if not incidents:
            return []

        ranked_results = []
        for incident, mission, doc in incidents:
            combined_incident_text = (
                f"{incident.failure_description} {incident.subsystem} "
                f"{incident.root_cause} {incident.failure_mode or ''}"
            )
            incident_vec = embedding_provider.get_embedding(combined_incident_text)
            
            # Compute actual cosine similarity
            sim = cosine_similarity(query_vec, incident_vec)
            lexical_sim = compute_lexical_overlap(problem_description, combined_incident_text)
            
            # Subsystem match boost
            subsystem_match_boost = 0.0
            if incident.subsystem.lower() in problem_description.lower():
                subsystem_match_boost = 0.20
            
            # Unified similarity score (0.0 to 1.0)
            score = round((0.60 * sim) + (0.25 * lexical_sim) + subsystem_match_boost, 4)
            score = min(score, 0.99)  # Keep realistic upper bound

            citation_data = []
            if doc:
                citation_data.append({
                    "document_id": doc.id,
                    "document_title": doc.title,
                    "source_url": doc.source_url,
                    "page_number": incident.source_page or 1
                })

            ranked_results.append({
                "id": incident.id,
                "mission_name": mission.mission_name if mission else (doc.mission_name if doc else "Unknown"),
                "space_agency": mission.space_agency if mission else (doc.space_agency if doc else "NASA/ISRO"),
                "subsystem": incident.subsystem,
                "failure_description": incident.failure_description,
                "failure_mode": incident.failure_mode,
                "trigger": incident.trigger,
                "root_cause": incident.root_cause,
                "mission_phase": incident.mission_phase,
                "mission_impact": incident.mission_impact,
                "corrective_action": incident.corrective_action,
                "source_page": incident.source_page,
                "document_id": doc.id if doc else None,
                "document_title": doc.title if doc else None,
                "similarity_score": score,
                "citations": citation_data
            })

        # Sort in descending order of similarity score
        ranked_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return ranked_results[:top_k]
