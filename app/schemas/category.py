from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    order: int = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class SubCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    order: int = 0
    category_id: int

class SubCategoryCreate(SubCategoryBase):
    pass

class SubCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None

class SubCategoryResponse(SubCategoryBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    subcategories: List[SubCategoryResponse] = []
    class Config:
        from_attributes = True
