# Deployment Strategy

> **TBD — DECIDE AFTER PROBLEM STATEMENT:** This is a candidate stack and may change after the PS.

## Candidate Stack
- **Frontend:** Vercel
- **Backend:** Render
- **Database/Auth/Storage:** Supabase

## Deployment Template
- **Environment variables:** Manage secrets in the deployment platform, not in source code.
- **Production vs development configuration:** Clear separation of dev, staging (if any), and prod environments.
- **Deployment order:** Database -> Backend -> Frontend.
- **Health checks:** Endpoints to verify service status.
- **Logs:** Centralized logging for debugging.
- **Rollback strategy:** Quick reversion to the previous stable release.
- **CORS configuration:** Allow frontend domain to access backend APIs.
- **Frontend/Backend URL configuration:** Inject backend URLs into frontend via environment variables.

