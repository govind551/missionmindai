from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.api.dependencies import get_optional_current_user
from app.models.user import User
from app.models.research_session import ResearchSession
from app.models.research_message import ResearchMessage
from app.schemas.chat import (
    QuestionRequest, AnswerResponse, ResearchSessionOut,
    ResearchSessionCreate, ResearchMessageOut, SessionSummaryOut
)
from app.services.rag_service import RAGService
from app.services.report_service import ReportService

router = APIRouter(prefix="/chat", tags=["Research Assistant"])

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    req: QuestionRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    result = await RAGService.answer_question(
        db=db,
        question=req.question,
        user_id=user_id,
        session_id=req.session_id,
        mission_filter=req.mission_filter,
        subsystem_filter=req.subsystem_filter,
        agency_filter=req.agency_filter,
        document_id=req.document_id,
        is_all_reports=req.is_all_reports
    )
    return result

@router.get("/sessions", response_model=List[ResearchSessionOut])
def get_sessions(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    sessions = db.query(ResearchSession).filter(
        ResearchSession.user_id == user_id
    ).order_by(ResearchSession.updated_at.desc()).all()
    return sessions

@router.post("/sessions", response_model=ResearchSessionOut)
def create_session(
    data: ResearchSessionCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    session = ResearchSession(
        user_id=user_id,
        title=data.title or "New Aerospace Investigation"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions/{session_id}", response_model=ResearchSessionOut)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found")
    return session

@router.get("/sessions/{session_id}/summary", response_model=SessionSummaryOut)
def get_session_summary(session_id: int, db: Session = Depends(get_db)):
    try:
        summary = ReportService.get_session_summary_data(db, session_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found")
    db.delete(session)
    db.commit()
    return {"message": "Session deleted successfully"}
