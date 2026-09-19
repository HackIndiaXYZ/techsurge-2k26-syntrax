-- 1. policies
ALTER TABLE policies ADD COLUMN name text;
ALTER TABLE policies ADD COLUMN currency text;
ALTER TABLE policies ADD COLUMN valid_from timestamptz;
ALTER TABLE policies ADD COLUMN valid_until timestamptz;
ALTER TABLE policies ALTER COLUMN status TYPE text USING status::text;
ALTER TABLE policies ALTER COLUMN status DROP DEFAULT;

-- 2. trigger_rules
ALTER TABLE trigger_rules RENAME COLUMN operator TO threshold_operator;
ALTER TABLE trigger_rules ALTER COLUMN threshold_operator TYPE text USING threshold_operator::text;
ALTER TABLE trigger_rules RENAME COLUMN window_minutes TO observation_window_minutes;
ALTER TABLE trigger_rules ADD COLUMN consensus_quorum integer DEFAULT 2;
ALTER TABLE trigger_rules ADD COLUMN policy_id uuid REFERENCES policies(id) ON DELETE CASCADE;
ALTER TABLE trigger_rules ADD COLUMN consensus_tolerance double precision;

-- 3. consensus_results
ALTER TABLE consensus_results RENAME COLUMN state TO status;
ALTER TABLE consensus_results DROP CONSTRAINT IF EXISTS ck_consensus_value_when_achieved;
ALTER TABLE consensus_results ALTER COLUMN status TYPE text USING status::text;
ALTER TABLE consensus_results ALTER COLUMN status DROP DEFAULT;
ALTER TABLE consensus_results RENAME COLUMN value TO consensus_value_mm;
ALTER TABLE consensus_results ADD COLUMN policy_id uuid;
ALTER TABLE consensus_results ADD COLUMN median_all_sources_mm double precision;
ALTER TABLE consensus_results ADD COLUMN source_count_total integer DEFAULT 0;
ALTER TABLE consensus_results ADD COLUMN source_count_accepted integer DEFAULT 0;
ALTER TABLE consensus_results ADD COLUMN source_count_outliers integer DEFAULT 0;
ALTER TABLE consensus_results ADD COLUMN accepted_source_ids jsonb;
ALTER TABLE consensus_results ADD COLUMN outlier_source_ids jsonb;
ALTER TABLE consensus_results ADD COLUMN reason text;
ALTER TABLE consensus_results ADD CONSTRAINT ck_consensus_value_when_achieved CHECK (
    (status != 'ACHIEVED') OR (consensus_value_mm IS NOT NULL)
);

-- 4. wallets
ALTER TABLE wallets DROP CONSTRAINT IF EXISTS fk_wallet_policyholder;
ALTER TABLE wallets RENAME COLUMN policyholder_id TO policy_id;

-- Remap any wallet storing a policyholder_id to the corresponding policy's id
UPDATE wallets w
SET policy_id = p.id
FROM policies p
WHERE w.policy_id = p.policyholder_id;

UPDATE wallets
SET policy_id = 'e5000000-0000-0000-0000-000000000001'::uuid
WHERE id = 'f6000000-0000-0000-0000-000000000001'::uuid
  AND policy_id = 'a1000000-0000-0000-0000-000000000001'::uuid;

ALTER TABLE wallets ADD CONSTRAINT fk_wallet_policy FOREIGN KEY (policy_id) REFERENCES policies(id) ON DELETE RESTRICT;
ALTER TABLE wallets ALTER COLUMN status TYPE text USING status::text;
ALTER TABLE wallets ALTER COLUMN status DROP DEFAULT;

-- 5. audit_events
ALTER TABLE audit_events RENAME COLUMN payload TO metadata;
ALTER TABLE audit_events ADD COLUMN status text;
ALTER TABLE audit_events ADD COLUMN message text;
ALTER TABLE audit_events ADD COLUMN updated_at timestamptz;
ALTER TABLE audit_events ADD COLUMN created_at timestamptz DEFAULT now();

-- 6. trigger_evaluations
ALTER TABLE trigger_evaluations RENAME COLUMN outcome TO trigger_status;
ALTER TABLE trigger_evaluations ALTER COLUMN trigger_status TYPE text USING trigger_status::text;
ALTER TABLE trigger_evaluations ADD COLUMN consensus_value_mm double precision;
ALTER TABLE trigger_evaluations ADD COLUMN threshold_mm double precision;

-- 7. payouts
ALTER TABLE payouts RENAME COLUMN state TO status;
ALTER TABLE payouts ALTER COLUMN status TYPE text USING status::text;
ALTER TABLE payouts ALTER COLUMN status DROP DEFAULT;
ALTER TABLE payouts ADD COLUMN failure_reason text;
ALTER TABLE payouts ALTER COLUMN idempotency_scope DROP NOT NULL;
ALTER TABLE payouts ALTER COLUMN idempotency_key DROP NOT NULL;

-- 8. wallet_transactions
ALTER TABLE wallet_transactions ALTER COLUMN direction TYPE text USING direction::text;
ALTER TABLE wallet_transactions ALTER COLUMN direction DROP NOT NULL;

-- 9. telemetry_events
ALTER TABLE telemetry_events ALTER COLUMN validation_state TYPE text USING validation_state::text;
