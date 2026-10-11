import uuid

from pydantic import BaseModel, Field, field_validator
from app.models.wallet import WALLET_TYPES


class WalletCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    type: str
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
