# SYSTEM INVENTORY

## 1. Project Information
- **Product:** TerraFlux
- **Repository:** `https://github.com/HackIndiaXYZ/techsurge-2k26-syntrax`
- **Frontend Domain:** `https://terrafluxapp.xyz`
- **Backend Domain:** `https://api.terrafluxapp.xyz`

## 2. Infrastructure & Deployment
- **Railway Project:** `hackathon project` (ID: `33452ec6-ded9-442c-9e62-8a6e2c13360f`)
- **Railway Environment:** `production`
- **Railway Service:** `techsurge-2k26-syntrax` (Status: Online)
- **Vercel Project:** `terraflux` (sanjus-projects-ad03de60)
- **Database:** PostgreSQL (Supabase)

## 3. Directory Structure
- `backend/`: FastAPI Python Application
    - `main.py`: Entry point
    - `routers/`: API endpoints (`policies.py`, `metrics.py`, `webhook.py`, etc.)
    - `models/`: SQLAlchemy ORM definitions (`policy.py`, `wallet.py`, `ai_assistance.py`, etc.)
    - `schemas/`: Pydantic definitions
    - `services/`: Business logic (`simulation.py`, `polling.py`, `trigger.py`, `settlement.py`, etc.)
    - `tests/`: Comprehensive Pytest suite covering all phases (1-10)
    - `seeds/`: Initial data population logic
- `frontend/`: Next.js React Application
- `database/`: Database configuration (possibly migrations or Supabase schema)
- `supabase/`: Supabase configuration
- `infra/`: Infrastructure definitions
- `scripts/`: Assorted helper scripts
- `ai/`: AI orchestration
- `docs/`: System documentation
- `tests/`: End-to-end tests
- `playwright-report/`: E2E results

## 4. Components & Verification Status
- **Authentication:** Supabase JWT. (Verified locally)
- **Database Migrations:** Alembic `15db173ea738 (head)`. (Verified locally)
- **Weather Consensus:** 2-of-3 threshold checking median and tolerance. (Verified locally)
- **Trigger Processing:** >= 100mm threshold evaluation. (Verified locally)
- **Settlement & Wallet:** Idempotent concurrent protected credits. (Verified locally)
- **Notification & Escalation:** 3-hour SLA AI handoff logic. (Verified locally)
- **Voice Integrations:** Twilio / Mock Provider with async call tracking. (Verified locally)
- **Webhook Processing:** Safe transition updating on `CallLog` and `AuditEvent`. (Verified locally)
- **Research Metrics:** Aggregate telemetry output on `/metrics`. (Verified locally)

## 5. Security Posture
- IDOR protections explicitly verified via User A / User B isolation matrix.
- Environment secrets decoupled and tested without hardcoded exposure.
- Cross-user wallet settlement prevented by `policyholder_id` constraints.
- Razorpay logic explicitly bound to Sandbox modes only.
