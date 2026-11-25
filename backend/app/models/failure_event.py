from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class FailureEvent(Base):
    __tablename__ = "failure_events"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("failure_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    event_order = Column(Integer, nullable=False)
    event_title = Column(String(250), nullable=False)
    event_description = Column(Text, nullable=False)
    event_type = Column(String(100), default="Documented Event")  # Root Cause, Cascading Failure, Impact, Observation
    relationship_type = Column(String(100), default="Documented Sequence")  # Confirmed Causal, Documented Sequence, Suspected
    event_timestamp = Column(String(100), nullable=True)
    evidence_chunk_id = Column(Integer, ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    source_page = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("FailureIncident", back_populates="failure_events")
    evidence_chunk = relationship("DocumentChunk", back_populates="failure_events")
