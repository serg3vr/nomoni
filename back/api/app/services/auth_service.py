import uuid

from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.category import Category
from app.models.user import User
from app.models.wallet import Wallet
from app.repositories import (
    category_repository,
    user_repository,
    wallet_repository,
)
from app.schemas.auth import Token, UserCreate, UserUpdate


async def register(db: AsyncSession, data: UserCreate) -> Token:
    """Register a user: hashed password + system catalog copies, one transaction."""
    email = data.email.lower()
    if await user_repository.get_by_email(db, email) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    user = User(
        email=email,
        password_hash=hash_password(data.password),
        name=data.name,
    )
    await user_repository.add(db, user)
    await _seed_catalog_copies(db, user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    return Token(access_token=create_access_token(user.id))


async def authenticate(db: AsyncSession, email: EmailStr, password: str) -> Token:
    user = await user_repository.get_by_email(db, str(email).lower().strip())
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is deactivated")
    return Token(access_token=create_access_token(user.id))


async def update_profile(db: AsyncSession, user: User, data: UserUpdate) -> User:
    update = data.model_dump(exclude_unset=True)
    if not update:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Empty update")
    for field, value in update.items():
        setattr(user, field, value)
    user.updated_by = user.id
    await db.commit()
    return user


async def _seed_catalog_copies(
    db: AsyncSession, new_user: User
) -> None:
    """Copy the system user's master catalog into the new user (D10)."""
    system_user = await user_repository.get_by_email(db, settings.system_user_email)
    if system_user is None:
        return

    for template in await category_repository.list_system_templates(db, system_user.id):
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

    for template in await wallet_repository.list_system_templates(db, system_user.id):
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
