from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class FailureIncident(Base):
    __tablename__ = "failure_incidents"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id", ondelete="SET NULL"), nullable=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    failure_description = Column(Text, nullable=False)
    subsystem = Column(String(150), nullable=False, index=True)  # Thermal, Propulsion, Guidance/Software, etc.
    failure_mode = Column(String(200), nullable=True)
    trigger = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=False)
    mission_phase = Column(String(100), nullable=True)
    mission_impact = Column(String(150), nullable=True)
    corrective_action = Column(Text, nullable=True)
    source_page = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    mission = relationship("Mission", back_populates="failure_incidents")
    document = relationship("Document", back_populates="failure_incidents")
    failure_events = relationship("FailureEvent", back_populates="incident", cascade="all, delete-orphan")
