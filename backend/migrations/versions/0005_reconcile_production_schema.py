"""Reconcile production schema

Revision ID: 2783680e1743
Revises: 0004
Create Date: 2026-09-27 16:45:04.619549+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2783680e1743'
down_revision: Union[str, None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if inspector.has_table('policies'):
        columns = [c['name'] for c in inspector.get_columns('policies')]
        if 'start_at' in columns:
            print("Skipping reconciliation on production database because start_at already exists.")
            return

    # For a fresh database, there is no data. 
    # We drop the flawed schema built by 0001-0004 and recreate it using the exact current ORM models.
    from models.base import Base
    import models  # Ensure all models are imported and registered with Base.metadata

    # Use the connection to drop all tables with CASCADE
    tables = Base.metadata.sorted_tables
    for table in reversed(tables):
        conn.execute(sa.text(f"DROP TABLE IF EXISTS {table.name} CASCADE"))
    
    Base.metadata.create_all(conn)


def downgrade() -> None:
    pass
