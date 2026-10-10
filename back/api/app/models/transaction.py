import uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.models.base import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="transactions_amount_check"),
        # the category/wallet, if provided, must belong to the same user
        ForeignKeyConstraint(
            ["user_id", "category_id"],
            ["categories.user_id", "categories.id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["user_id", "wallet_id"],
            ["wallets.user_id", "wallets.id"],
            ondelete="RESTRICT",
        ),
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
    category_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, default=None)  # pending if null (D13)
    wallet_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, default=None)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # cents, always > 0 (D14)
    note: Mapped[str | None] = mapped_column(Text, default=None)
    occurred_at: Mapped[date] = mapped_column(Date, nullable=False)

    category = relationship("Category")
    wallet = relationship("Wallet")
