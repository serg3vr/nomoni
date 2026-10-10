import calendar
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.transactions.service import get_own_category, get_own_wallet

router = APIRouter(prefix="/transactions", tags=["transactions"])


class TransactionCreate(BaseModel):
    amount: int = Field(..., gt=0)  # cents (D14)
    note: str | None = Field(default=None, max_length=500)
    category_id: uuid.UUID | None = None
    wallet_id: uuid.UUID | None = None
    occurred_at: date | None = None


class TransactionUpdate(BaseModel):
    amount: int | None = Field(default=None, gt=0)
    note: str | None = Field(default=None, max_length=500)
    category_id: uuid.UUID | None = None
    wallet_id: uuid.UUID | None = None
    occurred_at: date | None = None


class TransactionOut(BaseModel):
    id: uuid.UUID
    amount: int
    note: str | None
    category_id: uuid.UUID | None
    wallet_id: uuid.UUID | None
    occurred_at: date


def _month_range(year: int, month: int | None) -> tuple[date, date]:
    last_month = month or 12
    last_day = calendar.monthrange(year, last_month)[1]
    start = date(year, month, 1) if month else date(year, 1, 1)
    end = date(year, last_month, last_day)
    return start, end


async def _fetch_own(
    db: AsyncSession, user: User, txn_id: uuid.UUID
) -> Transaction:
    txn = await db.scalar(
        select(Transaction).where(
            Transaction.id == txn_id, Transaction.user_id == user.id
        )
    )
    if txn is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaction not found")
    return txn


@router.get("", response_model=list[TransactionOut])
async def list_transactions(
    year: int | None = None,
    month: int | None = None,
    category_id: uuid.UUID | None = None,
    wallet_id: uuid.UUID | None = None,
    pending: bool | None = None,
    limit: int = Query(default=500, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Transaction]:
    stmt = (
        select(Transaction)
        .order_by(Transaction.occurred_at.desc(), Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    if year is not None:
        start, end = _month_range(year, month)
        stmt = stmt.where(Transaction.occurred_at.between(start, end))
    if month is not None and year is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "year is required when month is given"
        )
    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    if wallet_id is not None:
        stmt = stmt.where(Transaction.wallet_id == wallet_id)
    if pending is True:
        stmt = stmt.where(
            (Transaction.category_id == None)  # noqa: E711
            | (Transaction.wallet_id == None)  # noqa: E711
        )
    if pending is False:
        stmt = stmt.where(
            Transaction.category_id != None,  # noqa: E711
            Transaction.wallet_id != None,  # noqa: E711
        )

    stmt = stmt.where(Transaction.user_id == user.id)
    result = await db.scalars(stmt)
    return list(result)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TransactionOut)
async def create_transaction(
    data: TransactionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Transaction:
    await get_own_category(db, user, data.category_id)
    await get_own_wallet(db, user, data.wallet_id)

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
    db.add(txn)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category or wallet reference",
        )
    await db.refresh(txn)
    return txn


@router.get("/{txn_id}", response_model=TransactionOut)
async def get_transaction(
    txn_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Transaction:
    return await _fetch_own(db, user, txn_id)


@router.patch("/{txn_id}", response_model=TransactionOut)
async def update_transaction(
    txn_id: uuid.UUID,
    data: TransactionUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Transaction:
    txn = await _fetch_own(db, user, txn_id)

    update = data.model_dump(exclude_unset=True)
    if "category_id" in update:
        await get_own_category(db, user, update["category_id"])
    if "wallet_id" in update:
        await get_own_wallet(db, user, update["wallet_id"])

    for field, value in update.items():
        setattr(txn, field, value)
    txn.updated_by = user.id
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category or wallet reference",
        )
    await db.refresh(txn)
    return txn


@router.delete("/{txn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    txn_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    txn = await _fetch_own(db, user, txn_id)
    await db.delete(txn)
    await db.commit()
