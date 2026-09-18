# Supabase Service Documentation

> **OWNER:** Akshaya (Infra)

## Role in TerraFlux

Supabase provides:

1. **PostgreSQL Database** — Durable persistence for all domain entities
2. **Authentication** — User identity (pre-existing, not modified)
3. **Row Level Security** — Access control at the database level
4. **Realtime** — Available for future subscription features

## What Supabase Does NOT Do

- Does not evaluate weather consensus (backend)
- Does not compute trigger outcomes (backend)
- Does not authorize settlements (backend)
- Does not run AI/ML models (AI layer)
- Does not serve the frontend directly for financial writes

## Access Patterns

| Actor                | Access Method                 | Permissions              |
|----------------------|-------------------------------|--------------------------|
| FastAPI Backend      | `service_role` key via SDK    | Full read/write          |
| Next.js Frontend     | `anon` key via SDK            | Read-only on ref tables  |
| Authenticated User   | `authenticated` via SDK       | Read-only on all tables  |

## RazorpayX Integration Boundary

RazorpayX is an **optional** test-mode payout provider.

The internal TerraFlux ledger (`wallets`, `wallet_transactions`) is authoritative.

RazorpayX status is stored in the `payouts` table as:
- `provider_name` (e.g., "razorpayx_test")
- `provider_reference` (e.g., transaction ID)

No RazorpayX secrets are stored in the database.

## AI Boundary

The database stores **authoritative deterministic facts**.

AI may query these facts for explanations but:
- Never writes consensus, triggers, or payouts
- Never modifies wallet balances
- Never overrides backend decisions
