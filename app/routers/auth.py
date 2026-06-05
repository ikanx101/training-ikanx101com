from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.services.auth_service import (
    get_password_hash, verify_password, create_access_token,
    get_user_by_email, get_current_user_from_cookie
)
from app.config import SECURITY_QUESTIONS

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Email atau password salah"})
    user.last_login = datetime.utcnow()
    db.commit()
    token = create_access_token({"sub": user.email})
    response = RedirectResponse("/", status_code=302)
    response.set_cookie("access_token", token, httponly=True, max_age=86400*30)
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("auth/register.html", {"request": request, "error": None, "questions": SECURITY_QUESTIONS})

@router.post("/register")
async def register(
    request: Request,
    email: str = Form(...), password: str = Form(...),
    full_name: str = Form(...), bio: str = Form(""),
    security_question: str = Form(...), security_answer: str = Form(...),
    db: Session = Depends(get_db)
):
    if get_user_by_email(db, email):
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": "Email sudah terdaftar", "questions": SECURITY_QUESTIONS})
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        bio=bio or None,
        security_question=security_question,
        security_answer_hash=get_password_hash(security_answer.lower().strip()),
        role="user"
    )
    db.add(user)
    db.commit()
    token = create_access_token({"sub": user.email})
    response = RedirectResponse("/", status_code=302)
    response.set_cookie("access_token", token, httponly=True, max_age=86400*30)
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse("/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("auth/forgot_password.html", {"request": request, "step": 1, "error": None, "email": ""})

@router.post("/forgot-password")
async def forgot_password_step1(request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    if not user:
        return templates.TemplateResponse("auth/forgot_password.html", {"request": request, "step": 1, "error": "Email tidak ditemukan", "email": ""})
    return templates.TemplateResponse("auth/forgot_password.html", {"request": request, "step": 2, "error": None, "email": email, "question": user.security_question})

@router.post("/forgot-password/verify")
async def forgot_password_verify(request: Request, email: str = Form(...), security_answer: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    if not user or not verify_password(security_answer.lower().strip(), user.security_answer_hash):
        return templates.TemplateResponse("auth/forgot_password.html", {"request": request, "step": 2, "error": "Jawaban salah", "email": email, "question": user.security_question if user else ""})
    return templates.TemplateResponse("auth/forgot_password.html", {"request": request, "step": 3, "error": None, "email": email})

@router.post("/forgot-password/reset")
async def reset_password(request: Request, email: str = Form(...), security_answer: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    if not user or not verify_password(security_answer.lower().strip(), user.security_answer_hash):
        return templates.TemplateResponse("auth/forgot_password.html", {"request": request, "step": 3, "error": "Verifikasi gagal", "email": email})
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return RedirectResponse("/auth/login?reset=1", status_code=302)
