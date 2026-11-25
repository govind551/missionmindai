from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="analyst")  # analyst, admin, researcher
    created_at = Column(DateTime, default=datetime.utcnow)

    research_sessions = relationship("ResearchSession", back_populates="user", cascade="all, delete-orphan")
    generated_reports = relationship("GeneratedReport", back_populates="user", cascade="all, delete-orphan")
