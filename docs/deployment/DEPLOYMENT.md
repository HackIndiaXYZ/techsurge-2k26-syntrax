# Deployment Architecture

**Team design decision:** deploy only after local clean-trigger, outlier and retry paths pass. Host Next.js on Vercel and FastAPI on Render; use a Supabase PostgreSQL project only when approved credentials are available. Railway is an emergency fallback. This is a demo deployment, not a production availability claim.

Set `FRONTEND_ORIGIN`, `DATABASE_URL`, `DEMO_OPERATOR_TOKEN`, and deployment URLs as provider environment secrets. Enable CORS only for the deployed frontend origin. Never ship simulation routes publicly without the operator token.
