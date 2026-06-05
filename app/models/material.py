from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    youtube_url = Column(String(500), nullable=True)
    youtube_embed_id = Column(String(100), nullable=True)
    tags = Column(String(500), nullable=True)
    resources = Column(JSON, nullable=True)
    order = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    subcategory = relationship("SubCategory", back_populates="materials")
    progresses = relationship("UserProgress", back_populates="material", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="material", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="material", cascade="all, delete-orphan")
    quiz = relationship("Quiz", back_populates="material", uselist=False, cascade="all, delete-orphan")
    files = relationship("MaterialFile", back_populates="material", cascade="all, delete-orphan",
                         order_by="MaterialFile.created_at")
