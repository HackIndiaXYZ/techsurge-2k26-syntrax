// ============================================================
// SYNTRAX Domain Types — derived from docs/architecture/API_CONTRACTS.md
// These types match the backend API contract exactly.
// The frontend NEVER calculates consensus, trigger, or payout.
// ============================================================

/** Policy lifecycle status */
export type PolicyStatus = "DRAFT" | "ACTIVE" | "TRIGGERED" | "PAID" | "EXPIRED" | "CANCELLED";

/** Consensus state as determined by the backend */
export type ConsensusState = "PENDING" | "ACHIEVED" | "NO_CONSENSUS" | "EXPIRED";

/** Trigger evaluation result from the backend */
export type TriggerState =
  | "TRIGGERED"
  | "NOT_MET"
  | "NOT_ELIGIBLE"
  | "NO_CONSENSUS"
  | "ALREADY_TRIGGERED"
  | "EXPIRED";

/** Settlement status */
export type SettlementStatus = "PENDING" | "TRIGGERED" | "SETTLED" | "DUPLICATE" | "BLOCKED" | "FAILED";

/** Validation status for a weather source reading */
export type SourceValidationStatus = "VALID" | "OUTLIER" | "IMPOSSIBLE_VALUE" | "STALE" | "FUTURE_TIMESTAMP" | "SOURCE_DISAGREEMENT";

/** Audit event types across the full lifecycle */
export type AuditEventType =
  | "TELEMETRY_RECEIVED"
  | "TELEMETRY_VALIDATED"
  | "TELEMETRY_REJECTED"
  | "CONSENSUS_ACHIEVED"
  | "CONSENSUS_FAILED"
  | "POLICY_TRIGGERED"
  | "POLICY_NOT_MET"
  | "SETTLEMENT_INITIATED"
  | "SETTLEMENT_EXECUTED"
  | "SETTLEMENT_DUPLICATE"
  | "SETTLEMENT_FAILED"
  | "WALLET_CREDITED"
  | "NOTIFICATION_SENT";

// ---- API Response Models ----

export interface Policy {
  id: string;
  policyholder: string;
  policyholder_id: string;
  region_id: string;
  region_name: string;
  metric: string;
  trigger_rule: string;
  threshold: number;
  window_minutes: number;
  payout_amount_paise: number;
  currency: string;
  status: PolicyStatus;
  starts_at: string;
  ends_at: string;
}

export interface WeatherSource {
  id: string;
  name: string;
  value: number;
  unit: string;
  observed_at: string;
  validation_status: SourceValidationStatus;
  is_in_consensus_group: boolean;
}

export interface Consensus {
  state: ConsensusState;
  value: number | null;
  quorum_required: number;
  quorum_met: boolean;
  agreeing_sources: number;
  total_sources: number;
  sources: WeatherSource[];
  window_start: string;
  window_end: string;
}

export interface TriggerEvaluation {
  state: TriggerState;
  observed_value: number | null;
  threshold: number;
  reason: string;
  evaluated_at: string;
  policy_id: string;
  trigger_rule_id: string;
}

export interface Settlement {
  payout_id: string;
  status: SettlementStatus;
  payout_amount_paise: number;
  currency: string;
  idempotency_key: string;
  transaction_id: string | null;
  executed_at: string | null;
  is_duplicate: boolean;
}

export interface Wallet {
  wallet_id: string;
  balance_paise: number;
  currency: string;
  last_credit_paise: number | null;
  last_transaction_id: string | null;
}

export interface AuditEvent {
  id: string;
  type: AuditEventType;
  detail: string;
  timestamp: string;
  correlation_id: string;
  actor: string;
}

export interface AiInsight {
  summary: string;
  anomaly_explanation: string | null;
  local_language_note: string | null;
}

/** The full dashboard response shape — matches GET /v1/dashboard */
export interface DashboardData {
  scenario: ScenarioId;
  policy: Policy;
  consensus: Consensus;
  trigger: TriggerEvaluation;
  settlement: Settlement;
  wallet: Wallet;
  audit: AuditEvent[];
  ai_insight: AiInsight | null;
}

// ---- Demo Scenarios ----

export type ScenarioId = "normal" | "corrupted-source" | "no-consensus" | "duplicate-settlement";

export interface ScenarioMeta {
  id: ScenarioId;
  label: string;
  description: string;
}

export const SCENARIOS: ScenarioMeta[] = [
  {
    id: "normal",
    label: "Normal Success",
    description: "All 3 sources agree. Consensus achieved, trigger fires, settlement executes.",
  },
  {
    id: "corrupted-source",
    label: "Corrupted Source",
    description: "Source C is an outlier. A and B still form consensus. System continues safely.",
  },
  {
    id: "no-consensus",
    label: "No Consensus",
    description: "All 3 sources disagree. No quorum. Settlement is blocked.",
  },
  {
    id: "duplicate-settlement",
    label: "Duplicate Settlement",
    description: "Settlement replayed. Idempotency prevents double payout.",
  },
];

// ---- Helper: format paise as INR display string ----

export function formatPaise(paise: number, currency: string = "INR"): string {
  const amount = paise / 100;
  if (currency === "INR") {
    return `₹${amount.toLocaleString("en-IN")}`;
  }
  return `${currency} ${amount.toLocaleString()}`;
}

