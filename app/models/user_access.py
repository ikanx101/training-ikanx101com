from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.database import Base

class UserSubcategoryAccess(Base):
    __tablename__ = "user_subcategory_access"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id", ondelete="CASCADE"), nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "subcategory_id", name="uq_user_subcat"),)
