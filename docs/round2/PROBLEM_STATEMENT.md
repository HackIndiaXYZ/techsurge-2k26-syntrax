# PS-F03 Official Problem Statement

## Official PS requirement

Architect a fully automated, zero-touch parametric insurance engine that continuously streams weather telemetry, deterministically adjudicates policies against pre-agreed trigger conditions, and executes sub-minute payouts directly to digital wallets without a manual claim. The organizer-specified workflow is multi-source telemetry ingestion, validation/consensus, deterministic trigger evaluation, idempotent payout execution, and audit trail.

The minimum solution uses simulated or public weather telemetry for a defined micro-region, evaluates a defined policy trigger, and makes a simulated payout to a synthetic wallet. The PS permits public weather and earth-observation data, public UPI documentation as a reference, documented trigger structures, and synthetic policies/wallets/payouts.

## Official safety boundary

No real money, bank or wallet accounts, UPI/FedNow/stablecoin rails, production provider contracts, insurer licenses, regulatory approvals, or unproven production-security claims. Basis risk must be discussed plainly. Liquidity management, Byzantine-fault-tolerant consensus, and dual-rail routing are optional extensions, not MVP requirements.
