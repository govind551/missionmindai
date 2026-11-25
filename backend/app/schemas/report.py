from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class ReportGenerateRequest(BaseModel):
    session_id: int
    report_title: Optional[str] = "MISSIONMIND Aerospace Technical Investigation Report"
    include_failure_chain: Optional[bool] = True
    include_similar_failures: Optional[bool] = True
    custom_notes: Optional[str] = None

class ReportOut(BaseModel):
    id: int
    user_id: int
    session_id: Optional[int]
    report_title: str
    file_path: str
    download_url: str
    created_at: datetime

    class Config:
        from_attributes = True
