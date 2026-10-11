import calendar
import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction


async def list_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    year: int | None = None,
    month: int | None = None,
    category_id: uuid.UUID | None = None,
    wallet_id: uuid.UUID | None = None,
    pending: bool | None = None,
    limit: int = 500,
    offset: int = 0,
) -> list[Transaction]:
    stmt = (
        select(Transaction)
        .order_by(Transaction.occurred_at.desc(), Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    if year is not None:
        last_month = month or 12
        start = date(year, month, 1) if month else date(year, 1, 1)
        end = date(year, last_month, calendar.monthrange(year, last_month)[1])
        stmt = stmt.where(Transaction.occurred_at.between(start, end))
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
    stmt = stmt.where(Transaction.user_id == user_id)
    result = await db.scalars(stmt)
    return list(result)


async def get(db: AsyncSession, user_id: uuid.UUID, txn_id: uuid.UUID) -> Transaction | None:
    return await db.scalar(
        select(Transaction).where(
            Transaction.id == txn_id, Transaction.user_id == user_id
        )
    )


async def add(db: AsyncSession, txn: Transaction) -> None:
    db.add(txn)
    await db.flush()


async def delete(db: AsyncSession, txn: Transaction) -> None:
    await db.delete(txn)
    await db.flush()
