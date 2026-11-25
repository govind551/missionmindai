import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.database.connection import SessionLocal, init_db
from app.models.user import User
from app.core.security import get_password_hash
from app.core.logging import logger

def create_admin():
    init_db()
    db = SessionLocal()
    try:
        admin_email = "admin@missionmind.ai"
        existing = db.query(User).filter(User.email == admin_email).first()
        if not existing:
            admin = User(
                name="Flight Director / Mission Admin",
                email=admin_email,
                password_hash=get_password_hash("Aerospace@2026"),
                role="admin"
            )
            db.add(admin)
            
            # Also create standard researcher account for testing
            researcher = User(
                name="Dr. Vikram Sarabhai",
                email="researcher@missionmind.ai",
                password_hash=get_password_hash("Aerospace@2026"),
                role="analyst"
            )
            db.add(researcher)
            db.commit()
            logger.info("Admin and researcher test accounts created successfully.")
            print("[SUCCESS] Created accounts:")
            print("  Admin:      admin@missionmind.ai / Aerospace@2026")
            print("  Researcher: researcher@missionmind.ai / Aerospace@2026")
        else:
            print("[INFO] Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
