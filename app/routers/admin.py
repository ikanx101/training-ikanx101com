from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import os, uuid
from app.database import get_db
from app.models.user import User
from app.models.category import Category, SubCategory
from app.models.material import Material
from app.models.progress import UserProgress
from app.models.comment import Comment
from app.models.quiz import Quiz, QuizQuestion, QuizChoice, QuizAttempt, QuizAnswer
from app.models.material_file import MaterialFile
from app.models.user_access import UserSubcategoryAccess
from app.services.auth_service import get_current_user_from_cookie, get_password_hash
from app.services.material_service import extract_youtube_id
from app.services.access_service import get_allowed_sub_ids

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {
    '.csv', '.xlsx', '.xls', '.tsv', '.json', '.txt',
    '.pdf', '.docx', '.doc', '.pptx', '.ppt',
    '.zip', '.rar', '.7z',
    '.r', '.py', '.ipynb', '.rmd',
    '.png', '.jpg', '.jpeg', '.gif',
}

async def _save_files(files: List[UploadFile], mat_id: int, db: Session):
    upload_dir = os.path.join("uploads", "materials", str(mat_id))
    os.makedirs(upload_dir, exist_ok=True)
    for f in files:
        if not f.filename:
            continue
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue
        data = await f.read()
        if len(data) > MAX_FILE_SIZE:
            continue
        stored_name = uuid.uuid4().hex + ext
        path = os.path.join(upload_dir, stored_name)
        with open(path, "wb") as fp:
            fp.write(data)
        db.add(MaterialFile(
            material_id=mat_id,
            original_name=f.filename,
            stored_name=stored_name,
            file_size=len(data),
        ))

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

def _pending_count(db: Session) -> int:
    return db.query(User).filter(User.is_approved == False, User.role == "user").count()

async def get_admin(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user or user.role != "admin":
        raise HTTPException(status_code=302, headers={"Location": "/"})
    return user

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user or user.role != "admin":
        return RedirectResponse("/", status_code=302)
    total_users = db.query(User).count()
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users = db.query(User).filter(User.last_login >= week_ago).count()
    new_users = db.query(User).filter(User.created_at >= week_ago).count()
    total_materials = db.query(Material).count()
    published = db.query(Material).filter(Material.is_published == True).count()
    draft = total_materials - published
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "user": user, "total_users": total_users, "active_users": active_users, "new_users": new_users, "total_materials": total_materials, "published": published, "draft": draft, "categories": categories, "pending_count": _pending_count(db)})

@router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user or user.role != "admin":
        return RedirectResponse("/", status_code=302)
    users = db.query(User).order_by(User.created_at.desc()).all()
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("admin/users.html", {"request": request, "user": user, "users": users, "categories": categories, "pending_count": _pending_count(db)})

@router.post("/users/{user_id}/role")
async def change_role(user_id: int, role: str = Form(...), request: Request = None, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    target = db.query(User).filter(User.id == user_id).first()
    if target:
        target.role = role
        if role == "admin":
            target.is_approved = True
        db.commit()
    return RedirectResponse("/admin/users", status_code=302)

@router.post("/users/{user_id}/delete")
async def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    target = db.query(User).filter(User.id == user_id).first()
    if target and target.id != admin.id:
        db.delete(target)
        db.commit()
    return RedirectResponse("/admin/users", status_code=302)

@router.post("/users/{user_id}/approve")
async def approve_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    target = db.query(User).filter(User.id == user_id).first()
    if target:
        target.is_approved = True
        db.commit()
    return RedirectResponse("/admin/users", status_code=302)

@router.post("/users/{user_id}/reject")
async def reject_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    target = db.query(User).filter(User.id == user_id).first()
    if target and target.id != admin.id:
        db.delete(target)
        db.commit()
    return RedirectResponse("/admin/users", status_code=302)

@router.get("/categories", response_class=HTMLResponse)
async def admin_categories(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user or user.role != "admin":
        return RedirectResponse("/", status_code=302)
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("admin/categories.html", {"request": request, "user": user, "categories": categories, "pending_count": _pending_count(db)})

@router.post("/categories/add")
async def add_category(request: Request, name: str = Form(...), description: str = Form(""), icon: str = Form(""), order: int = Form(0), db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    db.add(Category(name=name, description=description or None, icon=icon or None, order=order))
    db.commit()
    return RedirectResponse("/admin/categories", status_code=302)

@router.post("/categories/{cat_id}/delete")
async def delete_category(cat_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if cat:
        db.delete(cat)
        db.commit()
    return RedirectResponse("/admin/categories", status_code=302)

@router.post("/subcategories/add")
async def add_subcategory(request: Request, name: str = Form(...), description: str = Form(""), order: int = Form(0), category_id: int = Form(...), db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    db.add(SubCategory(name=name, description=description or None, order=order, category_id=category_id))
    db.commit()
    return RedirectResponse("/admin/categories", status_code=302)

@router.post("/subcategories/{sub_id}/delete")
async def delete_subcategory(sub_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    sub = db.query(SubCategory).filter(SubCategory.id == sub_id).first()
    if sub:
        db.delete(sub)
        db.commit()
    return RedirectResponse("/admin/categories", status_code=302)

@router.get("/materials", response_class=HTMLResponse)
async def admin_materials(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user or user.role != "admin":
        return RedirectResponse("/", status_code=302)
    materials = db.query(Material).order_by(Material.id.desc()).all()
    categories = db.query(Category).order_by(Category.order).all()
    subcategories = db.query(SubCategory).all()
    return templates.TemplateResponse("admin/materials.html", {"request": request, "user": user, "materials": materials, "categories": categories, "subcategories": subcategories, "pending_count": _pending_count(db)})

@router.post("/materials/quick-category")
async def quick_add_category(request: Request, name: str = Form(...), icon: str = Form(""), db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    if name.strip():
        existing = db.query(Category).filter(Category.name == name.strip()).first()
        if not existing:
            db.add(Category(name=name.strip(), icon=icon.strip() or None, order=0))
            db.commit()
    return RedirectResponse("/admin/materials", status_code=302)

@router.post("/materials/quick-subcategory")
async def quick_add_subcategory(request: Request, name: str = Form(...), category_id: int = Form(...), db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    if name.strip():
        db.add(SubCategory(name=name.strip(), category_id=category_id, order=0))
        db.commit()
    return RedirectResponse("/admin/materials", status_code=302)

@router.post("/materials/add")
async def add_material(request: Request,
                       title: str = Form(...), description: str = Form(""),
                       youtube_url: str = Form(""), tags: str = Form(""),
                       order: int = Form(0), subcategory_id: int = Form(...),
                       publish_now: str = Form(""),
                       files: List[UploadFile] = File([]),
                       db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    embed_id = extract_youtube_id(youtube_url) if youtube_url else ""
    mat = Material(title=title, description=description or None, youtube_url=youtube_url or None,
                   youtube_embed_id=embed_id or None, tags=tags or None, order=order,
                   subcategory_id=subcategory_id, is_published=(publish_now == "on"))
    db.add(mat)
    db.flush()
    await _save_files(files, mat.id, db)
    db.commit()
    return RedirectResponse("/admin/materials", status_code=302)

@router.post("/materials/{mat_id}/files/upload")
async def upload_files(mat_id: int, request: Request,
                       files: List[UploadFile] = File(...),
                       db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    await _save_files(files, mat_id, db)
    db.commit()
    return RedirectResponse(f"/admin/materials/{mat_id}/edit", status_code=302)


@router.post("/materials/files/{file_id}/delete")
async def delete_file(file_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    mf = db.query(MaterialFile).filter(MaterialFile.id == file_id).first()
    if mf:
        mat_id = mf.material_id
        path = os.path.join("uploads", "materials", str(mat_id), mf.stored_name)
        if os.path.exists(path):
            os.remove(path)
        db.delete(mf)
        db.commit()
        return RedirectResponse(f"/admin/materials/{mat_id}/edit", status_code=302)
    return RedirectResponse("/admin/materials", status_code=302)


@router.post("/materials/{mat_id}/toggle")
async def toggle_publish(mat_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    mat = db.query(Material).filter(Material.id == mat_id).first()
    if mat:
        mat.is_published = not mat.is_published
        db.commit()
    return RedirectResponse("/admin/materials", status_code=302)

@router.post("/materials/{mat_id}/delete")
async def delete_material(mat_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    mat = db.query(Material).filter(Material.id == mat_id).first()
    if mat:
        db.delete(mat)
        db.commit()
    return RedirectResponse("/admin/materials", status_code=302)

@router.get("/materials/{mat_id}/edit", response_class=HTMLResponse)
async def edit_material_page(mat_id: int, request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user or user.role != "admin":
        return RedirectResponse("/", status_code=302)
    mat = db.query(Material).filter(Material.id == mat_id).first()
    if not mat:
        return RedirectResponse("/admin/materials", status_code=302)
    categories = db.query(Category).order_by(Category.order).all()
    subcategories = db.query(SubCategory).all()
    mat_files = db.query(MaterialFile).filter(MaterialFile.material_id == mat_id).order_by(MaterialFile.created_at).all()
    return templates.TemplateResponse("admin/edit_material.html", {
        "request": request, "user": user, "mat": mat,
        "categories": categories, "subcategories": subcategories,
        "mat_files": mat_files, "pending_count": _pending_count(db),
    })

@router.post("/materials/{mat_id}/edit")
async def edit_material(mat_id: int, request: Request, title: str = Form(...), description: str = Form(""), youtube_url: str = Form(""), tags: str = Form(""), order: int = Form(0), subcategory_id: int = Form(...), publish_now: str = Form(""), db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    mat = db.query(Material).filter(Material.id == mat_id).first()
    if mat:
        mat.title = title
        mat.description = description or None
        mat.youtube_url = youtube_url or None
        mat.youtube_embed_id = extract_youtube_id(youtube_url) if youtube_url else None
        mat.tags = tags or None
        mat.order = order
        mat.subcategory_id = subcategory_id
        mat.is_published = (publish_now == "on")
        db.commit()
    return RedirectResponse("/admin/materials", status_code=302)

# ===== KOMENTAR PRIVAT =====

@router.get("/comments", response_class=HTMLResponse)
async def admin_comments(request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    from sqlalchemy import func as sqlfunc
    # Ambil pasangan (user_id, material_id) unik
    pairs = db.query(Comment.user_id, Comment.material_id).distinct().all()
    threads = []
    for user_id, material_id in pairs:
        u = db.query(User).filter(User.id == user_id).first()
        m = db.query(Material).filter(Material.id == material_id).first()
        if not u or not m:
            continue
        total = db.query(Comment).filter_by(user_id=user_id, material_id=material_id).count()
        unread = db.query(Comment).filter_by(
            user_id=user_id, material_id=material_id,
            is_from_admin=False, is_read_by_admin=False
        ).count()
        last_msg = db.query(Comment).filter_by(
            user_id=user_id, material_id=material_id
        ).order_by(Comment.created_at.desc()).first()
        threads.append({
            "user": u, "material": m,
            "total": total, "unread": unread,
            "last_at": last_msg.created_at if last_msg else None,
            "last_msg": last_msg,
        })
    threads.sort(key=lambda x: x["unread"], reverse=True)
    categories = db.query(Category).order_by(Category.order).all()
    total_unread = sum(t["unread"] for t in threads)
    return templates.TemplateResponse("admin/comments.html", {
        "request": request, "user": admin,
        "threads": threads, "categories": categories, "total_unread": total_unread,
        "pending_count": _pending_count(db),
    })

@router.get("/comments/{user_id}/{material_id}", response_class=HTMLResponse)
async def admin_view_thread(user_id: int, material_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    student = db.query(User).filter(User.id == user_id).first()
    material = db.query(Material).filter(Material.id == material_id).first()
    if not student or not material:
        return RedirectResponse("/admin/comments", status_code=302)
    comments = db.query(Comment).filter_by(
        user_id=user_id, material_id=material_id
    ).order_by(Comment.created_at).all()
    # Tandai semua pesan user sudah dibaca admin
    db.query(Comment).filter_by(
        user_id=user_id, material_id=material_id,
        is_from_admin=False, is_read_by_admin=False
    ).update({"is_read_by_admin": True})
    db.commit()
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("admin/comment_thread.html", {
        "request": request, "user": admin,
        "student": student, "material": material,
        "comments": comments, "categories": categories,
        "pending_count": _pending_count(db),
    })

@router.post("/comments/{user_id}/{material_id}/reply")
async def admin_reply(user_id: int, material_id: int, request: Request, content: str = Form(...), db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    if content.strip():
        db.add(Comment(
            material_id=material_id,
            user_id=user_id,
            content=content.strip(),
            is_from_admin=True,
            is_read_by_user=False,
            is_read_by_admin=True,
        ))
        db.commit()
    return RedirectResponse(f"/admin/comments/{user_id}/{material_id}", status_code=302)

@router.post("/comments/{comment_id}/delete")
async def admin_delete_comment(comment_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    c = db.query(Comment).filter(Comment.id == comment_id).first()
    if c:
        uid, mid = c.user_id, c.material_id
        db.delete(c)
        db.commit()
        return RedirectResponse(f"/admin/comments/{uid}/{mid}", status_code=302)
    return RedirectResponse("/admin/comments", status_code=302)


# ===== QUIZ =====

@router.get("/materials/{mat_id}/quiz", response_class=HTMLResponse)
async def admin_quiz_page(mat_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    material = db.query(Material).filter(Material.id == mat_id).first()
    if not material:
        return RedirectResponse("/admin/materials", status_code=302)
    quiz = db.query(Quiz).filter(Quiz.material_id == mat_id).first()
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("admin/quiz.html", {
        "request": request, "user": admin,
        "material": material, "quiz": quiz, "categories": categories,
        "pending_count": _pending_count(db),
    })


@router.post("/materials/{mat_id}/quiz/setup")
async def setup_quiz(mat_id: int, request: Request,
                     passing_score: int = Form(70),
                     is_active: str = Form(""),
                     db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    quiz = db.query(Quiz).filter(Quiz.material_id == mat_id).first()
    if quiz:
        quiz.passing_score = passing_score
        quiz.is_active = (is_active == "on")
    else:
        quiz = Quiz(material_id=mat_id, passing_score=passing_score, is_active=(is_active == "on"))
        db.add(quiz)
    db.commit()
    return RedirectResponse(f"/admin/materials/{mat_id}/quiz", status_code=302)


@router.post("/materials/{mat_id}/quiz/question/add")
async def add_quiz_question(mat_id: int, request: Request,
                             question_text: str = Form(...),
                             order: int = Form(0),
                             correct_choice: int = Form(...),
                             choice_1: str = Form(...),
                             choice_2: str = Form(...),
                             choice_3: str = Form(""),
                             choice_4: str = Form(""),
                             db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    quiz = db.query(Quiz).filter(Quiz.material_id == mat_id).first()
    if not quiz:
        quiz = Quiz(material_id=mat_id, passing_score=70, is_active=True)
        db.add(quiz)
        db.flush()
    q = QuizQuestion(quiz_id=quiz.id, question_text=question_text.strip(), order=order)
    db.add(q)
    db.flush()
    choices_raw = [choice_1, choice_2, choice_3, choice_4]
    for idx, text in enumerate(choices_raw, start=1):
        if text.strip():
            db.add(QuizChoice(
                question_id=q.id,
                choice_text=text.strip(),
                is_correct=(idx == correct_choice),
            ))
    db.commit()
    return RedirectResponse(f"/admin/materials/{mat_id}/quiz", status_code=302)


@router.post("/quiz/question/{q_id}/delete")
async def delete_quiz_question(q_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    q = db.query(QuizQuestion).filter(QuizQuestion.id == q_id).first()
    if q:
        mat_id = q.quiz.material_id
        db.query(QuizAnswer).filter(QuizAnswer.question_id == q.id).delete()
        db.delete(q)
        db.commit()
        return RedirectResponse(f"/admin/materials/{mat_id}/quiz", status_code=302)
    return RedirectResponse("/admin/materials", status_code=302)


# ===== KELOLA AKSES MATERI PER USER =====

@router.get("/users/{user_id}/access", response_class=HTMLResponse)
async def admin_user_access(user_id: int, request: Request, db: Session = Depends(get_db)):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        return RedirectResponse("/admin/users", status_code=302)
    all_categories = db.query(Category).order_by(Category.order).all()
    allowed_sub_ids = get_allowed_sub_ids(target, db)
    has_restrictions = target.has_content_restrictions
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("admin/user_access.html", {
        "request": request,
        "user": admin,
        "target": target,
        "all_categories": all_categories,
        "allowed_sub_ids": allowed_sub_ids or frozenset(),
        "has_restrictions": has_restrictions,
        "categories": categories,
        "pending_count": _pending_count(db),
    })


@router.post("/users/{user_id}/access")
async def save_user_access(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    admin = await get_current_user_from_cookie(request, db)
    if not admin or admin.role != "admin":
        return RedirectResponse("/", status_code=302)
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        return RedirectResponse("/admin/users", status_code=302)

    form_data = await request.form()
    restrict_on = form_data.get("has_restrictions", "") == "on"

    # Update flag pada user
    target.has_content_restrictions = restrict_on

    # Hapus semua record akses lama
    db.query(UserSubcategoryAccess).filter(UserSubcategoryAccess.user_id == user_id).delete()

    if restrict_on:
        raw_ids = form_data.getlist("subcategory_ids")
        for raw_id in raw_ids:
            try:
                sub_id = int(raw_id)
                db.add(UserSubcategoryAccess(user_id=user_id, subcategory_id=sub_id))
            except (ValueError, Exception):
                pass

    db.commit()
    return RedirectResponse(f"/admin/users/{user_id}/access?saved=1", status_code=302)
