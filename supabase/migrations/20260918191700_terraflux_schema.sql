-- ============================================================
-- TerraFlux Persistence Layer
-- Migration: 20260918191700_terraflux_schema
--
-- Implements the complete data model for autonomous parametric
-- climate insurance & instant settlement.
--
-- SAFETY: This migration is additive. It does not drop or
-- modify any objects from the baseline remote schema.
--
-- MONEY: All monetary values stored as bigint (paise).
-- TIMESTAMPS: All timestamptz (UTC).
-- IDs: All uuid with gen_random_uuid().
-- ============================================================

-- ============================================================
-- 1. CUSTOM ENUM TYPES
-- ============================================================

-- Telemetry validation states
CREATE TYPE public.validation_state AS ENUM (
    'PENDING',
    'ACCEPTED',
    'REJECTED',
    'DUPLICATE'
);

-- Consensus lifecycle
CREATE TYPE public.consensus_state AS ENUM (
    'PENDING',
    'ACHIEVED',
    'NO_CONSENSUS',
    'EXPIRED'
);

-- Consensus member roles
CREATE TYPE public.consensus_role AS ENUM (
    'ACCEPTED',
    'OUTLIER',
    'REJECTED'
);

-- Trigger evaluation outcomes
CREATE TYPE public.trigger_outcome AS ENUM (
    'TRIGGERED',
    'NOT_MET',
    'NOT_ELIGIBLE',
    'NO_CONSENSUS',
    'ALREADY_TRIGGERED',
    'EXPIRED'
);

-- Policy lifecycle
CREATE TYPE public.policy_status AS ENUM (
    'DRAFT',
    'ACTIVE',
    'EXPIRED',
    'CANCELLED',
    'SUSPENDED'
);

-- Wallet lifecycle
CREATE TYPE public.wallet_status AS ENUM (
    'ACTIVE',
    'SUSPENDED',
    'CLOSED'
);

-- Payout lifecycle
CREATE TYPE public.payout_state AS ENUM (
    'PENDING',
    'PROCESSING',
    'COMPLETED',
    'FAILED',
    'CANCELLED'
);

-- Wallet transaction direction
CREATE TYPE public.transaction_direction AS ENUM (
    'CREDIT',
    'DEBIT'
);

-- Trigger rule operators
CREATE TYPE public.trigger_operator AS ENUM (
    'GTE',
    'GT',
    'LTE',
    'LT',
    'EQ'
);

-- ============================================================
-- 2. LOOKUP / REFERENCE TABLES
-- ============================================================

-- 2.1 policyholders
CREATE TABLE public.policyholders (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    display_name text NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_policyholders_display_name UNIQUE (display_name)
);

COMMENT ON TABLE public.policyholders IS 'Synthetic/demo policyholders. No real PII.';

-- 2.2 micro_regions
CREATE TABLE public.micro_regions (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code        text NOT NULL,
    name        text NOT NULL,
    timezone    text NOT NULL,
    active      boolean NOT NULL DEFAULT true,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_micro_regions_code UNIQUE (code)
);

COMMENT ON TABLE public.micro_regions IS 'Geographic micro-regions for policy coverage and weather observation.';

-- 2.3 weather_sources
CREATE TABLE public.weather_sources (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code        text NOT NULL,
    kind        text NOT NULL,
    enabled     boolean NOT NULL DEFAULT true,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_weather_sources_code UNIQUE (code)
);

COMMENT ON TABLE public.weather_sources IS 'Known telemetry provider identities (IMD, OPENWEATHER, COMMUNITY, etc.).';

-- 2.4 trigger_rules
CREATE TABLE public.trigger_rules (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    metric          text NOT NULL,
    operator        public.trigger_operator NOT NULL,
    threshold_value numeric NOT NULL,
    unit            text NOT NULL,
    window_minutes  integer NOT NULL,
    version         integer NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_trigger_rules_definition UNIQUE (metric, operator, threshold_value, unit, window_minutes, version),
    CONSTRAINT ck_trigger_rules_window_positive CHECK (window_minutes > 0),
    CONSTRAINT ck_trigger_rules_version_positive CHECK (version > 0)
);

COMMENT ON TABLE public.trigger_rules IS 'Versioned deterministic trigger definitions. Backend evaluates these, not the database.';

-- ============================================================
-- 3. POLICIES
-- ============================================================

CREATE TABLE public.policies (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    policyholder_id     uuid NOT NULL,
    region_id           uuid NOT NULL,
    trigger_rule_id     uuid NOT NULL,
    payout_amount_paise bigint NOT NULL,
    status              public.policy_status NOT NULL DEFAULT 'ACTIVE',
    start_at            timestamptz NOT NULL,
    end_at              timestamptz NOT NULL,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fk_policies_policyholder FOREIGN KEY (policyholder_id)
        REFERENCES public.policyholders (id) ON DELETE RESTRICT,
    CONSTRAINT fk_policies_region FOREIGN KEY (region_id)
        REFERENCES public.micro_regions (id) ON DELETE RESTRICT,
    CONSTRAINT fk_policies_trigger_rule FOREIGN KEY (trigger_rule_id)
        REFERENCES public.trigger_rules (id) ON DELETE RESTRICT,
    CONSTRAINT ck_policies_payout_positive CHECK (payout_amount_paise > 0),
    CONSTRAINT ck_policies_date_range CHECK (end_at > start_at)
);

CREATE INDEX idx_policies_region_status_dates
    ON public.policies (region_id, status, start_at, end_at);

COMMENT ON TABLE public.policies IS 'Policy definitions linking holder, region, and trigger rule. Never cascade-deleted.';

-- ============================================================
-- 4. TELEMETRY
-- ============================================================

-- 4.1 telemetry_events
CREATE TABLE public.telemetry_events (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id        uuid NOT NULL,
    region_id        uuid NOT NULL,
    source_event_id  text NOT NULL,
    metric           text NOT NULL,
    value            numeric NOT NULL,
    unit             text NOT NULL,
    observed_at      timestamptz NOT NULL,
    window_start     timestamptz NOT NULL,
    window_end       timestamptz NOT NULL,
    received_at      timestamptz NOT NULL DEFAULT now(),
    validation_state public.validation_state NOT NULL DEFAULT 'PENDING',
    metadata         jsonb NOT NULL DEFAULT '{}',
    created_at       timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fk_telemetry_source FOREIGN KEY (source_id)
        REFERENCES public.weather_sources (id) ON DELETE RESTRICT,
    CONSTRAINT fk_telemetry_region FOREIGN KEY (region_id)
        REFERENCES public.micro_regions (id) ON DELETE RESTRICT,
    CONSTRAINT uq_telemetry_source_event UNIQUE (source_id, source_event_id)
);

CREATE INDEX idx_telemetry_region_metric_window
    ON public.telemetry_events (region_id, metric, window_end, validation_state);

COMMENT ON TABLE public.telemetry_events IS 'Raw/normalized weather observations. unique(source_id, source_event_id) provides ingestion idempotency.';

-- 4.2 telemetry_validation_results
CREATE TABLE public.telemetry_validation_results (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    telemetry_event_id  uuid NOT NULL,
    validation_rule     text NOT NULL,
    outcome             text NOT NULL,
    reason_code         text,
    details             jsonb NOT NULL DEFAULT '{}',
    created_at          timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fk_validation_telemetry FOREIGN KEY (telemetry_event_id)
        REFERENCES public.telemetry_events (id) ON DELETE RESTRICT
);

CREATE INDEX idx_validation_telemetry_event
    ON public.telemetry_validation_results (telemetry_event_id);

COMMENT ON TABLE public.telemetry_validation_results IS 'Evidence records for telemetry validation/anomaly detection.';

-- ============================================================
-- 5. CONSENSUS
-- ============================================================

-- 5.1 consensus_results
CREATE TABLE public.consensus_results (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id    uuid NOT NULL,
    metric       text NOT NULL,
    window_start timestamptz NOT NULL,
    window_end   timestamptz NOT NULL,
    state        public.consensus_state NOT NULL DEFAULT 'PENDING',
    value        numeric,
    quorum       integer NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fk_consensus_region FOREIGN KEY (region_id)
        REFERENCES public.micro_regions (id) ON DELETE RESTRICT,
    CONSTRAINT uq_consensus_window UNIQUE (region_id, metric, window_start, window_end),
    CONSTRAINT ck_consensus_quorum_non_negative CHECK (quorum >= 0),
    CONSTRAINT ck_consensus_value_when_achieved CHECK (
        (state != 'ACHIEVED') OR (value IS NOT NULL)
    )
);

COMMENT ON TABLE public.consensus_results IS 'Authoritative multi-source consensus result per observation window.';

-- 5.2 consensus_members
CREATE TABLE public.consensus_members (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    consensus_result_id uuid NOT NULL,
    telemetry_event_id  uuid NOT NULL,
    source_id           uuid NOT NULL,
    role                public.consensus_role NOT NULL,
    normalized_value    numeric NOT NULL,
    rejection_reason    text,
    created_at          timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fk_member_consensus FOREIGN KEY (consensus_result_id)
        REFERENCES public.consensus_results (id) ON DELETE RESTRICT,
    CONSTRAINT fk_member_telemetry FOREIGN KEY (telemetry_event_id)
        REFERENCES public.telemetry_events (id) ON DELETE RESTRICT,
    CONSTRAINT fk_member_source FOREIGN KEY (source_id)
        REFERENCES public.weather_sources (id) ON DELETE RESTRICT,
    CONSTRAINT uq_consensus_member UNIQUE (consensus_result_id, telemetry_event_id)
);

COMMENT ON TABLE public.consensus_members IS 'Which telemetry observations participated in consensus, and their roles.';

-- ============================================================
-- 6. TRIGGER EVALUATIONS
-- ============================================================

CREATE TABLE public.trigger_evaluations (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id           uuid NOT NULL,
    consensus_result_id uuid NOT NULL,
    outcome             public.trigger_outcome NOT NULL,
    reason              text,
    evaluated_at        timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fk_trigger_policy FOREIGN KEY (policy_id)
        REFERENCES public.policies (id) ON DELETE RESTRICT,
    CONSTRAINT fk_trigger_consensus FOREIGN KEY (consensus_result_id)
        REFERENCES public.consensus_results (id) ON DELETE RESTRICT,
    CONSTRAINT uq_trigger_evaluation UNIQUE (policy_id, consensus_result_id)
);

COMMENT ON TABLE public.trigger_evaluations IS 'Deterministic evaluation of a policy against a consensus event. Created by backend only.';

-- ============================================================
-- 7. WALLETS
-- ============================================================

CREATE TABLE public.wallets (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    policyholder_id   uuid NOT NULL,
    currency          text NOT NULL DEFAULT 'INR',
    balance_paise     bigint NOT NULL DEFAULT 0,
    status            public.wallet_status NOT NULL DEFAULT 'ACTIVE',
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fk_wallet_policyholder FOREIGN KEY (policyholder_id)
        REFERENCES public.policyholders (id) ON DELETE RESTRICT,
    CONSTRAINT uq_wallet_holder_currency UNIQUE (policyholder_id, currency),
    CONSTRAINT ck_wallet_balance_non_negative CHECK (balance_paise >= 0)
);

COMMENT ON TABLE public.wallets IS 'Synthetic demo wallet. Never implies a real bank account.';

-- ============================================================
-- 8. PAYOUTS
-- ============================================================

CREATE TABLE public.payouts (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id               uuid NOT NULL,
    trigger_evaluation_id   uuid NOT NULL,
    wallet_id               uuid NOT NULL,
    amount_paise            bigint NOT NULL,
    state                   public.payout_state NOT NULL DEFAULT 'PENDING',
    idempotency_scope       text NOT NULL,
    idempotency_key         text NOT NULL,
    provider_name           text,
    provider_reference      text,
    initiated_at            timestamptz,
    completed_at            timestamptz,
    created_at              timestamptz NOT NULL DEFAULT now(),
    updated_at              timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fk_payout_policy FOREIGN KEY (policy_id)
        REFERENCES public.policies (id) ON DELETE RESTRICT,
    CONSTRAINT fk_payout_trigger FOREIGN KEY (trigger_evaluation_id)
        REFERENCES public.trigger_evaluations (id) ON DELETE RESTRICT,
    CONSTRAINT fk_payout_wallet FOREIGN KEY (wallet_id)
        REFERENCES public.wallets (id) ON DELETE RESTRICT,
    CONSTRAINT ck_payout_amount_positive CHECK (amount_paise > 0),
    CONSTRAINT uq_payout_policy UNIQUE (policy_id),
    CONSTRAINT uq_payout_idempotency UNIQUE (idempotency_scope, idempotency_key)
);

COMMENT ON TABLE public.payouts IS 'Settlement intent and lifecycle. unique(policy_id) prevents double-pay. Never cascade-deleted.';

-- ============================================================
-- 9. WALLET TRANSACTIONS
-- ============================================================

CREATE TABLE public.wallet_transactions (
    id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id            uuid NOT NULL,
    payout_id            uuid NOT NULL,
    direction            public.transaction_direction NOT NULL,
    amount_paise         bigint NOT NULL,
    balance_before_paise bigint NOT NULL,
    balance_after_paise  bigint NOT NULL,
    created_at           timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fk_txn_wallet FOREIGN KEY (wallet_id)
        REFERENCES public.wallets (id) ON DELETE RESTRICT,
    CONSTRAINT fk_txn_payout FOREIGN KEY (payout_id)
        REFERENCES public.payouts (id) ON DELETE RESTRICT,
    CONSTRAINT ck_txn_amount_positive CHECK (amount_paise > 0),
    CONSTRAINT ck_txn_balance_before_non_negative CHECK (balance_before_paise >= 0),
    CONSTRAINT ck_txn_balance_after_non_negative CHECK (balance_after_paise >= 0),
    CONSTRAINT uq_txn_payout UNIQUE (payout_id)
);

COMMENT ON TABLE public.wallet_transactions IS 'Immutable wallet ledger. unique(payout_id) guarantees one transaction per payout.';

-- ============================================================
-- 10. AUDIT EVENTS
-- ============================================================

CREATE TABLE public.audit_events (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    correlation_id  uuid NOT NULL,
    entity_type     text NOT NULL,
    entity_id       uuid,
    event_type      text NOT NULL,
    actor           text NOT NULL,
    payload         jsonb NOT NULL DEFAULT '{}',
    occurred_at     timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_correlation
    ON public.audit_events (correlation_id, occurred_at);

CREATE INDEX idx_audit_entity
    ON public.audit_events (entity_type, entity_id, occurred_at);

COMMENT ON TABLE public.audit_events IS 'Immutable system evidence/audit trail. Never cascade-deleted.';

-- ============================================================
-- 11. ROW LEVEL SECURITY
-- ============================================================

-- Enable RLS on all tables.
-- Default: DENY ALL to anon. Only service_role (backend) can write financial tables.

ALTER TABLE public.policyholders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.micro_regions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weather_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trigger_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.telemetry_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.telemetry_validation_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consensus_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consensus_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trigger_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallet_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_events ENABLE ROW LEVEL SECURITY;

-- Read-only policies for authenticated users on reference/lookup tables
CREATE POLICY "Authenticated users can read policyholders"
    ON public.policyholders FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read micro_regions"
    ON public.micro_regions FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read weather_sources"
    ON public.weather_sources FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read trigger_rules"
    ON public.trigger_rules FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read policies"
    ON public.policies FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read telemetry_events"
    ON public.telemetry_events FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read telemetry_validation_results"
    ON public.telemetry_validation_results FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read consensus_results"
    ON public.consensus_results FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read consensus_members"
    ON public.consensus_members FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read trigger_evaluations"
    ON public.trigger_evaluations FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read wallets"
    ON public.wallets FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read payouts"
    ON public.payouts FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read wallet_transactions"
    ON public.wallet_transactions FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read audit_events"
    ON public.audit_events FOR SELECT TO authenticated USING (true);

-- Anon: read-only on non-financial reference data only
CREATE POLICY "Anon can read micro_regions"
    ON public.micro_regions FOR SELECT TO anon USING (true);

CREATE POLICY "Anon can read weather_sources"
    ON public.weather_sources FOR SELECT TO anon USING (true);

-- Service role bypasses RLS by default in Supabase.
-- No explicit write policies for anon or authenticated on financial tables.
-- This means: anon and authenticated CANNOT insert/update/delete on
-- policies, payouts, wallets, wallet_transactions, audit_events, etc.
-- Only the backend (using service_role key) can write to these tables.

-- ============================================================
-- 12. UPDATED_AT TRIGGER FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

-- Apply to tables with updated_at column
CREATE TRIGGER trg_policyholders_updated_at
    BEFORE UPDATE ON public.policyholders
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_micro_regions_updated_at
    BEFORE UPDATE ON public.micro_regions
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_weather_sources_updated_at
    BEFORE UPDATE ON public.weather_sources
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_policies_updated_at
    BEFORE UPDATE ON public.policies
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_wallets_updated_at
    BEFORE UPDATE ON public.wallets
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER trg_payouts_updated_at
    BEFORE UPDATE ON public.payouts
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

