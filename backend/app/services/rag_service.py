from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.services.retrieval_service import RetrievalService
from app.services.mission_detector import resolve_query_missions, detect_query_intent
from app.utils.confidence import evaluate_rag_confidence
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
        mission_filter: Optional[str] = None,
        subsystem_filter: Optional[str] = None,
        agency_filter: Optional[str] = None,
        document_id: Optional[int] = None,
        is_all_reports: Optional[bool] = False
    ) -> Dict[str, Any]:
        """
        Mission-Aware Grounded RAG Pipeline:
        1. Manages conversation session and history
        2. Resolves mission/report context (from specific report, query, session history, or explicit filter)
        3. Prevents cross-mission pollution by filtering chunks strictly to relevant report(s)
        4. Detects intent (mission impact, root cause, timeline) and applies targeted reranking
        5. If mission is ambiguous without context, prompts user to specify the mission
        6. Evaluates multi-dimensional confidence with transparent warnings
        7. Synthesizes structured, cited answers
        8. Persists conversation and citations
        """
        clean_question = question.strip()

        # Check for specific document scope
        from app.models.document import Document
        doc_record = db.query(Document).filter(Document.id == document_id).first() if document_id else None

        # 1. Manage research session
        if not session_id:
            session = ResearchSession(
                user_id=user_id,
                title=f"Investigation: {clean_question[:45]}..." if len(clean_question) > 45 else f"Investigation: {clean_question}"
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            session_id = session.id
        else:
            session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
            if not session:
                session = ResearchSession(user_id=user_id, title=f"Investigation: {clean_question[:45]}...")
                db.add(session)
                db.commit()
                db.refresh(session)
                session_id = session.id

        # Record user question in session
        user_msg = ResearchMessage(
            session_id=session_id,
            role="user",
            message_text=clean_question
        )
        db.add(user_msg)
        db.commit()

        # 2. Resolve Mission Context & Intent
        # If user explicitly selected a specific report or "Select All Reports":
        if doc_record:
            query_intent = detect_query_intent(clean_question)
            retrieved_chunks = RetrievalService.hybrid_retrieve(
                db=db,
                query=clean_question,
                top_k=settings.RETRIEVAL_TOP_K,
                document_id_filter=doc_record.id,
                query_intent=query_intent
            )
            conf_details = evaluate_rag_confidence(
                chunks=retrieved_chunks,
                query=clean_question,
                query_intent=query_intent,
                target_mission=doc_record.mission_name,
                is_comparison=False
            )
            active_mission_name = f"{doc_record.title} ({doc_record.mission_name})"
            comparison_missions = None
            mode = "single"

        elif is_all_reports:
            query_intent = detect_query_intent(clean_question)
            retrieved_chunks = RetrievalService.hybrid_retrieve(
                db=db,
                query=clean_question,
                top_k=settings.RETRIEVAL_TOP_K,
                mission_filter=None,
                document_id_filter=None,
                agency_filter=agency_filter,
                subsystem_filter=subsystem_filter,
                query_intent=query_intent
            )
            conf_details = evaluate_rag_confidence(
                chunks=retrieved_chunks,
                query=clean_question,
                query_intent=query_intent,
                target_mission=None,
                is_comparison=True
            )
            active_mission_name = "All Uploaded Reports"
            comparison_missions = None
            mode = "all_reports"

        else:
            mission_ctx = resolve_query_missions(
                db=db,
                query=clean_question,
                session_id=session_id,
                explicit_mission=mission_filter
            )
            query_intent = mission_ctx["query_intent"]
            mode = mission_ctx["mode"]

            # Case 1: Mission is ambiguous across multiple possibilities
            if mode == "unclear":
                clarification_text = (
                    "Multiple space missions are documented in the investigation library. "
                    "To ensure findings from different flights are not mixed, please specify which mission you would like to examine:\n\n"
                    + "\n".join([f"• **{m}**" for m in mission_ctx.get("available_missions", [])])
                    + "\n\n*For example, try:* \"What impact did the failure have on the Mars Polar Lander mission?\" or \"What happened during Challenger STS-51-L?\""
                )
                conf_details = {
                    "score": 0.0,
                    "level": "AMBIGUOUS",
                    "label": "Mission Clarification Required",
                    "warning": "The query does not specify a mission and no previous mission context is active in this session.",
                    "is_grounded": False,
                    "mission_consistent": True
                }

                assistant_msg = ResearchMessage(
                    session_id=session_id,
                    role="assistant",
                    message_text=clarification_text,
                    citations=[],
                    retrieval_confidence=0.0
                )
                db.add(assistant_msg)
                db.commit()
                db.refresh(assistant_msg)

                return {
                    "answer": clarification_text,
                    "retrieval_confidence": 0.0,
                    "is_grounded": False,
                    "citations": [],
                    "relevant_missions": [],
                    "session_id": session_id,
                    "message_id": assistant_msg.id,
                    "created_at": assistant_msg.created_at,
                    "confidence_details": conf_details,
                    "active_mission": None
                }

            # Case 2: Multi-Mission Comparison
            if mode == "comparison":
                comparison_missions = mission_ctx["missions"]
                retrieved_chunks = []
                for target_m in comparison_missions:
                    m_chunks = RetrievalService.hybrid_retrieve(
                        db=db,
                        query=clean_question,
                        top_k=3,
                        mission_filter=target_m,
                        query_intent=query_intent,
                        agency_filter=agency_filter
                    )
                    retrieved_chunks.extend(m_chunks)

                conf_details = evaluate_rag_confidence(
                    chunks=retrieved_chunks,
                    query=clean_question,
                    query_intent=query_intent,
                    target_mission=None,
                    is_comparison=True
                )
                active_mission_name = " & ".join(comparison_missions)

            # Case 3: Query on unsupported or global topic (no specific mission requested)
            elif mode == "unsupported_or_global":
                retrieved_chunks = RetrievalService.hybrid_retrieve(
                    db=db,
                    query=clean_question,
                    top_k=settings.RETRIEVAL_TOP_K,
                    mission_filter=None,
                    agency_filter=agency_filter,
                    subsystem_filter=subsystem_filter,
                    query_intent=query_intent
                )
                conf_details = evaluate_rag_confidence(
                    chunks=retrieved_chunks,
                    query=clean_question,
                    query_intent=query_intent,
                    target_mission=None,
                    is_comparison=False
                )
                active_mission_name = None
                comparison_missions = None

            # Case 4: Single Mission (Direct from query or preserved from session history)
            else:
                target_mission = mission_ctx["missions"][0]
                retrieved_chunks = RetrievalService.hybrid_retrieve(
                    db=db,
                    query=clean_question,
                    top_k=settings.RETRIEVAL_TOP_K,
                    mission_filter=target_mission,
                    agency_filter=agency_filter,
                    subsystem_filter=subsystem_filter,
                    query_intent=query_intent
                )

                conf_details = evaluate_rag_confidence(
                    chunks=retrieved_chunks,
                    query=clean_question,
                    query_intent=query_intent,
                    target_mission=target_mission,
                    is_comparison=False
                )
                active_mission_name = target_mission
                comparison_missions = None

        top_confidence = conf_details["score"]

        # 3. Formulate Grounded Answer
        llm_result = await llm_provider.generate_grounded_answer(
            question=clean_question,
            evidence_chunks=retrieved_chunks,
            confidence=top_confidence,
            query_intent=query_intent,
            target_mission=active_mission_name if mode == "single" else None,
            comparison_missions=comparison_missions,
            confidence_details=conf_details
        )

        # 4. Format and Validate Citations
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

        # 5. Persist Assistant Response in Research Session
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
            "created_at": assistant_msg.created_at,
            "confidence_details": conf_details,
            "active_mission": active_mission_name
        }
