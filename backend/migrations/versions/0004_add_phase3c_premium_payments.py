"""Add Phase 3C premium_payments table

Creates the premium_payments table for Razorpay TEST payment tracking.
Completely separate from the insurance payout/wallet_transactions subsystem.

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-26

COORDINATION NOTE:
  Phase 3C: Razorpay TEST payment integration.
  Akshaya must review and apply to shared PostgreSQL/Supabase instance.
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if "premium_payments" not in inspector.get_table_names():
        op.create_table(
            "premium_payments",
            sa.Column("id", sa.Uuid(), primary_key=True),
            sa.Column("policy_id", sa.Uuid(), sa.ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("policyholder_id", sa.Uuid(), sa.ForeignKey("policyholders.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("amount_paise", sa.BigInteger(), nullable=False),
            sa.Column("currency", sa.Text(), server_default="INR", nullable=False),
            sa.Column("provider", sa.Text(), server_default="razorpay", nullable=False),
            sa.Column("provider_order_id", sa.Text(), nullable=True),
            sa.Column("provider_payment_id", sa.Text(), nullable=True),
            sa.Column("provider_signature", sa.Text(), nullable=True),
            sa.Column("status", sa.Text(), server_default="CREATED", nullable=False),
            sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("provider_order_id", name="uq_premium_payments_provider_order_id"),
            sa.UniqueConstraint("provider_payment_id", name="uq_premium_payments_provider_payment_id"),
        )

        # Index for looking up payments by policy
        op.create_index(
            "ix_premium_payments_policy_id",
            "premium_payments",
            ["policy_id"],
        )


def downgrade() -> None:
    op.drop_index("ix_premium_payments_policy_id", table_name="premium_payments")
    op.drop_table("premium_payments")
