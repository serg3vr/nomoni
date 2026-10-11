import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.services.catalog_service import (
    create_wallet,
    delete_wallet,
    list_wallets,
    update_wallet,
    wallet_balances,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.wallets import (
    WalletBalanceOut,
    WalletCreate,
    WalletOut,
    WalletUpdate,
)

router = APIRouter(prefix="/wallets", tags=["catalog"])


@router.get("/balances", response_model=list[WalletBalanceOut])
async def wallet_balances_endpoint(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[WalletBalanceOut]:
    return [
        WalletBalanceOut(
            id=wallet.id,
            name=wallet.name,
            type=wallet.type,
            initial_balance=wallet.initial_balance,
            spent=spent,
            balance=balance,
        )
        for wallet, spent, balance in await wallet_balances(db, user)
    ]


@router.get("", response_model=list[WalletOut])
async def list_wallets_endpoint(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[WalletOut]:
    return await list_wallets(db, user)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=WalletOut)
async def create_wallet_endpoint(
    data: WalletCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WalletOut:
    return await create_wallet(db, user, data)


@router.patch("/{wallet_id}", response_model=WalletOut)
async def update_wallet_endpoint(
    wallet_id: uuid.UUID,
    data: WalletUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WalletOut:
    return await update_wallet(db, user, wallet_id, data)


@router.delete("/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wallet_endpoint(
    wallet_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await delete_wallet(db, user, wallet_id)
