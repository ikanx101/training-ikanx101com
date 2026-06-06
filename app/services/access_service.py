from typing import Optional, FrozenSet
from sqlalchemy.orm import Session
from app.models.user_access import UserSubcategoryAccess


def get_allowed_sub_ids(user, db: Session) -> Optional[FrozenSet[int]]:
    """
    Returns None if user has no content restrictions (sees everything).
    Returns a frozenset (possibly empty) of allowed subcategory IDs if restricted.
    Empty frozenset means user is blocked from all content.
    """
    if not getattr(user, "has_content_restrictions", False):
        return None
    records = db.query(UserSubcategoryAccess.subcategory_id).filter(
        UserSubcategoryAccess.user_id == user.id
    ).all()
    return frozenset(r.subcategory_id for r in records)


def filter_categories(categories: list, allowed_sub_ids: Optional[FrozenSet[int]]) -> list:
    """Return only categories that have at least one visible subcategory."""
    if allowed_sub_ids is None:
        return categories
    return [c for c in categories if any(s.id in allowed_sub_ids for s in c.subcategories)]


def user_can_access_subcategory(user, sub_id: int, db: Session) -> bool:
    """True if user is admin, has no restrictions, or sub_id is in allowed set."""
    if user.role == "admin":
        return True
    allowed = get_allowed_sub_ids(user, db)
    return allowed is None or sub_id in allowed
