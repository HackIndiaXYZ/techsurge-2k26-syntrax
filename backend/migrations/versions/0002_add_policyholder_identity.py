"""Add policyholder identity fields

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-24

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create policyholders table
    op.create_table(
        "policyholders",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column("auth_user_id", sa.Uuid(), nullable=True),
        sa.Column("phone_number", sa.Text(), nullable=True),
        sa.Column("phone_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    
    op.create_unique_constraint("uq_policyholder_auth_user", "policyholders", ["auth_user_id"])
    
    # Add policyholder_id column to policies if it doesn't exist
    # (Handling case where it might have been added manually or not)
    # Since Alembic migration will run on fresh DB or existing, we should add it if missing
    # Actually, Alembic's add_column is standard.
    op.add_column("policies", sa.Column("policyholder_id", sa.Uuid(), nullable=True))
    
    # Add foreign key from policies to policyholders
    op.create_foreign_key(
        "fk_policyholder",
        "policies",
        "policyholders",
        ["policyholder_id"],
        ["id"],
        ondelete="RESTRICT"
    )

def downgrade() -> None:
    op.drop_constraint("fk_policyholder", "policies", type_="foreignkey")
    op.drop_column("policies", "policyholder_id")
    op.drop_table("policyholders")
