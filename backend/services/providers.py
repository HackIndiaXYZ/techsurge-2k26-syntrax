"""
services/providers.py — Payout provider abstraction for PS-F03.

Architecture:
    Settlement Service
          ↓
    PayoutProvider (Protocol / abstract interface)
          ↓
    MockPayoutProvider  ← demo / hackathon / testing

The settlement engine remains the financial authority.
The provider is only responsible for *executing* the synthetic disbursement.

Provider NEVER decides whether a payout should occur.
Provider NEVER authorizes a payout independently.
Provider ONLY executes what settlement has already authorized.

NO real money.
NO real bank.
NO real UPI.
NO external API calls.
NO credentials required.
"""
import enum
from dataclasses import dataclass
from typing import Protocol


# ── Provider result types ─────────────────────────────────────────────────────

class ProviderStatus(str, enum.Enum):
    """Outcome of a provider disbursement attempt."""
    SUCCESS = "SUCCESS"
    FAILED  = "FAILED"
    UNKNOWN = "UNKNOWN"   # timeout / indeterminate — must be treated as failed
                          # until confirmed via reconciliation


@dataclass(frozen=True)
class ProviderResult:
    """
    Structured result from a provider disbursement call.

    provider_reference:
        Provider-assigned transaction/reference ID.
        None when provider call did not reach the provider (network error, etc.)

    status:
        SUCCESS | FAILED | UNKNOWN

    error_code:
        Short machine-readable error identifier from the provider.

    error_message:
        Human-readable message for logging/display.
    """
    status: ProviderStatus
    provider_reference: str | None = None
    error_code: str | None = None
    error_message: str | None = None


# ── Provider Protocol ─────────────────────────────────────────────────────────

class PayoutProvider(Protocol):
    """
    Structural protocol for payout providers.

    Any class implementing `disburse()` satisfies this protocol.
    No inheritance required.
    """
    def disburse(
        self,
        payout_id: str,
        amount_paise: int,
        policy_id: str,
        idempotency_key: str,
    ) -> ProviderResult:
        """
        Attempt to disburse a synthetic payout.

        Args:
            payout_id:        Internal payout record ID.
            amount_paise:     Amount in integer paise. MUST be int — never float.
            policy_id:        Policy the payout belongs to.
            idempotency_key:  Stable key for deduplication (policy_id::trigger_evaluation_id).

        Returns:
            ProviderResult with status, reference, and optional error detail.
        """
        ...   # pragma: no cover


# ── Mock / Simulated Provider ─────────────────────────────────────────────────

class MockPayoutProvider:
    """
    Deterministic mock provider for demo, hackathon, and unit tests.

    Simulates:
      SUCCESS  — normal case
      FAILED   — deterministic failure (controlled by force_failure)
      UNKNOWN  — simulated timeout / indeterminate (controlled by force_unknown)

    Does NOT sleep.
    Does NOT make external calls.
    Does NOT require credentials.
    Does NOT touch the database.

    The settlement service is responsible for persisting results.
    """

    def __init__(
        self,
        force_failure: bool = False,
        force_unknown: bool = False,
    ) -> None:
        """
        Args:
            force_failure: If True, every call returns FAILED.
            force_unknown: If True, every call returns UNKNOWN (timeout simulation).
                           Takes precedence over force_failure.
        """
        self._force_failure = force_failure
        self._force_unknown = force_unknown

    def disburse(
        self,
        payout_id: str,
        amount_paise: int,
        policy_id: str,
        idempotency_key: str,
    ) -> ProviderResult:
        """
        Simulate a disbursement.

        Normal (default):
            Returns SUCCESS with a synthetic reference ID.

        force_unknown=True:
            Returns UNKNOWN — caller must treat as FAILED until reconciled.

        force_failure=True:
            Returns FAILED with error details.

        Idempotency:
            Calling with the same idempotency_key multiple times always returns
            the same deterministic outcome (SUCCESS for mock — no state kept).
            Real providers must be called with stable idempotency_key values.
        """
        assert isinstance(amount_paise, int), (
            f"amount_paise must be int, got {type(amount_paise).__name__}"
        )

        if self._force_unknown:
            return ProviderResult(
                status=ProviderStatus.UNKNOWN,
                provider_reference=None,
                error_code="PROVIDER_TIMEOUT",
                error_message=(
                    "Provider did not respond within the expected window. "
                    "Outcome is unknown. Treat as FAILED until reconciled."
                ),
            )

        if self._force_failure:
            return ProviderResult(
                status=ProviderStatus.FAILED,
                provider_reference=None,
                error_code="PROVIDER_DECLINED",
                error_message=(
                    f"Mock provider declined payout {payout_id!r}. "
                    "Simulated failure for testing."
                ),
            )

        # Success path — deterministic synthetic reference
        provider_reference = f"MOCK-{str(payout_id)[:8].upper()}-{amount_paise}P"
        return ProviderResult(
            status=ProviderStatus.SUCCESS,
            provider_reference=provider_reference,
            error_code=None,
            error_message=None,
        )


# ── Default provider instance (used by settlement service) ────────────────────

# Singleton mock provider used across the application.
# Swap this out at startup via dependency injection / config when a real provider is available.
_default_provider: PayoutProvider = MockPayoutProvider()


def get_default_provider() -> PayoutProvider:
    """Return the currently configured payout provider."""
    return _default_provider
