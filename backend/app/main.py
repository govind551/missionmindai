from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.logging import logger
from app.database.connection import init_db

# Import routers
from app.api.routes import (
    auth,
    documents,
    chat,
    citations,
    failures,
    failure_chain,
    voice,
    reports,
    admin,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Space Mission Lessons-Learned Assistant with Grounded Citations and Failure Intelligence"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes under /api
app.include_router(auth.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(citations.router, prefix="/api")
app.include_router(failures.router, prefix="/api")
app.include_router(failure_chain.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

# Mount static directories for PDF downloads & viewer
os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(settings.GENERATED_REPORTS_DIRECTORY, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIRECTORY), name="uploads")
app.mount("/static/reports", StaticFiles(directory=settings.GENERATED_REPORTS_DIRECTORY), name="reports")

@app.on_event("startup")
def startup_event():
    logger.info("Initializing database schema on startup...")
    init_db()
    logger.info("MissionMind AI Backend ready for aerospace research queries.")

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "documentation": "/docs",
        "api_root": "/api"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "subsystems": {
            "retrieval_engine": "ACTIVE",
            "citation_verifier": "ACTIVE",
            "pdf_ingestion": "ACTIVE",
            "failure_intelligence": "ACTIVE"
        }
    }
