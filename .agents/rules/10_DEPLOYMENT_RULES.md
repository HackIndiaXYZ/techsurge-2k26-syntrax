# PS-F03 Deployment Rules

1. Akshaya owns optional deployment: Vercel frontend, Render FastAPI, Supabase PostgreSQL, Railway fallback.
2. Deploy after local core scenarios pass; use server-side provider secrets and configured CORS.
3. Prepare a deterministic local fallback; deployment is not a production availability claim.
