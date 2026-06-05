from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class MaterialFile(Base):
    __tablename__ = "material_files"
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    original_name = Column(String(500), nullable=False)
    stored_name = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    material = relationship("Material", back_populates="files")
