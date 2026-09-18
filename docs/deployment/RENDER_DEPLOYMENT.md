# Render Backend Deployment

Deploy the FastAPI service with a start command owned by the backend project, server-side `DATABASE_URL`, `FRONTEND_ORIGIN`, and `DEMO_OPERATOR_TOKEN`. Run migration/seed only through an approved release step, then smoke-test read dashboard, clean trigger, and retry. Record the deployed API URL in the team handoff, not a secret.
