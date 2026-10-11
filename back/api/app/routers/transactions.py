import uuid
from typing import Annotated, List, Optional

import calendar
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.services.transactions_service import (
    create_transaction,
    delete_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.transactions import (
    TransactionCreate,
    TransactionOut,
    TransactionUpdate,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
async def list_transactions_endpoint(
    year: Optional[int] = None,
    month: Optional[int] = None,
    category_id: Optional[uuid.UUID] = None,
    wallet_id: Optional[uuid.UUID] = None,
    pending: Optional[bool] = None,
    limit: int = Query(default=500, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> list[TransactionOut]:
    return await list_transactions(
        db,
        user,
        year=year,
        month=month,
        category_id=category_id,
        wallet_id=wallet_id,
        pending=pending,
        limit=limit,
        offset=offset,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TransactionOut)
async def create_transaction_endpoint(
    data: TransactionCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionOut:
    return await create_transaction(db, user, data)


@router.get("/{txn_id}", response_model=TransactionOut)
async def get_transaction_endpoint(
    txn_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionOut:
    return await get_transaction(db, user, txn_id)


@router.patch("/{txn_id}", response_model=TransactionOut)
async def update_transaction_endpoint(
    txn_id: uuid.UUID,
    data: TransactionUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TransactionOut:
    return await update_transaction(db, user, txn_id, data)


@router.delete("/{txn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction_endpoint(
    txn_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await delete_transaction(db, user, txn_id)
