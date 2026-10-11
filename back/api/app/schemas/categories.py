import uuid

from pydantic import BaseModel, Field
from app.models.category import CATEGORY_TYPES


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    type: str = "EXPENSE"
    color: str | None = Field(default=None, max_length=16)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    color: str | None = Field(default=None, max_length=16)
    hidden: bool | None = None


class CategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    color: str | None
    hidden: bool
    is_system: bool


__all__ = ["CategoryCreate", "CategoryUpdate", "CategoryOut", "CATEGORY_TYPES"]
