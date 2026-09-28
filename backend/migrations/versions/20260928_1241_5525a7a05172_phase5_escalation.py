"""phase5_escalation

Revision ID: 5525a7a05172
Revises: phase4_notifications
Create Date: 2026-09-28 12:41:51.844142+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5525a7a05172'
down_revision: Union[str, None] = 'phase4_notifications'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add escalation fields to notifications
    op.add_column('notifications', sa.Column('escalation_due_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('notifications', sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create AI assistance handoffs table
    op.create_table('ai_assistance_handoffs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('notification_id', sa.Uuid(), nullable=False),
        sa.Column('policyholder_id', sa.Uuid(), nullable=False),
        sa.Column('policy_id', sa.Uuid(), nullable=False),
        sa.Column('payout_id', sa.Uuid(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('context_metadata', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['payout_id'], ['payouts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['policyholder_id'], ['policyholders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('notification_id')
    )


def downgrade() -> None:
    op.drop_table('ai_assistance_handoffs')
    op.drop_column('notifications', 'escalated_at')
    op.drop_column('notifications', 'escalation_due_at')
