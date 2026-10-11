import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(User.email == email))


async def add(db: AsyncSession, user: User) -> None:
    """Adds to the session (no commit — the service owns the transaction)."""
    db.add(user)
    await db.flush()
