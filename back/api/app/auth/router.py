from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user, router_prefix
from app.auth.schemas import Token, UserCreate, UserOut, UserUpdate
from app.auth.service import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User

router = APIRouter(prefix=router_prefix, tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Token)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)) -> Token:
    email = data.email.lower()
    existing = await db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(
        email=email,
        password_hash=hash_password(data.password),
        name=data.name,
        currency=data.currency,
    )
    db.add(user)
    await db.commit()
    return Token(access_token=create_access_token(user.id))


@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    user = await db.scalar(select(User).where(User.email == form.username.lower().strip()))
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    update = data.model_dump(exclude_unset=True)
    if not update:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Empty update")
    for field, value in update.items():
        setattr(user, field, value)
    await db.commit()
    return user
