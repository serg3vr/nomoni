import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.category import Category
from app.models.user import User
from app.models.wallet import Wallet


async def add_user_defaults(db: AsyncSession, new_user: User) -> None:
    """Copy the system master catalog (owned by the system user) into the new user's rows."""
    system_user = await db.scalar(select(User).where(User.email == settings.system_user_email))
    if system_user is None:
        return

    templates = await db.scalars(
        select(Category).where(
            Category.user_id == system_user.id,
            Category.is_system.is_(True),
        )
    )
    for template in templates:
        db.add(
            Category(
                user_id=new_user.id,
                name=template.name,
                type=template.type,
                color=template.color,
                is_system=True,
                created_by=template.created_by,
            )
        )

    templates = await db.scalars(
        select(Wallet).where(
            Wallet.user_id == system_user.id,
            Wallet.is_system.is_(True),
        )
    )
    for template in templates:
        db.add(
            Wallet(
                user_id=new_user.id,
                name=template.name,
                type=template.type,
                initial_balance=template.initial_balance,
                is_system=True,
                created_by=template.created_by,
            )
        )
