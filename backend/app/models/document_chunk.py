import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False, index=True)
    section_heading = Column(String(300), nullable=True)
    chunk_text = Column(Text, nullable=False)
    # Stored as JSON array or serialized vector for universal compatibility with PostgreSQL and SQLite
    embedding_json = Column(Text, nullable=True)
    chunk_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")
    failure_events = relationship("FailureEvent", back_populates="evidence_chunk")

    @property
    def embedding(self):
        if self.embedding_json:
            try:
                return json.loads(self.embedding_json)
            except Exception:
                return None
        return None

    @embedding.setter
    def embedding(self, value):
        if value is not None:
            if isinstance(value, str):
                self.embedding_json = value
            else:
                self.embedding_json = json.dumps(list(value))
        else:
            self.embedding_json = None
