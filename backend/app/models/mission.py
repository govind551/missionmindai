from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base

class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    mission_name = Column(String(200), unique=True, index=True, nullable=False)
    space_agency = Column(String(100), nullable=False)  # NASA, ISRO, ESA, etc.
    launch_year = Column(Integer, nullable=True)
    mission_description = Column(Text, nullable=True)
    outcome = Column(String(50), default="Failure")  # Failure, Partial Failure, Mishap
    created_at = Column(DateTime, default=datetime.utcnow)

    failure_incidents = relationship("FailureIncident", back_populates="mission", cascade="all, delete-orphan")
