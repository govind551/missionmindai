from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    mission_name = Column(String(200), nullable=False, index=True)
    space_agency = Column(String(100), nullable=False, index=True)
    publication_year = Column(Integer, nullable=True)
    document_type = Column(String(100), default="Mishap Investigation Report")
    source_url = Column(String(1000), nullable=True)
    licence = Column(String(200), default="Public Domain / Official Government Release")
    file_path = Column(String(500), nullable=False)
    total_pages = Column(Integer, default=0)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    failure_incidents = relationship("FailureIncident", back_populates="document")
