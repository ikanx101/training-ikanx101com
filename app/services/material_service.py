import re
from sqlalchemy.orm import Session
from app.models.material import Material

def extract_youtube_id(url: str) -> str:
    if not url:
        return ""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([\w-]{11})',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return ""

def get_published_materials(db: Session, subcategory_id: int = None):
    q = db.query(Material).filter(Material.is_published == True)
    if subcategory_id:
        q = q.filter(Material.subcategory_id == subcategory_id)
    return q.order_by(Material.order).all()

def search_materials(db: Session, query: str):
    q = db.query(Material).filter(Material.is_published == True)
    search = f"%{query}%"
    return q.filter(
        (Material.title.ilike(search)) | (Material.tags.ilike(search)) | (Material.description.ilike(search))
    ).all()
