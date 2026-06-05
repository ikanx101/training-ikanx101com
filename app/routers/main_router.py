from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category, SubCategory
from app.models.material import Material
from app.models.progress import UserProgress
from app.models.bookmark import Bookmark
from app.models.comment import Comment
from app.models.quiz import Quiz, QuizAttempt, QuizAnswer, QuizChoice
from app.models.material_file import MaterialFile
from app.services.auth_service import get_current_user_from_cookie
from app.services.material_service import search_materials

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    categories = db.query(Category).order_by(Category.order).all()
    if user:
        featured = db.query(Material).filter(Material.is_published == True).order_by(Material.id.desc()).limit(6).all()
        stats = {}
    else:
        featured = []
        stats = {
            "total_materials": db.query(Material).filter(Material.is_published == True).count(),
            "total_categories": db.query(Category).count(),
        }
    return templates.TemplateResponse("home.html", {"request": request, "user": user, "categories": categories, "featured": featured, "stats": stats})

@router.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = Query(""), db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)
    if not user.is_approved:
        return RedirectResponse("/auth/pending", status_code=302)
    results = search_materials(db, q) if q else []
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("search.html", {"request": request, "user": user, "results": results, "query": q, "categories": categories})

@router.get("/category/{category_id}", response_class=HTMLResponse)
async def category_page(category_id: int, request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)
    if not user.is_approved:
        return RedirectResponse("/auth/pending", status_code=302)
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return RedirectResponse("/")
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("category.html", {"request": request, "user": user, "category": category, "categories": categories})

@router.get("/subcategory/{sub_id}", response_class=HTMLResponse)
async def subcategory_page(sub_id: int, request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)
    if not user.is_approved:
        return RedirectResponse("/auth/pending", status_code=302)
    sub = db.query(SubCategory).filter(SubCategory.id == sub_id).first()
    if not sub:
        return RedirectResponse("/")
    materials = db.query(Material).filter(Material.subcategory_id == sub_id, Material.is_published == True).order_by(Material.order).all()
    progress_map = {}
    if user:
        progs = db.query(UserProgress).filter(UserProgress.user_id == user.id, UserProgress.material_id.in_([m.id for m in materials])).all()
        progress_map = {p.material_id: p for p in progs}
    total = len(materials)
    completed = sum(1 for m in materials if progress_map.get(m.id) and progress_map[m.id].is_completed)
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("subcategory.html", {"request": request, "user": user, "sub": sub, "materials": materials, "progress_map": progress_map, "total": total, "completed": completed, "categories": categories})

@router.get("/material/{material_id}", response_class=HTMLResponse)
async def material_page(material_id: int, request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)
    if not user.is_approved:
        return RedirectResponse("/auth/pending", status_code=302)
    material = db.query(Material).filter(Material.id == material_id, Material.is_published == True).first()
    if not material:
        return RedirectResponse("/")
    progress = None
    bookmarked = False
    comments = []
    if user:
        progress = db.query(UserProgress).filter_by(user_id=user.id, material_id=material_id).first()
        if not progress:
            progress = UserProgress(user_id=user.id, material_id=material_id, is_completed=False)
            db.add(progress)
            db.commit()
            db.refresh(progress)
        bm = db.query(Bookmark).filter_by(user_id=user.id, material_id=material_id).first()
        bookmarked = bm is not None
        # Ambil thread komentar privat milik user ini
        comments = db.query(Comment).filter_by(
            material_id=material_id, user_id=user.id
        ).order_by(Comment.created_at).all()
        # Tandai balasan admin sudah dibaca oleh user
        db.query(Comment).filter_by(
            material_id=material_id, user_id=user.id, is_from_admin=True, is_read_by_user=False
        ).update({"is_read_by_user": True})
        db.commit()
    related = db.query(Material).filter(Material.subcategory_id == material.subcategory_id, Material.is_published == True, Material.id != material_id).order_by(Material.order).limit(5).all()
    categories = db.query(Category).order_by(Category.order).all()
    mat_files = db.query(MaterialFile).filter(MaterialFile.material_id == material_id).order_by(MaterialFile.created_at).all()
    # Quiz
    quiz = db.query(Quiz).filter(Quiz.material_id == material_id, Quiz.is_active == True).first()
    quiz_attempt = None
    quiz_answers_map = {}
    best_attempt = None
    if quiz and user:
        attempt_id = request.query_params.get("quiz_attempt")
        if attempt_id:
            try:
                qa = db.query(QuizAttempt).filter(
                    QuizAttempt.id == int(attempt_id),
                    QuizAttempt.user_id == user.id,
                    QuizAttempt.quiz_id == quiz.id,
                ).first()
                if qa:
                    quiz_attempt = qa
                    quiz_answers_map = {ans.question_id: ans for ans in qa.answers}
            except ValueError:
                pass
        best_attempt = db.query(QuizAttempt).filter(
            QuizAttempt.user_id == user.id,
            QuizAttempt.quiz_id == quiz.id,
        ).order_by(QuizAttempt.score.desc()).first()
    return templates.TemplateResponse("material.html", {
        "request": request, "user": user, "material": material,
        "progress": progress, "bookmarked": bookmarked,
        "related": related, "categories": categories, "comments": comments,
        "mat_files": mat_files,
        "quiz": quiz, "quiz_attempt": quiz_attempt,
        "quiz_answers_map": quiz_answers_map, "best_attempt": best_attempt,
    })

@router.post("/material/{material_id}/comment")
async def post_comment(material_id: int, request: Request, content: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)
    if not user.is_approved:
        return RedirectResponse("/auth/pending", status_code=302)
    if content.strip():
        db.add(Comment(
            material_id=material_id,
            user_id=user.id,
            content=content.strip(),
            is_from_admin=False,
            is_read_by_user=True,
            is_read_by_admin=False,
        ))
        db.commit()
    return RedirectResponse(f"/material/{material_id}#komentar", status_code=302)

@router.post("/material/{material_id}/quiz")
async def submit_quiz(material_id: int, request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)
    if not user.is_approved:
        return RedirectResponse("/auth/pending", status_code=302)
    quiz = db.query(Quiz).filter(Quiz.material_id == material_id, Quiz.is_active == True).first()
    if not quiz or not quiz.questions:
        return RedirectResponse(f"/material/{material_id}", status_code=302)
    form_data = await request.form()
    questions = quiz.questions
    total = len(questions)
    correct = 0
    answers_to_save = []
    for q in questions:
        raw = form_data.get(f"q_{q.id}")
        if raw:
            try:
                choice_id = int(raw)
                choice = db.query(QuizChoice).filter(
                    QuizChoice.id == choice_id, QuizChoice.question_id == q.id
                ).first()
                if choice:
                    if choice.is_correct:
                        correct += 1
                    answers_to_save.append((q.id, choice_id, choice.is_correct))
            except ValueError:
                pass
    score = int((correct / total) * 100) if total > 0 else 0
    passed = score >= quiz.passing_score
    attempt = QuizAttempt(
        user_id=user.id, quiz_id=quiz.id,
        score=score, passed=passed,
        total_questions=total, correct_answers=correct,
    )
    db.add(attempt)
    db.flush()
    for q_id, c_id, is_correct in answers_to_save:
        db.add(QuizAnswer(attempt_id=attempt.id, question_id=q_id, choice_id=c_id, is_correct=is_correct))
    db.commit()
    return RedirectResponse(f"/material/{material_id}?quiz_attempt={attempt.id}#quiz", status_code=302)


@router.post("/material/{material_id}/complete")
async def mark_complete(material_id: int, request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)
    if not user.is_approved:
        return RedirectResponse("/auth/pending", status_code=302)
    from datetime import datetime
    progress = db.query(UserProgress).filter_by(user_id=user.id, material_id=material_id).first()
    if not progress:
        progress = UserProgress(user_id=user.id, material_id=material_id)
        db.add(progress)
    progress.is_completed = not progress.is_completed
    progress.completed_at = datetime.utcnow() if progress.is_completed else None
    db.commit()
    return RedirectResponse(f"/material/{material_id}", status_code=302)

@router.post("/material/{material_id}/bookmark")
async def toggle_bookmark(material_id: int, request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)
    if not user.is_approved:
        return RedirectResponse("/auth/pending", status_code=302)
    bm = db.query(Bookmark).filter_by(user_id=user.id, material_id=material_id).first()
    if bm:
        db.delete(bm)
    else:
        db.add(Bookmark(user_id=user.id, material_id=material_id))
    db.commit()
    return RedirectResponse(f"/material/{material_id}", status_code=302)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)
    if not user.is_approved:
        return RedirectResponse("/auth/pending", status_code=302)
    bookmarks = db.query(Bookmark).filter_by(user_id=user.id).order_by(Bookmark.created_at.desc()).all()
    recent = db.query(UserProgress).filter_by(user_id=user.id).order_by(UserProgress.last_watched.desc()).limit(10).all()
    completed_count = db.query(UserProgress).filter_by(user_id=user.id, is_completed=True).count()
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "bookmarks": bookmarks, "recent": recent, "completed_count": completed_count, "categories": categories})

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)
    if not user.is_approved:
        return RedirectResponse("/auth/pending", status_code=302)
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "categories": categories, "success": None, "error": None})

@router.post("/profile")
async def update_profile(request: Request, full_name: str = Form(...), bio: str = Form(""), db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=302)
    if not user.is_approved:
        return RedirectResponse("/auth/pending", status_code=302)
    user.full_name = full_name
    user.bio = bio or None
    db.commit()
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "categories": categories, "success": "Profil berhasil diperbarui", "error": None})
