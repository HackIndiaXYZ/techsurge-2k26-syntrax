# TerraFlux Migrations

> **OWNER:** Akshaya (Infra)

## Migration List

| Order | Filename                                     | Purpose                               |
|-------|----------------------------------------------|---------------------------------------|
| 1     | `20260918132418_remote_schema.sql`           | Baseline remote schema (pulled)       |
| 2     | `20260918191700_terraflux_schema.sql`        | TerraFlux tables, enums, RLS, indexes |
| 3     | `20260918191800_terraflux_seed.sql`          | Deterministic synthetic seed data     |

## Migration Strategy

- Migrations run in lexicographic timestamp order.
- The baseline migration is preserved as the remote schema snapshot.
- The schema migration is **additive** — it does not drop or modify baseline objects.
- The seed migration uses `ON CONFLICT DO NOTHING` for safe re-runs.

## Applying Migrations

### To Remote (Supabase Hosted)

```bash
supabase db push
```

This applies all pending migrations in order.

### Local Development

```bash
supabase start        # Start local Supabase stack (requires Docker)
supabase db reset     # Reset local DB and re-apply all migrations
```

> **WARNING:** Never run `supabase db reset` against the remote database.

## Rollback Considerations

- No destructive rollback scripts are provided for MVP.
- Financial tables use `ON DELETE RESTRICT` — data cannot be accidentally cascade-deleted.
- If a rollback is needed, create a new migration that reverses specific changes.
- Never drop tables containing financial or audit data without explicit team approval.

## Adding New Migrations

```bash
supabase migration new <description>
```

This creates a new timestamped `.sql` file in `supabase/migrations/`.
