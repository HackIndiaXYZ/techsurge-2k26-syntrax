# Supabase Deployment Guide

> **OWNER:** Akshaya (Infra)  
> **PROJECT:** syntrax (`qdnwxtncipqbjreuzoxl`)

## Project Configuration

| Setting          | Value                          |
|------------------|--------------------------------|
| Project Name     | syntrax                        |
| Project Ref      | qdnwxtncipqbjreuzoxl           |
| Organization ID  | wfivbaxdpppghqhcaqid           |
| Region           | ap-south-1 (Mumbai)            |

## Linking (Already Done)

```bash
supabase link --project-ref qdnwxtncipqbjreuzoxl
```

> Do NOT relink to another project. Do NOT create a new Supabase project.

## Pushing Migrations

```bash
supabase db push
```

This pushes all local migrations to the remote Supabase database.

## Environment Variables

The backend (FastAPI) requires the following environment variables for database access:

```
SUPABASE_URL=https://qdnwxtncipqbjreuzoxl.supabase.co
SUPABASE_ANON_KEY=<anon-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
DATABASE_URL=postgresql://postgres.<ref>:<password>@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

> **NEVER** commit these values. Use `.env` files (gitignored) or environment variables.

## Security Checklist

- [x] RLS enabled on all 14 tables
- [x] `anon` role: read-only on `micro_regions` and `weather_sources` only
- [x] `authenticated` role: read-only on all tables
- [x] `service_role`: bypasses RLS (used by backend only)
- [x] No anonymous financial write policies
- [x] No secrets in migration files
- [x] No credentials in seed data
- [x] `.env` files are gitignored

## Running Integration Tests

```bash
set DATABASE_URL=postgresql://postgres.<ref>:<password>@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
pip install psycopg2-binary
python database/test_db_integration.py
```

## Schema Inspection

After pushing, verify via Supabase Dashboard → Table Editor, or:

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

Expected: 14 tables (audit_events, consensus_members, consensus_results, micro_regions, payouts, policies, policyholders, telemetry_events, telemetry_validation_results, trigger_evaluations, trigger_rules, wallet_transactions, wallets, weather_sources).
