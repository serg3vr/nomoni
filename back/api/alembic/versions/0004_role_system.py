"""role SYSTEM + read-only system rows

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SYSTEM_USER_EMAIL = "system@nomoni.com"


def upgrade() -> None:
    op.drop_constraint("users_role_check", "users", type_="check")
    op.create_check_constraint(
        "users_role_check",
        "users",
        "role IN ('USER', 'ADMIN', 'SYSTEM')",
    )
    op.execute(f"UPDATE users SET role = 'SYSTEM' WHERE email = '{SYSTEM_USER_EMAIL}'")


def downgrade() -> None:
    op.execute(f"UPDATE users SET role = 'ADMIN' WHERE email = '{SYSTEM_USER_EMAIL}'")
    op.drop_constraint("users_role_check", "users", type_="check")
    op.create_check_constraint(
        "users_role_check",
        "users",
        "role IN ('USER', 'ADMIN')",
    )
