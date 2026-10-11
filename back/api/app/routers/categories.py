import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.services.catalog_service import (
    create_category,
    delete_category,
    list_categories,
    update_category,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.categories import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["catalog"])


@router.get("", response_model=list[CategoryOut])
async def list_categories_endpoint(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[CategoryOut]:
    return await list_categories(db, user)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CategoryOut)
async def create_category_endpoint(
    data: CategoryCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryOut:
    return await create_category(db, user, data)


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category_endpoint(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryOut:
    return await update_category(db, user, category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_endpoint(
    category_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await delete_category(db, user, category_id)
