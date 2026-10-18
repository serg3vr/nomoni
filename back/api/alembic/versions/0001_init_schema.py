"""init schema (complete)

Revision ID: 0001
Revises:
Create Date: 2026-10-10
"""
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RUNTIME_DB_USER = os.getenv("APP_RUNTIME_DB_USER", "nomoniu")


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('currency', sa.String(length=8), server_default='MXN', nullable=False),
    sa.Column('role', sa.String(length=10), server_default='USER', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.CheckConstraint("role IN ('USER', 'ADMIN', 'SYSTEM')", name='users_role_check'),
    )
    op.create_table('categories',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('type', sa.String(length=10), server_default='EXPENSE', nullable=False),
    sa.Column('color', sa.String(length=16), nullable=True),
    sa.Column('is_system', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('hidden', sa.Boolean(), server_default='false', nullable=False),
    sa.CheckConstraint("type IN ('EXPENSE', 'INCOME')", name='categories_type_check'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'id', name='categories_user_id_uq'),
    sa.UniqueConstraint('user_id', 'name', name='categories_user_name_uq')
    )
    op.create_table('wallets',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('type', sa.String(length=12), nullable=False),
    sa.Column('initial_balance', sa.BigInteger(), nullable=False),
    sa.Column('is_system', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('hidden', sa.Boolean(), server_default='false', nullable=False),
    sa.CheckConstraint("type IN ('CASH', 'BANK', 'CREDIT_CARD', 'DIGITAL')", name='wallets_type_check'),
    sa.CheckConstraint('initial_balance >= 0', name='wallets_initial_balance_check'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'id', name='wallets_user_id_uq'),
    sa.UniqueConstraint('user_id', 'name', name='wallets_user_name_uq')
    )
    op.create_table('transactions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('category_id', sa.Uuid(), nullable=True),
    sa.Column('wallet_id', sa.Uuid(), nullable=True),
    sa.Column('amount', sa.BigInteger(), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('occurred_at', sa.Date(), nullable=False),
    sa.CheckConstraint('amount > 0', name='transactions_amount_check'),
    sa.ForeignKeyConstraint(['user_id', 'category_id'], ['categories.user_id', 'categories.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['user_id', 'wallet_id'], ['wallets.user_id', 'wallets.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    # indexes (autogenerate does not create them)
    op.execute("CREATE INDEX transactions_user_occurred_idx ON transactions (user_id, occurred_at DESC)")
    op.create_index('transactions_category_idx', 'transactions', ['category_id'])
    op.create_index('transactions_wallet_idx', 'transactions', ['wallet_id'])
    op.create_index(
        'transactions_pending_idx',
        'transactions',
        ['user_id'],
        postgresql_where=sa.text("category_id IS NULL OR wallet_id IS NULL"),
    )

    # runtime user grants (CRUD-only account)
    op.execute(f"GRANT USAGE ON SCHEMA public TO {RUNTIME_DB_USER}")
    op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON users, categories, wallets, transactions TO {RUNTIME_DB_USER}")

    # default privileges: every object the user running the migration creates
    # from now on is automatically usable by the runtime user (no need to
    # remember GRANTs). Without FOR ROLE it applies to the current role.
    op.execute(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {RUNTIME_DB_USER}"
    )
    op.execute(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f"GRANT USAGE, SELECT ON SEQUENCES TO {RUNTIME_DB_USER}"
    )


def downgrade() -> None:
    op.drop_table('transactions')
    op.drop_table('wallets')
    op.drop_table('categories')
    op.drop_table('users')
