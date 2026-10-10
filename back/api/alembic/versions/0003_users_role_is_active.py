"""users role + is_active (admin foundations)

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SYSTEM_USER_EMAIL = "system@nomoni.com"


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=10),
            nullable=False,
            server_default="USER",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.create_check_constraint(
        "users_role_check", "users", "role IN ('USER', 'ADMIN')"
    )
    op.execute(
        f"UPDATE users SET role = 'ADMIN' WHERE email = '{SYSTEM_USER_EMAIL}'"
    )


def downgrade() -> None:
    op.drop_constraint("users_role_check", "users", type_="check")
    op.drop_column("users", "is_active")
    op.drop_column("users", "role")
