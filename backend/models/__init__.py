"""
models/__init__.py — Export all SQLAlchemy models.

Importing this module ensures all models are registered with the Base metadata
before Alembic or create_all_tables() is called.
"""
from models.base import Base  # noqa: F401
from models.region import MicroRegion  # noqa: F401
from models.source import WeatherSource  # noqa: F401
from models.policy import Policy, PolicyStatus, TriggerRule  # noqa: F401
from models.telemetry import TelemetryEvent  # noqa: F401
from models.consensus import ConsensusResult, ConsensusStatus  # noqa: F401
from models.trigger import TriggerEvaluation, TriggerStatus  # noqa: F401
from models.payout import Payout, PayoutStatus  # noqa: F401
from models.wallet import Wallet, WalletTransaction  # noqa: F401
from models.audit import AuditEvent, AuditEventType  # noqa: F401
from models.policyholder import Policyholder  # noqa: F401
from models.payment import PremiumPayment, PaymentStatus  # noqa: F401

__all__ = [
    "Base",
    "MicroRegion",
    "WeatherSource",
    "Policy", "PolicyStatus", "TriggerRule",
    "TelemetryEvent",
    "ConsensusResult", "ConsensusStatus",
    "TriggerEvaluation", "TriggerStatus",
    "Payout", "PayoutStatus",
    "Wallet", "WalletTransaction",
    "AuditEvent", "AuditEventType",
    "Policyholder",
    "PremiumPayment", "PaymentStatus",
]

