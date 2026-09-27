"""wallet ownership

Revision ID: 198f035a1a5a
Revises: 2783680e1743
Create Date: 2026-09-27 17:13:08.657891+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '198f035a1a5a'
down_revision: Union[str, None] = '2783680e1743'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add policyholder_id column, nullable initially
    op.add_column('wallets', sa.Column('policyholder_id', sa.Uuid(), nullable=True))
    
    # 2. Populate policyholder_id by joining with policies
    op.execute("""
        UPDATE wallets
        SET policyholder_id = policies.policyholder_id
        FROM policies
        WHERE wallets.policy_id = policies.id
    """)

    # If any wallets still have NULL policyholder_id (e.g. orphans), delete them
    op.execute("DELETE FROM wallets WHERE policyholder_id IS NULL")

    # If there are duplicate policyholder_ids (e.g. user had multiple policies),
    # keep only the most recently updated/created wallet per policyholder
    op.execute("""
        DELETE FROM wallets
        WHERE id NOT IN (
            SELECT DISTINCT ON (policyholder_id) id
            FROM wallets
            ORDER BY policyholder_id, created_at DESC
        )
    """)

    # 3. Alter column to not null
    op.alter_column('wallets', 'policyholder_id', nullable=False)
    
    # 4. Create unique constraint
    op.create_unique_constraint('uq_wallets_policyholder_id', 'wallets', ['policyholder_id'])
    
    # 5. Create foreign key
    op.create_foreign_key('fk_wallets_policyholder_id_policyholders', 'wallets', 'policyholders', ['policyholder_id'], ['id'], ondelete='RESTRICT')
    
    # 6. Drop old column and FK
    # Need to query for the exact constraint name if 'wallets_policy_id_fkey' is incorrect, but normally it's that.
    op.drop_constraint('wallets_policy_id_fkey', 'wallets', type_='foreignkey')
    op.drop_column('wallets', 'policy_id')

def downgrade() -> None:
    op.add_column('wallets', sa.Column('policy_id', sa.Uuid(), nullable=True))
    
    # Attempt to restore policy_id (might not be exact if multiple policies existed, but best effort)
    op.execute("""
        UPDATE wallets
        SET policy_id = (SELECT id FROM policies WHERE policies.policyholder_id = wallets.policyholder_id LIMIT 1)
    """)
    op.execute("DELETE FROM wallets WHERE policy_id IS NULL")

    op.drop_constraint('fk_wallets_policyholder_id_policyholders', 'wallets', type_='foreignkey')
    op.drop_constraint('uq_wallets_policyholder_id', 'wallets', type_='unique')
    op.alter_column('wallets', 'policy_id', nullable=False)
    op.create_foreign_key('wallets_policy_id_fkey', 'wallets', 'policies', ['policy_id'], ['id'], ondelete='RESTRICT')
    op.drop_column('wallets', 'policyholder_id')

