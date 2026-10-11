import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.models.wallet import Wallet


async def list_user(db: AsyncSession, user_id: uuid.UUID) -> list[Wallet]:
    result = await db.scalars(
        select(Wallet).where(Wallet.user_id == user_id).order_by(Wallet.created_at)
    )
    return list(result)


async def get(db: AsyncSession, user_id: uuid.UUID, wallet_id: uuid.UUID) -> Wallet | None:
    return await db.scalar(
        select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == user_id)
    )


async def name_exists(
    db: AsyncSession,
    user_id: uuid.UUID,
    name: str,
    exclude_id: uuid.UUID | None = None,
) -> bool:
    stmt = select(Wallet).where(Wallet.user_id == user_id, Wallet.name == name)
    if exclude_id is not None:
        stmt = stmt.where(Wallet.id != exclude_id)
    return (await db.scalar(stmt)) is not None


async def add(db: AsyncSession, wallet: Wallet) -> None:
    db.add(wallet)
    await db.flush()


async def delete(db: AsyncSession, wallet: Wallet) -> None:
    await db.delete(wallet)
    await db.flush()


async def balances(
    db: AsyncSession, user_id: uuid.UUID
) -> list[tuple[Wallet, int, int]]:
    """(wallet, spent_cents, balance_cents) — derived, never stored."""
    rows = await db.execute(
        select(
            Wallet,
            func.coalesce(func.sum(Transaction.amount), 0).label("spent"),
        )
        .outerjoin(Transaction, Transaction.wallet_id == Wallet.id)
        .where(Wallet.user_id == user_id)
        .group_by(Wallet.id)
        .order_by(Wallet.created_at)
    )
    return [
        (wallet, int(spent), wallet.initial_balance - int(spent))
        for wallet, spent in rows
    ]


async def list_system_templates(
    db: AsyncSession, system_user_id: uuid.UUID
) -> list[Wallet]:
    result = await db.scalars(
        select(Wallet).where(
            Wallet.user_id == system_user_id,
            Wallet.is_system.is_(True),
        )
    )
    return list(result)
