import calendar
import uuid
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.models.wallet import Wallet
from app.repositories import (
    category_repository,
    transaction_repository,
    wallet_repository,
)
from app.schemas.transactions import TransactionCreate, TransactionUpdate


async def list_transactions(
    db: AsyncSession,
    user: User,
    year: int | None = None,
    month: int | None = None,
    category_id: uuid.UUID | None = None,
    wallet_id: uuid.UUID | None = None,
    pending: bool | None = None,
    limit: int = 500,
    offset: int = 0,
) -> list[Transaction]:
    if month is not None and year is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "year is required when month is given"
        )
    return await transaction_repository.list_user(
        db,
        user.id,
        year=year,
        month=month,
        category_id=category_id,
        wallet_id=wallet_id,
        pending=pending,
        limit=limit,
        offset=offset,
    )


async def get_transaction(
    db: AsyncSession, user: User, txn_id: uuid.UUID
) -> Transaction:
    txn = await transaction_repository.get(db, user.id, txn_id)
    if txn is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaction not found")
    return txn


async def create_transaction(
    db: AsyncSession, user: User, data: TransactionCreate
) -> Transaction:
    await _validate_refs(db, user, data.category_id, data.wallet_id)
    txn = Transaction(
        user_id=user.id,
        category_id=data.category_id,
        wallet_id=data.wallet_id,
        amount=data.amount,
        note=data.note,
        occurred_at=data.occurred_at or date.today(),
        created_by=user.id,
        updated_by=user.id,
    )
    await transaction_repository.add(db, txn)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Invalid category or wallet reference"
        )
    await db.refresh(txn)
    return txn


async def update_transaction(
    db: AsyncSession,
    user: User,
    txn_id: uuid.UUID,
    data: TransactionUpdate,
) -> Transaction:
    txn = await get_transaction(db, user, txn_id)
    update = data.model_dump(exclude_unset=True)
    if "category_id" in update or "wallet_id" in update:
        await _validate_refs(
            db,
            user,
            update.get("category_id", txn.category_id),
            update.get("wallet_id", txn.wallet_id),
        )
    for field, value in update.items():
        setattr(txn, field, value)
    txn.updated_by = user.id
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Invalid category or wallet reference"
        )
    await db.refresh(txn)
    return txn


async def delete_transaction(
    db: AsyncSession, user: User, txn_id: uuid.UUID
) -> None:
    txn = await get_transaction(db, user, txn_id)
    await transaction_repository.delete(db, txn)
    await db.commit()


async def _validate_refs(
    db: AsyncSession,
    user: User,
    category_id: uuid.UUID | None,
    wallet_id: uuid.UUID | None,
) -> None:
    if category_id is not None:
        category: Category | None = await category_repository.get(
            db, user.id, category_id
        )
        if category is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
        if category.type != "EXPENSE":
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Only EXPENSE categories are allowed in the MVP",
            )
    if wallet_id is not None:
        wallet: Wallet | None = await wallet_repository.get(
            db, user.id, wallet_id
        )
        if wallet is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Wallet not found")
