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
    _seed_admin()

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
                security_question="Apa nama hewan peliharaan pertama kamu?",
                security_answer_hash=get_password_hash("kucing"),
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()
