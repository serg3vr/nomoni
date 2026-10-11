import uuid
from datetime import date

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    amount: int = Field(..., gt=0)  # cents (D14)
    note: str | None = Field(default=None, max_length=500)
    category_id: uuid.UUID | None = None
    wallet_id: uuid.UUID | None = None
    occurred_at: date | None = None


class TransactionUpdate(BaseModel):
    amount: int | None = Field(default=None, gt=0)
    note: str | None = Field(default=None, max_length=500)
    category_id: uuid.UUID | None = None
    wallet_id: uuid.UUID | None = None
    occurred_at: date | None = None


class TransactionOut(BaseModel):
    id: uuid.UUID
    amount: int
    note: str | None
    category_id: uuid.UUID | None
    wallet_id: uuid.UUID | None
    occurred_at: date
