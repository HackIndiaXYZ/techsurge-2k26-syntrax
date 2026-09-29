"""phase7_call_logs

Revision ID: 15db173ea738
Revises: 40d6ad434813
Create Date: 2026-09-29 05:06:54.620916+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '15db173ea738'
down_revision: Union[str, None] = '40d6ad434813'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('call_logs',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('voice_call_job_id', sa.Uuid(), nullable=False),
    sa.Column('provider_call_id', sa.Text(), nullable=True),
    sa.Column('provider', sa.Text(), nullable=False),
    sa.Column('event_type', sa.Text(), nullable=False),
    sa.Column('provider_status', sa.Text(), nullable=True),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('payload_metadata', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.ForeignKeyConstraint(['voice_call_job_id'], ['voice_call_jobs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('voice_call_jobs', sa.Column('requested_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('voice_call_jobs', sa.Column('started_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('voice_call_jobs', sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('voice_call_jobs', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('voice_call_jobs', sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    op.drop_column('voice_call_jobs', 'failed_at')
    op.drop_column('voice_call_jobs', 'completed_at')
    op.drop_column('voice_call_jobs', 'answered_at')
    op.drop_column('voice_call_jobs', 'started_at')
    op.drop_column('voice_call_jobs', 'requested_at')
    op.drop_table('call_logs')
