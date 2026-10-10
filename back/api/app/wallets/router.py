import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.models.wallet import WALLET_TYPES, Wallet

router = APIRouter(prefix="/wallets", tags=["catalog"])


class WalletCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    type: str = Field(json_schema_extra={"enum": WALLET_TYPES})
    initial_balance: int = Field(default=0, ge=0)  # cents (D14)

    @field_validator("type")
    @classmethod
    def type_valid(cls, v: str) -> str:
        if v not in WALLET_TYPES:
            raise ValueError(f"type must be one of {WALLET_TYPES}")
        return v


class WalletUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    type: str | None = None
    initial_balance: int | None = Field(default=None, ge=0)
    hidden: bool | None = None

    @field_validator("type")
    @classmethod
    def type_valid(cls, v: str | None) -> str | None:
        if v is not None and v not in WALLET_TYPES:
            raise ValueError(f"type must be one of {WALLET_TYPES}")
        return v


class WalletOut(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    initial_balance: int
    hidden: bool
    is_system: bool


class WalletBalanceOut(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    initial_balance: int
    spent: int
    balance: int


def _assert_mutable(wallet: Wallet, user: User) -> None:
    if wallet.is_system and user.role != "SYSTEM":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System catalog rows are read-only",
        )


@router.get("/balances", response_model=list[WalletBalanceOut])
async def wallet_balances(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[WalletBalanceOut]:
    rows = await db.execute(
        select(
            Wallet,
            func.coalesce(func.sum(Transaction.amount), 0).label("spent"),
        )
        .outerjoin(Transaction, Transaction.wallet_id == Wallet.id)
        .where(Wallet.user_id == user.id)
        .group_by(Wallet.id)
        .order_by(Wallet.created_at)
    )
    result: list[WalletBalanceOut] = []
    for wallet, spent in rows:
        result.append(
            WalletBalanceOut(
                id=wallet.id,
                name=wallet.name,
                type=wallet.type,
                initial_balance=wallet.initial_balance,
                spent=spent,
                balance=wallet.initial_balance - spent,
            )
        )
    return result


@router.get("", response_model=list[WalletOut])
async def list_wallets(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Wallet]:
    result = await db.scalars(
        select(Wallet)
        .where(Wallet.user_id == user.id)
        .order_by(Wallet.created_at)
    )
    return list(result)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=WalletOut)
async def create_wallet(
    data: WalletCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Wallet:
    existing = await db.scalar(
        select(Wallet).where(Wallet.user_id == user.id, Wallet.name == data.name)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wallet name already exists",
        )
    wallet = Wallet(
        user_id=user.id,
        name=data.name,
        type=data.type,
        initial_balance=data.initial_balance,
        created_by=user.id,
        updated_by=user.id,
    )
    db.add(wallet)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wallet name already exists",
        )
    await db.refresh(wallet)
    return wallet


@router.patch("/{wallet_id}", response_model=WalletOut)
async def update_wallet(
    wallet_id: uuid.UUID,
    data: WalletUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Wallet:
    wallet = await db.scalar(
        select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == user.id)
    )
    if wallet is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Wallet not found")

    _assert_mutable(wallet, user)

    update = data.model_dump(exclude_unset=True)
    if update.get("name"):
        conflict = await db.scalar(
            select(Wallet).where(
                Wallet.user_id == user.id,
                Wallet.name == update["name"],
                Wallet.id != wallet_id,
            )
        )
        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Wallet name already exists",
            )
    for field, value in update.items():
        setattr(wallet, field, value)
    wallet.updated_by = user.id
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wallet name already exists",
        )
    await db.refresh(wallet)
    return wallet


@router.delete("/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wallet(
    wallet_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    wallet = await db.scalar(
        select(Wallet).where(Wallet.id == wallet_id, Wallet.user_id == user.id)
    )
    if wallet is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Wallet not found")

    _assert_mutable(wallet, user)

    await db.delete(wallet)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Wallet has transactions and cannot be deleted",
        )
