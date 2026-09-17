# SECURITY

**FINAL SECURITY MODEL: UNKNOWN UNTIL ROUND 2 PROBLEM STATEMENT IS REVEALED.**

## Default Auth Architecture
- **Supabase Auth + PostgreSQL RLS**
- Handles JWTs, integrates natively with Postgres Row Level Security (RLS).
- (Fallback: Firebase Auth, Clerk, Auth0).

## Security Principles
- Never put secret API keys in the frontend (use server-side).
- Never commit secrets to Git (.env is gitignored). Use .env.example.
- Enforce HTTPS/TLS, input validation, rate limiting, and CORS.
- Implement least privilege access.
