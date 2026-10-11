import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


async def list_user(db: AsyncSession, user_id: uuid.UUID) -> list[Category]:
    result = await db.scalars(
        select(Category)
        .where(Category.user_id == user_id)
        .order_by(Category.is_system.desc(), Category.name)
    )
    return list(result)


async def get(db: AsyncSession, user_id: uuid.UUID, category_id: uuid.UUID) -> Category | None:
    return await db.scalar(
        select(Category).where(
            Category.id == category_id, Category.user_id == user_id
        )
    )


async def name_exists(
    db: AsyncSession,
    user_id: uuid.UUID,
    name: str,
    exclude_id: uuid.UUID | None = None,
) -> bool:
    stmt = select(Category).where(
        Category.user_id == user_id, Category.name == name
    )
    if exclude_id is not None:
        stmt = stmt.where(Category.id != exclude_id)
    return (await db.scalar(stmt)) is not None


async def add(db: AsyncSession, category: Category) -> None:
    db.add(category)
    await db.flush()


async def delete(db: AsyncSession, category: Category) -> None:
    await db.delete(category)
    await db.flush()


async def list_system_templates(
    db: AsyncSession, system_user_id: uuid.UUID
) -> list[Category]:
    result = await db.scalars(
        select(Category).where(
            Category.user_id == system_user_id,
            Category.is_system.is_(True),
        )
    )
    return list(result)


async def get_by_type(
    db: AsyncSession, user_id: uuid.UUID, category_id: uuid.UUID
) -> Category | None:
    return await db.scalar(
        select(Category).where(
            Category.id == category_id, Category.user_id == user_id
        )
    )
