import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category, CATEGORY_TYPES
from app.models.user import User
from app.models.wallet import Wallet, WALLET_TYPES
from app.repositories import category_repository, wallet_repository
from app.schemas.categories import CategoryCreate, CategoryUpdate
from app.schemas.wallets import WalletCreate, WalletUpdate


# ---------------------------------------------------------------------------
# categories
# ---------------------------------------------------------------------------

def _assert_category_mutable(category: Category, user: User) -> None:
    if category.is_system and user.role != "SYSTEM":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "System catalog rows are read-only"
        )


def _assert_category_type_allowed(value: str, user: User) -> None:
    if value == "EXPENSE":
        return
    if value in CATEGORY_TYPES and user.role == "SYSTEM":
        return  # SYSTEM may create INCOME templates (phase 2)
    raise HTTPException(
        status.HTTP_400_BAD_REQUEST,
        "Only EXPENSE categories can be created in the MVP",
    )


async def list_categories(db: AsyncSession, user: User) -> list[Category]:
    return await category_repository.list_user(db, user.id)


async def create_category(
    db: AsyncSession, user: User, data: CategoryCreate
) -> Category:
    _assert_category_type_allowed(data.type, user)
    if await category_repository.name_exists(db, user.id, data.name):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Category name already exists"
        )
    category = Category(
        user_id=user.id,
        name=data.name,
        type=data.type,
        color=data.color,
        created_by=user.id,
        updated_by=user.id,
    )
    await category_repository.add(db, category)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Category name already exists"
        )
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession,
    user: User,
    category_id: uuid.UUID,
    data: CategoryUpdate,
) -> Category:
    category = await _get_category_or_404(db, user, category_id)
    _assert_category_mutable(category, user)

    update = data.model_dump(exclude_unset=True)
    if update.get("name") and update["name"] and await category_repository.name_exists(
        db, user.id, update["name"], category_id
    ):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Category name already exists"
        )
    for field, value in update.items():
        setattr(category, field, value)
    category.updated_by = user.id
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Category name already exists"
        )
    await db.refresh(category)
    return category


async def delete_category(
    db: AsyncSession, user: User, category_id: uuid.UUID
) -> None:
    category = await _get_category_or_404(db, user, category_id)
    _assert_category_mutable(category, user)
    try:
        await category_repository.delete(db, category)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Category has transactions and cannot be deleted",
        )


async def _get_category_or_404(
    db: AsyncSession, user: User, category_id: uuid.UUID
) -> Category:
    category = await category_repository.get(db, user.id, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    return category


# ---------------------------------------------------------------------------
# wallets
# ---------------------------------------------------------------------------

def _assert_wallet_mutable(wallet: Wallet, user: User) -> None:
    if wallet.is_system and user.role != "SYSTEM":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "System catalog rows are read-only"
        )


async def list_wallets(db: AsyncSession, user: User) -> list[Wallet]:
    return await wallet_repository.list_user(db, user.id)


async def wallet_balances(
    db: AsyncSession, user: User
) -> list[tuple[Wallet, int, int]]:
    return await wallet_repository.balances(db, user.id)


async def create_wallet(
    db: AsyncSession, user: User, data: WalletCreate
) -> Wallet:
    if data.type not in WALLET_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid wallet type")
    if await wallet_repository.name_exists(db, user.id, data.name):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Wallet name already exists"
        )
    wallet = Wallet(
        user_id=user.id,
        name=data.name,
        type=data.type,
        initial_balance=data.initial_balance,
        created_by=user.id,
        updated_by=user.id,
    )
    await wallet_repository.add(db, wallet)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Wallet name already exists"
        )
    await db.refresh(wallet)
    return wallet


async def update_wallet(
    db: AsyncSession, user: User, wallet_id: uuid.UUID, data: WalletUpdate
) -> Wallet:
    wallet = await _get_wallet_or_404(db, user, wallet_id)
    _assert_wallet_mutable(wallet, user)

    update = data.model_dump(exclude_unset=True)
    if "type" in update and update["type"] not in WALLET_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid wallet type")
    if update.get("name") and await wallet_repository.name_exists(
        db, user.id, update["name"], wallet_id
    ):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Wallet name already exists"
        )
    for field, value in update.items():
        setattr(wallet, field, value)
    wallet.updated_by = user.id
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Wallet name already exists"
        )
    await db.refresh(wallet)
    return wallet


async def delete_wallet(
    db: AsyncSession, user: User, wallet_id: uuid.UUID
) -> None:
    wallet = await _get_wallet_or_404(db, user, wallet_id)
    _assert_wallet_mutable(wallet, user)
    try:
        await wallet_repository.delete(db, wallet)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Wallet has transactions and cannot be deleted",
        )


async def _get_wallet_or_404(
    db: AsyncSession, user: User, wallet_id: uuid.UUID
) -> Wallet:
    wallet = await wallet_repository.get(db, user.id, wallet_id)
    if wallet is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Wallet not found")
    return wallet
