from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class MaterialBase(BaseModel):
    title: str
    description: Optional[str] = None
    youtube_url: Optional[str] = None
    tags: Optional[str] = None
    order: int = 0
    subcategory_id: int

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    youtube_url: Optional[str] = None
    tags: Optional[str] = None
    order: Optional[int] = None
    is_published: Optional[bool] = None
    subcategory_id: Optional[int] = None

class MaterialResponse(MaterialBase):
    id: int
    youtube_embed_id: Optional[str] = None
    resources: Optional[Any] = None
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True
