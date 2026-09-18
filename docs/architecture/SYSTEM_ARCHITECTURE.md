# PS-F03 System Architecture

## Team design decision

Build a modular monolith: a Next.js web client, one FastAPI service, and PostgreSQL (Supabase-hosted if provisioned). Direct HTTP processing is enough for the small, seeded event volume. The architecture stays event-shaped in data, without introducing a broker.

```text
Simulation controls / public-shaped source adapters
                 |
          POST telemetry event
                 v
 FastAPI: validate -> deduplicate -> consensus -> trigger -> payout -> audit
                 |                              |
                 v                              v
           PostgreSQL                       synthetic wallet ledger
                 |
                 v
 Next.js dashboard polls read APIs every second during demo
```

The backend is the only component allowed to mutate policy, telemetry, payout, transaction, or audit data. The frontend presents API data and issues only documented operator simulation commands. AI is not on the decision path.

## Trust boundary

Incoming telemetry is untrusted until it passes schema, identity, freshness, range, and duplicate checks. A consensus result is evidence, not a payment. Only the deterministic trigger engine can create a payout instruction, and only the idempotent settlement service can credit a synthetic wallet.
