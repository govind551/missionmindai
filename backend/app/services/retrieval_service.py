import numpy as np
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.providers.embedding_provider import embedding_provider
from app.utils.confidence import compute_lexical_overlap, calculate_retrieval_confidence
from app.services.mission_detector import MISSION_CATALOG, detect_query_intent
from app.core.config import settings
from app.core.logging import logger

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))

def doc_matches_mission(doc: Document, mission_targets: List[str]) -> bool:
    """
    Checks if a document belongs to any of the specified target missions.
    """
    if not mission_targets:
        return True

    doc_str = f"{doc.mission_name or ''} {doc.title or ''} {doc.file_path or ''}".lower()

    for target in mission_targets:
        t_low = target.lower()
        if t_low in doc_str:
            return True
        for m in MISSION_CATALOG:
            if m["canonical_name"].lower() == t_low or t_low in m["canonical_name"].lower():
                if any(kw in doc_str for kw in m["keywords"]):
                    return True
    return False

class RetrievalService:
    @staticmethod
    def hybrid_retrieve(
        db: Session,
        query: str,
        top_k: int = 5,
        mission_filter: Optional[Union[str, List[str]]] = None,
        agency_filter: Optional[str] = None,
        subsystem_filter: Optional[str] = None,
        query_intent: Optional[str] = None,
        document_id_filter: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes mission-filtered hybrid retrieval with intent-based passage reranking:
        1. Dense vector semantic similarity
        2. Lexical keyword overlap
        3. Strict document / mission-level filtering
        4. Intent-specific passage boost (prioritizing direct answers to question intent)
        5. Preserves physical 1-based PDF page positions
        """
        query_embedding = embedding_provider.get_embedding(query)
        if not query_intent:
            query_intent = detect_query_intent(query)

        # Normalize mission targets
        mission_targets = []
        if mission_filter and not document_id_filter:
            if isinstance(mission_filter, str):
                mission_targets = [mission_filter]
            else:
                mission_targets = list(mission_filter)

        # Query chunks with document relations
        query_builder = db.query(DocumentChunk, Document).join(Document, DocumentChunk.document_id == Document.id)

        if document_id_filter:
            query_builder = query_builder.filter(Document.id == document_id_filter)
        elif agency_filter:
            query_builder = query_builder.filter(Document.space_agency.ilike(f"%{agency_filter}%"))

        all_chunks = query_builder.all()
        if not all_chunks:
            return []

        # Filter strictly by mission if mission_targets provided (and not single document)
        if mission_targets and not document_id_filter:
            filtered_chunks = [(c, d) for c, d in all_chunks if doc_matches_mission(d, mission_targets)]
        else:
            filtered_chunks = all_chunks

        if not filtered_chunks:
            logger.info(f"No chunks matched mission filter: {mission_targets}")
            return []

        scored_results = []
        for chunk, doc in filtered_chunks:
            chunk_vec = chunk.embedding
            if chunk_vec:
                dense_sim = cosine_similarity(query_embedding, chunk_vec)
            else:
                dense_sim = 0.0

            lexical_sim = compute_lexical_overlap(query, chunk.chunk_text)

            # Subsystem keyword relevance boost if matched
            subsystem_boost = 0.0
            if subsystem_filter and (subsystem_filter.lower() in chunk.chunk_text.lower() or subsystem_filter.lower() in (doc.title or "").lower()):
                subsystem_boost = 0.15

            # Base hybrid score
            hybrid_score = calculate_retrieval_confidence(dense_sim + subsystem_boost, lexical_sim)

            # Intent-based passage reranking boost
            chunk_lower = chunk.chunk_text.lower()
            intent_boost = 0.0

            if query_intent == "mission_impact":
                impact_terms = [
                    'loss of vehicle', 'loss of mission', 'loss of crew', 'destroyed', 'destruction',
                    'impacted the ground', 'fatalities', 'breakup', 'failed to attain', 'failed to reach',
                    'sub-orbital', 'disintegration', 'debris', 'crashed', 'terminal impact', 'lost',
                    'loss of all seven', 'unfulfilled'
                ]
                impact_matches = sum(1 for term in impact_terms if term in chunk_lower)
                if impact_matches > 0:
                    intent_boost = min(0.35, 0.12 * impact_matches)

            elif query_intent == "root_cause":
                root_terms = [
                    'root cause', 'proximate cause', 'caused by', 'failure mechanism',
                    'inadequate', 'defect', 'initiated by', 'flaw', 'forensic investigation'
                ]
                root_matches = sum(1 for term in root_terms if term in chunk_lower)
                if root_matches > 0:
                    intent_boost = min(0.30, 0.12 * root_matches)

            elif query_intent == "corrective_action":
                corrective_terms = [
                    'recommendation', 'corrective action', 'prevent', 'redesign', 'return to flight',
                    'lessons learned', 'directives', 'findings and recommendations'
                ]
                corr_matches = sum(1 for term in corrective_terms if term in chunk_lower)
                if corr_matches > 0:
                    intent_boost = min(0.30, 0.12 * corr_matches)

            final_score = min(1.0, round(hybrid_score + intent_boost, 4))

            # Retrieve printed page from metadata if available, otherwise physical page
            meta = chunk.chunk_metadata or {}
            printed_page = meta.get("printed_page", chunk.page_number)

            scored_results.append({
                "chunk_id": chunk.id,
                "document_id": doc.id,
                "document_title": doc.title,
                "mission_name": doc.mission_name,
                "space_agency": doc.space_agency,
                "publication_year": doc.publication_year,
                "document_type": doc.document_type,
                "source_url": doc.source_url,
                "licence": doc.licence,
                "page_number": chunk.page_number,  # Physical 1-based page for PDF viewer navigation
                "printed_page": printed_page,
                "section_heading": chunk.section_heading,
                "chunk_text": chunk.chunk_text,
                "dense_score": round(dense_sim, 4),
                "lexical_score": round(lexical_sim, 4),
                "intent_boost": round(intent_boost, 4),
                "hybrid_score": final_score
            })

        # Rank by final hybrid score descending
        scored_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        top_results = scored_results[:top_k]
        return top_results
