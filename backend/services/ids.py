"""
services/ids.py — ULID generation utility.

Uses python-ulid for time-ordered, lexicographically sortable IDs.
Falls back to UUID-based string if ULID library unavailable.
"""
try:
    from ulid import ULID

    def new_ulid() -> str:
        return str(ULID())

except ImportError:
    import uuid

    def new_ulid() -> str:  # type: ignore[misc]
        """Fallback: use UUID4 without hyphens, padded to 26 chars."""
        return uuid.uuid4().hex[:26].upper()

