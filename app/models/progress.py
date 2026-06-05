from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class UserProgress(Base):
    __tablename__ = "user_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    last_watched = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "material_id", name="uq_user_material"),)

    user = relationship("User", back_populates="progresses")
    material = relationship("Material", back_populates="progresses")
