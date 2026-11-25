from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.retrieval_service import RetrievalService
from app.providers.llm_provider import llm_provider
from app.models.research_session import ResearchSession
from app.models.research_message import ResearchMessage
from app.schemas.citation import CitationItem
from app.core.config import settings
from app.core.logging import logger

class RAGService:
    @staticmethod
    async def answer_question(
        db: Session,
        question: str,
        user_id: int,
        session_id: Optional[int] = None,
        subsystem_filter: Optional[str] = None,
        agency_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full RAG pipeline:
        1. Ensure active research session
        2. Execute hybrid retrieval
        3. Evaluate confidence score
        4. Generate grounded LLM response
        5. Verify citations against retrieved chunks
        6. Persist Q&A in research session
        """
        # 1. Manage research session
        if not session_id:
            session = ResearchSession(
                user_id=user_id,
                title=f"Investigation: {question[:45]}..." if len(question) > 45 else f"Investigation: {question}"
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            session_id = session.id
        else:
            session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
            if not session:
                session = ResearchSession(user_id=user_id, title=f"Investigation: {question[:45]}...")
                db.add(session)
                db.commit()
                db.refresh(session)
                session_id = session.id

        # Record user question
        user_msg = ResearchMessage(
            session_id=session_id,
            role="user",
            message_text=question
        )
        db.add(user_msg)
        db.commit()

        # 2. Hybrid Retrieval
        retrieved_chunks = RetrievalService.hybrid_retrieve(
            db=db,
            query=question,
            top_k=settings.RETRIEVAL_TOP_K,
            subsystem_filter=subsystem_filter,
            agency_filter=agency_filter
        )

        # 3. Confidence determination
        if retrieved_chunks:
            top_confidence = retrieved_chunks[0]["hybrid_score"]
        else:
            top_confidence = 0.0

        # 4. LLM Generation with grounding
        llm_result = await llm_provider.generate_grounded_answer(
            question=question,
            evidence_chunks=retrieved_chunks,
            confidence=top_confidence
        )

        # 5. Format and validate citations
        citations = []
        relevant_missions = []
        if llm_result["is_grounded"]:
            for c in retrieved_chunks:
                citations.append(CitationItem(
                    chunk_id=c["chunk_id"],
                    document_id=c["document_id"],
                    document_title=c["document_title"],
                    mission_name=c["mission_name"],
                    space_agency=c["space_agency"],
                    page_number=c["page_number"],
                    section_heading=c.get("section_heading"),
                    snippet=c["chunk_text"][:280] + "..." if len(c["chunk_text"]) > 280 else c["chunk_text"],
                    score=c["hybrid_score"],
                    source_url=c.get("source_url")
                ))
                if c["mission_name"] not in relevant_missions:
                    relevant_missions.append(c["mission_name"])

        # 6. Save assistant answer
        citations_data = [cit.dict() for cit in citations]
        assistant_msg = ResearchMessage(
            session_id=session_id,
            role="assistant",
            message_text=llm_result["answer"],
            citations=citations_data,
            retrieval_confidence=top_confidence
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)

        return {
            "answer": llm_result["answer"],
            "retrieval_confidence": top_confidence,
            "is_grounded": llm_result["is_grounded"],
            "citations": citations,
            "relevant_missions": relevant_missions,
            "session_id": session_id,
            "message_id": assistant_msg.id,
            "created_at": assistant_msg.created_at
        }
