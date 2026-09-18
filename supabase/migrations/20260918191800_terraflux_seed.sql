-- ============================================================
-- TerraFlux Seed Data
-- Migration: 20260918191800_terraflux_seed
--
-- Deterministic synthetic seed data for demo scenarios.
-- No real customer data. All IDs are fixed UUIDs for repeatability.
--
-- Uses INSERT ... ON CONFLICT DO NOTHING for safe re-runs.
-- ============================================================

-- ============================================================
-- 1. Synthetic Policyholder
-- ============================================================
INSERT INTO public.policyholders (id, display_name)
VALUES ('a1000000-0000-0000-0000-000000000001'::uuid, 'Ravi Kumar (Synthetic Farmer)')
ON CONFLICT (display_name) DO NOTHING;

-- ============================================================
-- 2. Micro-Region
-- ============================================================
INSERT INTO public.micro_regions (id, code, name, timezone)
VALUES ('b2000000-0000-0000-0000-000000000001'::uuid, 'KURNOOL-SYNTH-001', 'Kurnool Synthetic Micro-Region', 'Asia/Kolkata')
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- 3. Weather Sources (3 providers)
-- ============================================================
INSERT INTO public.weather_sources (id, code, kind) VALUES
    ('c3000000-0000-0000-0000-000000000001'::uuid, 'SYN-SRC-A', 'SYNTHETIC'),
    ('c3000000-0000-0000-0000-000000000002'::uuid, 'SYN-SRC-B', 'SYNTHETIC'),
    ('c3000000-0000-0000-0000-000000000003'::uuid, 'SYN-SRC-C', 'SYNTHETIC')
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- 4. Trigger Rule (canonical MVP rule)
--    rainfall >= 100 mm in 60-minute window, version 1
--    Payout: ₹10,000 (1,000,000 paise)
-- ============================================================
INSERT INTO public.trigger_rules (id, metric, operator, threshold_value, unit, window_minutes, version)
VALUES ('d4000000-0000-0000-0000-000000000001'::uuid, 'RAINFALL_MM', 'GTE', 100.0, 'mm', 60, 1)
ON CONFLICT (metric, operator, threshold_value, unit, window_minutes, version) DO NOTHING;

-- ============================================================
-- 5. Active Policy
--    Links holder → region → trigger rule
--    Payout amount: ₹10,000 = 1,000,000 paise
-- ============================================================
INSERT INTO public.policies (id, policyholder_id, region_id, trigger_rule_id, payout_amount_paise, status, start_at, end_at)
VALUES (
    'e5000000-0000-0000-0000-000000000001'::uuid,
    'a1000000-0000-0000-0000-000000000001'::uuid,
    'b2000000-0000-0000-0000-000000000001'::uuid,
    'd4000000-0000-0000-0000-000000000001'::uuid,
    1000000,
    'ACTIVE',
    '2026-01-01T00:00:00Z',
    '2027-01-01T00:00:00Z'
)
ON CONFLICT DO NOTHING;

-- ============================================================
-- 6. Synthetic Wallet
--    Starting balance: ₹0 (0 paise)
-- ============================================================
INSERT INTO public.wallets (id, policyholder_id, currency, balance_paise, status)
VALUES (
    'f6000000-0000-0000-0000-000000000001'::uuid,
    'a1000000-0000-0000-0000-000000000001'::uuid,
    'INR',
    0,
    'ACTIVE'
)
ON CONFLICT (policyholder_id, currency) DO NOTHING;

