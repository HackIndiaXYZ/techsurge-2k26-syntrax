"""add notifications table

Revision ID: phase4_notifications
Revises: 198f035a1a5a
Create Date: 2026-09-28 10:55:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'phase4_notifications'
down_revision: Union[str, None] = '198f035a1a5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'notifications',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('policyholder_id', sa.Uuid(), nullable=False),
        sa.Column('policy_id', sa.Uuid(), nullable=False),
        sa.Column('payout_id', sa.Uuid(), nullable=False),
        sa.Column('event_type', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False, server_default='UNREAD'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['policyholder_id'], ['policyholders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['payout_id'], ['payouts.id'], ondelete='CASCADE'),
    )

    # Idempotency constraint: one settlement notification per payout
    op.create_unique_constraint(
        'uq_notification_payout_event',
        'notifications',
        ['payout_id', 'event_type'],
    )

    # Index for querying by policyholder (GET /notifications)
    op.create_index(
        'ix_notifications_policyholder_id',
        'notifications',
        ['policyholder_id'],
    )

    # Index for querying by policy
    op.create_index(
        'ix_notifications_policy_id',
        'notifications',
        ['policy_id'],
    )


def downgrade() -> None:
    op.drop_index('ix_notifications_policy_id', table_name='notifications')
    op.drop_index('ix_notifications_policyholder_id', table_name='notifications')
    op.drop_constraint('uq_notification_payout_event', 'notifications', type_='unique')
    op.drop_table('notifications')
