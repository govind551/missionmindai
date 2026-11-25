import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.api.dependencies import get_optional_current_user
from app.models.user import User
from app.models.generated_report import GeneratedReport
from app.schemas.report import ReportGenerateRequest, ReportOut
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Research Reports (PDF)"])

@router.post("/generate", response_model=ReportOut)
def generate_report(
    req: ReportGenerateRequest,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    report = ReportService.generate_research_pdf(
        db=db,
        user_id=user_id,
        session_id=req.session_id,
        report_title=req.report_title or "MISSIONMIND Aerospace Technical Investigation Report",
        include_failure_chain=req.include_failure_chain if req.include_failure_chain is not None else True,
        include_similar_failures=req.include_similar_failures if req.include_similar_failures is not None else True,
        custom_notes=req.custom_notes
    )

    return ReportOut(
        id=report.id,
        user_id=report.user_id,
        session_id=report.session_id,
        report_title=report.report_title,
        file_path=report.file_path,
        download_url=f"/api/reports/{report.id}/download",
        created_at=report.created_at
    )

@router.get("", response_model=List[ReportOut])
def list_reports(
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    reports = db.query(GeneratedReport).filter(
        GeneratedReport.user_id == user_id
    ).order_by(GeneratedReport.created_at.desc()).all()

    return [
        ReportOut(
            id=r.id,
            user_id=r.user_id,
            session_id=r.session_id,
            report_title=r.report_title,
            file_path=r.file_path,
            download_url=f"/api/reports/{r.id}/download",
            created_at=r.created_at
        )
        for r in reports
    ]

@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportOut(
        id=r.id,
        user_id=r.user_id,
        session_id=r.session_id,
        report_title=r.report_title,
        file_path=r.file_path,
        download_url=f"/api/reports/{r.id}/download",
        created_at=r.created_at
    )

@router.get("/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
    if not r or not os.path.exists(r.file_path):
        raise HTTPException(status_code=404, detail="Report PDF file not found")
    
    filename = os.path.basename(r.file_path)
    return FileResponse(
        r.file_path,
        media_type="application/pdf",
        filename=filename
    )

@router.get("/session/{session_id}/download-latest")
def download_latest_session_report(
    session_id: int,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else 1
    report = ReportService.generate_research_pdf(
        db=db,
        user_id=user_id,
        session_id=session_id,
        report_title="MISSIONMIND AI – Technical Investigation Report"
    )
    filename = os.path.basename(report.file_path)
    return FileResponse(
        report.file_path,
        media_type="application/pdf",
        filename=filename
    )
