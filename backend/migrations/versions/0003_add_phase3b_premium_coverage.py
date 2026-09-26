"""Add Phase 3B policy lifecycle fields

Adds premium_amount_paise and coverage_amount_paise columns to policies table.
These support the policy purchase lifecycle where premium is what the user pays
and coverage is what the user receives on a trigger event.

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-26

COORDINATION NOTE:
  Phase 3B: Policy & Premium Lifecycle model changes.
  Akshaya must review and apply to shared PostgreSQL/Supabase instance.
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    columns = [col['name'] for col in inspector.get_columns('policies')]

    if "premium_amount_paise" not in columns:
        op.add_column(
            "policies",
            sa.Column("premium_amount_paise", sa.BigInteger(), nullable=True),
        )

    if "coverage_amount_paise" not in columns:
        op.add_column(
            "policies",
            sa.Column("coverage_amount_paise", sa.BigInteger(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("policies", "coverage_amount_paise")
    op.drop_column("policies", "premium_amount_paise")
