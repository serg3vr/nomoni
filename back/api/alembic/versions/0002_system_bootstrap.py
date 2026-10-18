"""system user bootstrap + master catalog seed

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-10
"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from uuid6 import uuid7

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SYSTEM_USER_EMAIL = "system@nomoni.com"
SYSTEM_USER_PASSWORD = "12345678"  # dev bootstrap credential: rotate on real deployments

SYSTEM_CATEGORIES = ("Comida", "Transporte", "Hogar", "Ocio", "Salud", "Otros")
SYSTEM_WALLETS = (
    ("Efectivo", "CASH"),
    ("PayPal", "DIGITAL"),
    ("Tarjeta de crédito", "CREDIT_CARD"),
)


def _hash(raw: str) -> str:
    import bcrypt

    return bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()
TEST_USER_EMAIL = "sergio@hotmail.com"


def upgrade() -> None:
    system_id = uuid.uuid4()
    op.execute(
        sa.text(
            """
            insert into users (id, email, password_hash, name, currency, role, created_by, updated_by)
            values (:id, :email, :password_hash, 'System', 'MXN', 'SYSTEM', :id, :id)
            """
        ).bindparams(
            id=system_id,
            email=SYSTEM_USER_EMAIL,
            password_hash=_hash(SYSTEM_USER_PASSWORD),
        )
    )

    for name in SYSTEM_CATEGORIES:
        op.execute(
            sa.text(
                """
                insert into categories (id, created_by, updated_by, user_id, name, type, is_system)
                values (:id, :uid, :uid, :uid, :name, 'EXPENSE', true)
                """
            ).bindparams(id=uuid7(), uid=system_id, name=name)
        )

    for name, wallet_type in SYSTEM_WALLETS:
        op.execute(
            sa.text(
                """
                insert into wallets (id, created_by, updated_by, user_id, name, type, initial_balance, is_system)
                values (:id, :uid, :uid, :uid, :name, :wtype, 0, true)
                """
            ).bindparams(id=uuid7(), uid=system_id, name=name, wtype=wallet_type)
        )

    # test user: regular USER with his own catalog copies (same shape the
    # register endpoint creates), ready to transact out of the box
    tester_id = uuid.uuid4()
    op.execute(
        sa.text(
            """
            insert into users (id, email, password_hash, name, currency, role, created_by, updated_by)
            values (:id, :email, :password_hash, 'Sergio', 'MXN', 'USER', :sid, :sid)
            """
        ).bindparams(
            id=tester_id,
            sid=system_id,
            email=TEST_USER_EMAIL,
            password_hash=_hash(SYSTEM_USER_PASSWORD),
        )
    )

    for name in SYSTEM_CATEGORIES:
        op.execute(
            sa.text(
                """
                insert into categories (id, created_by, updated_by, user_id, name, type, is_system)
                values (:id, :sid, :sid, :uid, :name, 'EXPENSE', true)
                """
            ).bindparams(id=uuid7(), sid=system_id, uid=tester_id, name=name)
        )

    for name, wallet_type in SYSTEM_WALLETS:
        op.execute(
            sa.text(
                """
                insert into wallets (id, created_by, updated_by, user_id, name, type, initial_balance, is_system)
                values (:id, :sid, :sid, :uid, :name, :wtype, 0, true)
                """
            ).bindparams(id=uuid7(), sid=system_id, uid=tester_id, name=name, wtype=wallet_type)


        )


def downgrade() -> None:
    op.execute(
        "delete from users where email in ('system@nomoni.com', 'sergio@hotmail.com')"
    )

