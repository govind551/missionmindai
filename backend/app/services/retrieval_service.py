import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, text
from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.providers.embedding_provider import embedding_provider
from app.utils.confidence import compute_lexical_overlap, calculate_retrieval_confidence
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

class RetrievalService:
    @staticmethod
    def hybrid_retrieve(
        db: Session,
        query: str,
        top_k: int = 5,
        mission_filter: Optional[str] = None,
        agency_filter: Optional[str] = None,
        subsystem_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid retrieval:
        1. Dense semantic vector similarity
        2. Lexical keyword filtering & overlap
        3. Reciprocal Rank Fusion / Weighted Score
        4. Calculates confidence score
        """
        query_embedding = embedding_provider.get_embedding(query)
        
        # Query chunks with document relations
        query_builder = db.query(DocumentChunk, Document).join(Document, DocumentChunk.document_id == Document.id)
        
        if agency_filter:
            query_builder = query_builder.filter(Document.space_agency.ilike(f"%{agency_filter}%"))
        if mission_filter:
            query_builder = query_builder.filter(Document.mission_name.ilike(f"%{mission_filter}%"))
            
        all_chunks = query_builder.all()
        if not all_chunks:
            return []

        scored_results = []
        for chunk, doc in all_chunks:
            chunk_vec = chunk.embedding
            if chunk_vec:
                dense_sim = cosine_similarity(query_embedding, chunk_vec)
            else:
                dense_sim = 0.0

            lexical_sim = compute_lexical_overlap(query, chunk.chunk_text)
            
            # Subsystem keyword relevance boost if matched in chunk or title
            subsystem_boost = 0.0
            if subsystem_filter and (subsystem_filter.lower() in chunk.chunk_text.lower() or subsystem_filter.lower() in doc.title.lower()):
                subsystem_boost = 0.15

            # Calculate unified confidence
            hybrid_score = calculate_retrieval_confidence(dense_sim + subsystem_boost, lexical_sim)

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
                "page_number": chunk.page_number,
                "section_heading": chunk.section_heading,
                "chunk_text": chunk.chunk_text,
                "dense_score": round(dense_sim, 4),
                "lexical_score": round(lexical_sim, 4),
                "hybrid_score": hybrid_score
            })

        # Rank by hybrid score descending
        scored_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        top_results = scored_results[:top_k]
        return top_results
