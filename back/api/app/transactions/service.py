import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.user import User
from app.models.wallet import Wallet


async def get_own_category(
    db: AsyncSession, user: User, category_id: uuid.UUID | None
) -> Category | None:
    """Must exist, must be owned by the caller, and must be EXPENSE in the MVP."""
    if category_id is None:
        return None
    category = await db.scalar(
        select(Category).where(Category.id == category_id, Category.user_id == user.id)
    )
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    if category.type != "EXPENSE":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Only EXPENSE categories are allowed in the MVP",
        )
    return category


async def get_own_wallet(
    db: AsyncSession, user: User, wallet_id: uuid.UUID | None
) -> Wallet | None:
    if wallet_id is None:
        return None
    wallet = await db.scalar(
        select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == user.id)
    )
    if wallet is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Wallet not found")
    return wallet
