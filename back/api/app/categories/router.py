import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.db.session import get_db
from app.models.category import CATEGORY_TYPES, Category
from app.models.user import User

router = APIRouter(prefix="/categories", tags=["catalog"])


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


def _assert_mutable(category: Category, user: User) -> None:
    if category.is_system and user.role != "SYSTEM":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System catalog rows are read-only",
        )


def _check_type(value: str | None, user: User) -> str:
    if value == "EXPENSE":
        return value
    if value in CATEGORY_TYPES and user.role == "SYSTEM":
        return value  # SYSTEM may create INCOME templates (phase 2)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Only EXPENSE categories can be created in the MVP",
    )


@router.get("", response_model=list[CategoryOut])
async def list_categories(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Category]:
    result = await db.scalars(
        select(Category)
        .where(Category.user_id == user.id)
        .order_by(Category.is_system.desc(), Category.name)
    )
    return list(result)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CategoryOut)
async def create_category(
    data: CategoryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Category:
    category_type = _check_type(data.type, user)
    existing = await db.scalar(
        select(Category).where(
            Category.user_id == user.id, Category.name == data.name
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already exists",
        )
    category = Category(
        user_id=user.id,
        name=data.name,
        type=category_type,
        color=data.color,
        created_by=user.id,
        updated_by=user.id,
    )
    db.add(category)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already exists",
        )
    await db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Category:
    category = await db.scalar(
        select(Category).where(
            Category.id == category_id, Category.user_id == user.id
        )
    )
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")

    _assert_mutable(category, user)

    update = data.model_dump(exclude_unset=True)
    if update.get("name"):
        conflict = await db.scalar(
            select(Category).where(
                Category.user_id == user.id,
                Category.name == update["name"],
                Category.id != category_id,
            )
        )
        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category name already exists",
            )
    for field, value in update.items():
        setattr(category, field, value)
    category.updated_by = user.id
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already exists",
        )
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    category = await db.scalar(
        select(Category).where(
            Category.id == category_id, Category.user_id == user.id
        )
    )
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")

    _assert_mutable(category, user)

    await db.delete(category)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category has transactions and cannot be deleted",
        )
