# TerraFlux — Complete Engineering Audit

## 1. Executive Summary
This forensic audit evaluates the TerraFlux codebase against its intended architecture as an Autonomous Parametric Climate Insurance & Instant Settlement Engine. The current implementation is a sophisticated, functioning hackathon prototype with a robust, deterministic backend pipeline for weather ingestion, consensus, and synthetic settlement. Approximately 75% of the core insurance logic is successfully implemented.

However, the system lacks fundamental real-world application components. Authentication is entirely mocked, there is no real user identity model (specifically no phone numbers or real registration), and the AI Assistance/Phone Notification workflow is disconnected from the main pipeline and lacks the necessary orchestration (3-hour timeout, schedulers, notification persistence) to function autonomously. The remaining 25% of work must focus on bridging these gaps to evolve the system into a demonstratable, research-grade product.

## 2. Current System Architecture
**Current Architecture:**
- **Frontend (Next.js):** Communicates with the backend via REST APIs. Provides an unauthenticated demo environment. It drives the backend simulation.
- **Backend (FastAPI):** Exposes endpoints for simulations and data retrieval. Executes a deterministic pipeline: Telemetry Ingestion → Validation → Consensus → Trigger Evaluation → Settlement → Synthetic Wallet Credit.
- **Database (Supabase PostgreSQL):** Stores policies, weather data, consensus results, synthetic wallets, and an immutable audit ledger.
- **AI Module:** Contains FastAPI routes for anomaly detection, explanation, and Twilio voice calls, but is largely unused by the frontend or automated workflows.

## 3. Repository Structure
- `backend/`: FastAPI application containing `main.py`, `routers/`, `services/`, `models/`, `schemas/`, `providers/`, and `tests/`.
- `backend/ai/`: Isolated module containing AI explanations, anomaly scoring, and Twilio voice wrappers (`voice.py`, `router.py`).
- `frontend/`: Next.js 15 application (App Router) with Tailwind CSS, containing `src/app/`, `src/components/`, `src/lib/`.
- `supabase/`: Database migrations (`migrations/`) and seeds.
- `tests/`: Project root tests (Playwright boilerplate).

## 4. Technology Stack
**Frontend:**
- Framework: Next.js (App Router)
- Language: TypeScript
- UI/Styling: Tailwind CSS, Lucide React icons
- State Management: React Context (`src/lib/context.tsx`)
- Authentication: None (Mocked UI)

**Backend:**
- Framework: FastAPI
- Language: Python (likely 3.12+ given UV usage)
- ORM: SQLAlchemy (Async), Alembic
- AI/Telephony: Twilio (partially implemented), Gemini (via wrappers)

**Database:**
- Platform: Supabase PostgreSQL
- Data Model: Highly normalized with Enums, Constraints, and Row Level Security (RLS).

## 5. Frontend Audit
- **Login (`app/login/page.tsx`):** UI PRESENT — BACKEND FUNCTIONALITY MISSING. The login form is a static mock that routes directly to `/dashboard` without any API call or state mutation.
- **Dashboard (`app/dashboard/page.tsx`):** IMPLEMENTED. Fetches system health, policy, wallet, and audit events. Uses hardcoded IDs (`DEMO_POLICY_ID`). 
- **Weather / Simulation (`app/weather/page.tsx`):** IMPLEMENTED. Connects to `/simulations` endpoint. Drives the deterministic pipeline with simulated scenarios (Normal, Corrupted, No Consensus).
- **Wallet (`app/wallet/page.tsx`):** IMPLEMENTED IN CODE. Displays synthetic transactions.
- **Events (`app/events/page.tsx`):** IMPLEMENTED. Displays the audit trail from the database.

## 6. Backend Audit
- **Routers:** `health.py`, `telemetry.py`, `simulations.py`, `policies.py`, `payouts.py`, `wallets.py`, `audit.py`, `weather.py`, `ai/router.py`.
- **Pipeline Services:** `consensus.py`, `trigger.py`, `settlement.py` are robustly implemented.
- **AI Integration:** `ai/router.py` exists but is NOT called by the frontend or backend pipeline.
- **Polling:** `polling.py` implements a background weather polling loop, but it does not orchestrate notifications or AI workflows.
- **Authentication:** COMPLETELY MISSING. No authentication middleware, no JWT validation, no session management.

## 7. Database Audit
- `policyholders`: Minimal schema (`id`, `display_name`). MISSING phone numbers, emails, or Supabase Auth links.
- `micro_regions`, `weather_sources`, `policies`, `trigger_rules`: Fully implemented reference data.
- `telemetry_events`, `consensus_results`, `consensus_members`, `trigger_evaluations`: Implemented.
- `wallets`, `payouts`, `wallet_transactions`: Implemented synthetic financial ledger.
- `audit_events`: Implemented immutable event store.
- `notifications`: COMPLETELY MISSING.
- `call_logs`: COMPLETELY MISSING.

## 8. Authentication Audit
**Classification: RED**
Authentication is entirely mocked and bypassable. 
- Real registration does not exist.
- Email/Password login is a UI mock that blindly pushes to `/dashboard`.
- Phone number is not collected or verified.
- Unauthenticated users have full access to all endpoints.
- Authorization is not enforced; the frontend uses hardcoded IDs (`DEMO_POLICY_ID`, `DEMO_WALLET_ID`) to fetch data.

## 9. User / Policyholder Identity Audit
**Classification: COMPLETELY MISSING (Real Identity) / PARTIALLY IMPLEMENTED (Synthetic Data)**
The conceptual relationship `AUTH USER → POLICYHOLDER → POLICY → WALLET` is broken at the root. There is no `users` table or authentication identity. `policyholders` exists only as a synthetic construct to hold a `display_name`. Consequently, there is nowhere for the phone number to live, making autonomous AI calls impossible without hardcoding.

## 10. Weather Pipeline Audit
**Classification: IMPLEMENTED IN CODE**
The pipeline logic (ingestion → normalization → anomaly detection) exists in `backend/services/telemetry.py`. Data is fetched from OpenMeteo, AccuWeather, and IMD via `backend/providers`. The data model (`telemetry_events`) supports idempotency via `source_id` and `source_event_id` unique constraints.

## 11. Consensus Audit
**Classification: IMPLEMENTED IN CODE**
The consensus logic evaluates observations in `backend/services/consensus.py`. It requires a quorum, filters outliers based on tolerance, and calculates the median value. The result is stored authoritatively in `consensus_results`.

## 12. Trigger Audit
**Classification: IMPLEMENTED IN CODE (REAL BACKEND LOGIC)**
Trigger evaluation is deterministic and executed via `backend/services/trigger.py`. It compares the consensus value against the policy's `trigger_rule` (e.g., rainfall >= 100 mm). The outcome is logged in `trigger_evaluations`.

## 13. Settlement Audit
**Classification: IMPLEMENTED IN CODE (SYNTHETIC)**
The settlement process (`backend/services/settlement.py`) is highly robust, employing two layers of idempotency (fast-path SELECT and DB UniqueConstraints) to prevent double payouts. It interfaces with a Mock Provider to simulate the disbursement. It does not move real money.

## 14. Wallet Audit
**Classification: IMPLEMENTED IN CODE (DEMO WALLET)**
The wallet represents a synthetic balance. `wallet_transactions` serve as an immutable ledger tracking credits. However, it is not tied to a real authenticated user.

## 15. Notification Audit
**Classification: COMPLETELY MISSING**
There is no implementation for notifications (in-app, push, SMS). The system does not record when a notification is delivered, nor does it track user acknowledgments or timestamps. The required 3-hour timeout mechanism (scheduler/worker) is absent.

## 16. AI Audit
**Classification: BACKEND LOGIC EXISTS BUT FRONTEND DOES NOT USE IT**
The AI module (`backend/ai`) provides REST endpoints for anomaly analysis and explanation generation. However, the frontend (`src/lib/api.ts`) never calls these endpoints. The AI is structurally isolated from the core deterministic loop, which correctly respects the architectural boundary (AI does not authorize payouts).

## 17. AI Phone Assistance Gap Audit
**Classification: PARTIALLY IMPLEMENTED (ORPHANED)**
`backend/ai/voice.py` contains a `TwilioVoiceProvider` capable of executing outbound calls and generating TwiML scripts. 
**Gaps:**
- No phone numbers are stored in the database.
- The 3-hour escalation timeout does not exist.
- No automated worker or scheduler triggers the call.
- The `TwilioVoiceProvider` defaults to a `MockVoiceProvider` in development.
- Call states (status, outcomes) are not persisted to the database.

## 18. Security Audit
- **Authentication Bypass:** Critical risk. The system currently operates without access controls.
- **IDOR Vulnerabilities:** High risk. Endpoints accept any `policy_id` or `wallet_id` without verifying ownership.
- **Row Level Security (RLS):** Implemented on the database (denying anon/authenticated writes), meaning only the backend (via service_role) can mutate state. This is a solid foundation, but meaningless without backend authorization.

## 19. Production Deployment Audit
*(Based on repository contents and standard practices)*
- Frontend is configured for Vercel (Next.js).
- Backend is configured for Uvicorn (suitable for Railway).
- Database migrations exist for Supabase.
- Local behavior relies on hardcoded seeds (`20260918191800_terraflux_seed.sql`).

## 20. Testing Audit
- **Backend:** `pytest` tests exist in `backend/tests/` covering consensus, providers, scenarios, and triggers. Test coverage for the deterministic core is good.
- **Frontend:** Playwright is configured, but only boilerplate tests exist (`tests/example.spec.ts`). Missing UI and E2E tests.

## 21. End-to-End Execution Trace
`USER → AUTHENTICATION` (BROKEN - Mocked)
`AUTHENTICATION → POLICY` (BROKEN - Hardcoded DEMO_POLICY_ID)
`POLICY → WEATHER DATA` (WORKING via `polling.py` / `/simulations`)
`WEATHER DATA → NORMALIZATION` (WORKING)
`NORMALIZATION → QUALITY CHECK` (WORKING)
`QUALITY CHECK → CONSENSUS` (WORKING)
`CONSENSUS → EVENT` (WORKING)
`EVENT → TRIGGER` (WORKING)
`TRIGGER → SETTLEMENT` (WORKING)
`SETTLEMENT → WALLET` (WORKING - Synthetic)
`WALLET → NOTIFICATION` (BROKEN - Missing)
`NOTIFICATION → USER RESPONSE` (BROKEN - Missing)
`USER RESPONSE → AI ASSISTANCE` (BROKEN - Missing 3-hour timer)
`AI ASSISTANCE → AUDIT` (BROKEN - Missing integration)

## 22. Current vs Target Comparison
| Capability | Current State | Target State |
|---|---|---|
| User Identity | Hardcoded Dummy | Real Supabase Auth |
| Phone Number | Missing | Collected & Verified |
| Telemetry & Consensus | Functional | Functional |
| Settlement & Wallet | Functional (Synthetic) | Functional (Synthetic) |
| Notification | Missing | Sent & Logged |
| Timeout Logic | Missing | 3-Hour Escalation |
| AI Phone Call | Isolated Code | Automated via Twilio |

## 23. Gap Matrix
| Capability | Current State | Evidence | Missing Work | Priority |
|---|---|---|---|---|
| **Authentication** | Mocked | `app/login/page.tsx` | Supabase Auth integration, session handling | P0 |
| **User Identity** | Missing | `policyholders` schema | `users` mapping, phone number collection | P0 |
| **Notifications** | Missing | Database schema | `notifications` table, delivery tracking | P1 |
| **Timeout Engine** | Missing | `services/polling.py` | Background scheduler for 3-hour wait | P1 |
| **AI Voice Caller** | Orphaned | `ai/voice.py` | Connect scheduler to Twilio trigger | P1 |
| **Call Logging** | Missing | Database schema | `call_logs` table, webhook receivers | P1 |
| **Frontend AI UI** | Missing | `src/lib/api.ts` | Integrate AI explanation APIs in UI | P2 |

## 24. Components We Can Reuse (KEEP AS-IS)
- `backend/services/telemetry.py`
- `backend/services/consensus.py`
- `backend/services/trigger.py`
- `backend/services/settlement.py`
- Database schema for policies, rules, telemetry, consensus, payouts, and wallets.
- General frontend dashboard layout and design system.

## 25. Components Requiring Modification
- `backend/models/policy.py` (Must link to a real user/policyholder).
- `frontend/src/lib/context.tsx` (Remove hardcoded IDs, fetch based on authenticated user).
- `backend/main.py` (Add authentication middleware).
- `frontend/src/app/login/page.tsx` (Replace with real authentication flow).

## 26. Components Completely Missing
- Real User Registration & Login
- Phone Number Collection & Verification UI
- Notifications System (Database tables, API routes)
- Escalation Scheduler / Worker (The 3-hour timer)
- Telephony Webhook Receivers (To capture user responses via dial pad)
- Database tables for AI Call status and transcripts.

## 27. Research-Paper Readiness
**Measurable Artifacts Currently Available:**
- Source agreement ratios.
- Deterministic trigger latency.
- Idempotency guarantees (duplicate settlement prevention).
**Missing for Papers:**
- AI interaction success rates.
- Notification acknowledgment latency.
- False-positive analysis (requires real historical backtesting data).

## 28. Demo Readiness
1. User registers: **MISSING**
2. User provides mobile number: **MISSING**
3. User authenticates: **MOCK**
4. User purchases policy: **MOCK (Hardcoded)**
5. Policy is visible: **WORKING**
6. Wallet associated: **WORKING**
7. Weather event occurs: **WORKING (Simulated)**
8. Sources processed: **WORKING**
9. Consensus reached: **WORKING**
10. Trigger fires: **WORKING**
11. Settlement occurs: **WORKING**
12. Wallet updates: **WORKING**
13. User receives notification: **MISSING**
14. User does not acknowledge: **MISSING**
15. 3-hour timeout: **MISSING**
16. AI assistance triggers: **MISSING**
17. AI call reaches phone: **PARTIAL (Code exists, no orchestration)**
18. Call outcome stored: **MISSING**
19. Audit trail visible: **WORKING (For backend events, missing AI events)**

## 29. Architectural Risks
- **Authentication Migration Risk:** High. Moving from hardcoded IDs to real JWTs requires changes across all backend routers and frontend contexts.
- **Race Conditions in 3-Hour Timeout:** The future scheduler must handle concurrent checks and ensure idempotency before triggering a Twilio call.
- **Telephony Webhooks:** Twilio will fire async webhooks for call status. The backend must securely ingest these and map them to the correct simulation/policy state.

## 30. Proposed Implementation Roadmap
**PHASE 1: Identity & Authentication (P0)**
- Integrate Supabase Auth in Next.js.
- Update database schema: link `auth.users` to `policyholders`.
- Add phone number field to user profile.
- Protect backend endpoints with JWT validation.

**PHASE 2: Notification & Acknowledgment Base (P1)**
- Create `notifications` DB table.
- Build backend logic to create a notification upon `PAYOUT_COMPLETED`.
- Build frontend UI for users to acknowledge the settlement.

**PHASE 3: The Escalation Engine (P1)**
- Implement a background worker (e.g., Celery, APScheduler, or a polling script) to query for unacknowledged notifications older than 3 hours.

**PHASE 4: Telephony & AI Integration (P1)**
- Wire the Escalation Engine to `backend/ai/voice.py`.
- Implement webhook endpoints to receive Twilio call status and digit responses.
- Record call outcomes into the `audit_events` table.

**PHASE 5: UI Integration & Testing (P2)**
- Connect the frontend to the `ai/router.py` explanation endpoints.
- End-to-end testing of the entire flow.

---

### WHAT TERRAFLUX ALREADY HAS
- Real telemetry ingestion from OpenMeteo, AccuWeather, IMD.
- Deterministic, robust consensus and threshold trigger engines.
- Idempotent synthetic settlement preventing duplicate payouts.
- Immutable database ledger for wallets and audits.
- Simulated frontend demonstration UI for the weather pipeline.

### WHAT TERRAFLUX CLAIMS BUT DOES NOT ACTUALLY IMPLEMENT
- AI-driven autonomous phone assistance (Code exists but is not orchestrated or triggered).
- Secure, real-world user accounts.

### WHAT IS PARTIALLY IMPLEMENTED
- Twilio integration (`voice.py` exists but is orphaned).
- AI Explanations (`ai/router.py` exists but frontend does not call it).

### WHAT IS COMPLETELY MISSING
- Supabase Authentication (Login, Registration).
- Phone Number collection and mapping.
- Notification persistence and delivery tracking.
- The 3-hour wait scheduler/worker.
- Webhook handlers for Twilio call states.

### WHAT MUST BE FIXED FIRST
1. Authentication & User Identity (Foundation for everything else).
2. Tying Policies and Wallets to the authenticated User.

### WHAT CAN BE LEFT UNCHANGED
- The core deterministic pipeline (`telemetry`, `consensus`, `trigger`, `settlement`).
- The database structure for the pipeline and synthetic wallets.

### THE REMAINING 25%
- [ ] Implement Supabase Auth (Frontend + Backend JWT).
- [ ] Add phone numbers to user profiles.
- [ ] Create `notifications` table and frontend acknowledgment UI.
- [ ] Build a background scheduler to detect 3-hour timeouts.
- [ ] Wire the scheduler to the existing Twilio `voice.py` logic.
- [ ] Add Twilio webhook receivers to log call success/failure.
- [ ] Remove hardcoded IDs (`DEMO_POLICY_ID`) from the frontend.

### FINAL ARCHITECTURE
**CURRENT ARCHITECTURE:**
Frontend (Unauth, Hardcoded) → Backend Pipeline (Simulations) → DB (Synthetic Wallet)

**TARGET ARCHITECTURE:**
User (Supabase Auth) → Frontend → Backend Pipeline → DB (Wallet & Notification) → [3 Hour Wait Scheduler] → Twilio API → User's Phone
