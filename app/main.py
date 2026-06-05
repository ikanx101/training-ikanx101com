import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import create_tables
from app.models import user, category, material, progress, bookmark
from app.routers import auth, main_router, admin

app = FastAPI(title="Study Data with ikanx101.com", version="1.0.0")

os.makedirs("uploads/materials", exist_ok=True)
os.makedirs("app/static/img", exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(main_router.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup():
    create_tables()
    _migrate_db()
    _seed_admin()

def _migrate_db():
    from sqlalchemy import text
    from app.database import engine
    from app.config import DATABASE_URL
    with engine.connect() as conn:
        try:
            if DATABASE_URL.startswith("sqlite"):
                conn.execute(text("ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT 0"))
            else:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT FALSE"))
            conn.commit()
            # Semua user yang sudah ada sebelumnya langsung di-approve (backward compat)
            conn.execute(text("UPDATE users SET is_approved = TRUE"))
            conn.commit()
        except Exception:
            pass  # Column sudah ada, tidak perlu migrasi

def _seed_admin():
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth_service import get_password_hash
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@ikanx101.com").first()
        if not existing:
            admin_user = User(
                email="admin@ikanx101.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Ikang Fadhli",
                bio="Admin Study Data with ikanx101.com",
                role="admin",
                is_approved=True,
                security_question="Apa nama hewan peliharaan pertama kamu?",
                security_answer_hash=get_password_hash("kucing"),
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()
