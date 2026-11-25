# MISSIONMIND AI – Development & Quick Start Guide

## Prerequisites
- Python 3.10+
- Node.js 18+ (Node 24 supported)
- PostgreSQL with pgvector (or fallback SQLite engine)

## Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env as required
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Seed Ingestion
To populate the database with official NASA and ISRO mission investigation reports:
```bash
python scripts/seed_data.py
```

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Running Verification Tests
```bash
pytest backend/tests -v
```
