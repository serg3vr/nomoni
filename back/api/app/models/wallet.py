import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from app.models.base import Base

WALLET_TYPES: tuple[str, ...] = ("CASH", "BANK", "CREDIT_CARD", "DIGITAL")


class Wallet(Base):
    __tablename__ = "wallets"
    __table_args__ = (
        CheckConstraint(
            "type IN ('CASH', 'BANK', 'CREDIT_CARD', 'DIGITAL')",
            name="wallets_type_check",
        ),
        CheckConstraint("initial_balance >= 0", name="wallets_initial_balance_check"),
        UniqueConstraint("user_id", "name", name="wallets_user_name_uq"),
        UniqueConstraint("user_id", "id", name="wallets_user_id_uq"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120))
    type: Mapped[str] = mapped_column(String(12), nullable=False)
    initial_balance: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
