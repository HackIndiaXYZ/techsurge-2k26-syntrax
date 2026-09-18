// ============================================================
// TERRAFLUX Domain Types
// These types match the backend API contract exactly.
// The frontend NEVER calculates consensus, trigger, or payout.
// ============================================================

export type PolicyStatus = "DRAFT" | "ACTIVE" | "TRIGGERED" | "PAID" | "EXPIRED" | "CANCELLED";
export type ConsensusState = "PENDING" | "ACHIEVED" | "NO_CONSENSUS" | "EXPIRED";
export type TriggerState = "TRIGGERED" | "NOT_MET" | "NOT_ELIGIBLE" | "NO_CONSENSUS" | "ALREADY_TRIGGERED" | "EXPIRED";
export type SettlementStatus = "PENDING" | "TRIGGERED" | "SETTLED" | "DUPLICATE" | "BLOCKED" | "FAILED";
export type RazorpayXStatus = "PROCESSED" | "PENDING" | "FAILED" | "UNAVAILABLE";
export type SourceValidationStatus = "VALID" | "OUTLIER" | "IMPOSSIBLE_VALUE" | "STALE" | "FUTURE_TIMESTAMP" | "SOURCE_DISAGREEMENT";
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

export type AiLanguage = "en" | "hi" | "te";

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

export interface WeatherMetrics {
  rainfall_mm: number;
  temperature_c: number;
  humidity_percent: number;
  wind_speed_kmh: number;
  wind_direction_deg: number;
  pressure_hpa: number;
}

export interface WeatherSource {
  id: string;
  name: string;
  metrics: WeatherMetrics;
  observed_at: string;
  validation_status: SourceValidationStatus;
  is_in_consensus_group: boolean;
}

export interface Consensus {
  state: ConsensusState;
  value: number | null; // This is specifically for the primary metric (rainfall)
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
  external_payout_status: RazorpayXStatus;
  external_reference: string | null;
}

export interface WalletTransaction {
  id: string;
  type: "CREDIT" | "BLOCKED" | "INFO";
  amount_paise: number;
  event_id: string;
  description: string;
  timestamp: string;
  status: string;
}

export interface Wallet {
  wallet_id: string;
  balance_paise: number;
  currency: string;
  last_credit_paise: number | null;
  last_transaction_id: string | null;
  transactions: WalletTransaction[];
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
  explanations: Record<AiLanguage, string>;
  anomaly_explanation: string | null;
  tts_available: boolean;
}

// Time-series data points for charts
export interface TimeSeriesPoint {
  time: string;
  source_a: number;
  source_b: number;
  source_c: number;
  consensus: number | null;
}

export interface DashboardData {
  scenario: ScenarioId;
  policy: Policy;
  consensus: Consensus;
  trigger: TriggerEvaluation;
  settlement: Settlement;
  wallet: Wallet;
  audit: AuditEvent[];
  ai_insight: AiInsight | null;
  history: {
    rainfall: TimeSeriesPoint[];
    temperature: TimeSeriesPoint[];
  };
  event_list: {
    id: string;
    timestamp: string;
    consensus_value: number | null;
    decision: string;
    settlement_amount: number;
    status: string;
  }[];
}

// Demo Scenarios
export type ScenarioId = "normal" | "corrupted-source" | "no-consensus" | "duplicate-settlement";

export interface ScenarioMeta {
  id: ScenarioId;
  label: string;
  description: string;
}

export const SCENARIOS: ScenarioMeta[] = [
  { id: "normal", label: "Normal Event", description: "All sources valid. Trust pipeline completes." },
  { id: "corrupted-source", label: "Corrupted Source", description: "One outlier rejected. Consensus still achieved." },
  { id: "no-consensus", label: "No Consensus", description: "Insufficient agreement. Settlement blocked safely." },
  { id: "duplicate-settlement", label: "Duplicate Settlement", description: "Replay detected. Idempotency prevents double payout." },
];

export function formatPaise(paise: number, currency: string = "INR"): string {
  const amount = paise / 100;
  if (currency === "INR") {
    return `₹${amount.toLocaleString("en-IN")}`;
  }
  return `${currency} ${amount.toLocaleString()}`;
}
