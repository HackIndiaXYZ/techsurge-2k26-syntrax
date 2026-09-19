"""
services/ids.py — ID generation utility.

Generates UUID4 values for use as primary keys.
The PostgreSQL schema uses UUID columns, so all IDs must be valid UUIDs.
"""
import uuid


def new_ulid() -> str:
    """Generate a new UUID4 string for use as a primary key.
    
    Named 'new_ulid' for backward compatibility with existing callers,
    but generates standard UUID4 values since the DB uses UUID columns.
    """
    return str(uuid.uuid4())


def new_uuid() -> uuid.UUID:
    """Generate a new UUID4 object for direct use with PgUUID columns."""
    return uuid.uuid4()
