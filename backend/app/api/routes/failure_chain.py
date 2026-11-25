from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.connection import get_db
from app.services.failure_chain_service import FailureChainService

router = APIRouter(prefix="/failure-chain", tags=["Failure Chain Analyzer"])

class AnalyzeRequest(BaseModel):
    incident_id: int

@router.get("/missions")
def list_available_missions(db: Session = Depends(get_db)):
    return FailureChainService.list_missions_with_chains(db)

@router.get("/{incident_id}")
def get_failure_chain(incident_id: int, db: Session = Depends(get_db)):
    chain = FailureChainService.get_failure_chain_by_incident(db, incident_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Failure chain reconstruction not found for this incident")
    return chain

@router.post("/analyze")
def analyze_chain(req: AnalyzeRequest, db: Session = Depends(get_db)):
    chain = FailureChainService.get_failure_chain_by_incident(db, req.incident_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Incident not found")
    return chain
