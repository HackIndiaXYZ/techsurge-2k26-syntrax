// =============================================================================
// TerraFlux TypeScript Types — Matches backend Pydantic schemas exactly
// =============================================================================

// ── Health ───────────────────────────────────────────────────────────────────
export interface HealthResponse {
  status: 'ok' | 'degraded';
  environment: string;
  database: 'connected' | 'error';
}

// ── Weather Sources ─────────────────────────────────────────────────────────
export interface WeatherSource {
  name: string;
  status: 'ONLINE' | 'OFFLINE' | 'DEGRADED' | 'UNKNOWN';
  latency_ms: number;
}

export interface PollResponse {
  status: string;
  message: string;
}

// ── Simulation Request ──────────────────────────────────────────────────────
export type SimulationScenario =
  | 'NORMAL'
  | 'CORRUPTED_SOURCE'
  | 'NO_CONSENSUS'
  | 'DUPLICATE_REPLAY'
  | 'BELOW_THRESHOLD';

export interface ObservationInput {
  source_id: string;
  value: number;
}

export interface SimulationRequest {
  scenario: SimulationScenario;
  policy_id: string;
  region_id: string;
  observations: ObservationInput[];
  observed_at: string; // ISO 8601
}

// ── Simulation Response (full pipeline result) ──────────────────────────────
export interface ObservationResult {
  source_id: string;
  value: number;
  status: 'ACCEPTED' | 'REJECTED' | 'DUPLICATE';
  rejection_reason: string | null;
}

export interface TelemetryResult {
  submitted: number;
  accepted: number;
  rejected: number;
  duplicates: number;
  observations: ObservationResult[];
}

export interface ConsensusResult {
  status: 'REACHED' | 'NO_CONSENSUS';
  median_all_sources: number | null;
  consensus_value_mm: number | null;
  accepted_sources: string[];
  outlier_sources: string[];
  reason: string | null;
}

export interface TriggerResult {
  status: 'TRIGGERED' | 'NOT_TRIGGERED' | 'TRIGGER_BLOCKED_NO_CONSENSUS';
  threshold_mm: number;
  consensus_value_mm: number | null;
  reason: string;
}

export interface SettlementResult {
  status: 'SUCCESS' | 'DUPLICATE' | 'SKIPPED' | 'FAILED';
  payout_id: string | null;
  idempotency_status: 'NEW' | 'ALREADY_SETTLED' | null;
  payout_amount_paise: number | null;
  payout_amount_inr_display: string | null;
  reason: string | null;
}

export interface WalletSimResult {
  wallet_id: string | null;
  balance_before_paise: number | null;
  balance_after_paise: number | null;
  credited: boolean;
}

export interface LatencyResult {
  observed_at: string;
  received_at: string;
  trigger_evaluated_at: string | null;
  payout_completed_at: string | null;
  detection_latency_ms: number | null;
  settlement_latency_ms: number | null;
  end_to_end_latency_ms: number | null;
}

export interface SimulationResponse {
  correlation_id: string;
  scenario: string;
  policy_id: string;
  telemetry: TelemetryResult;
  consensus: ConsensusResult;
  trigger: TriggerResult;
  settlement: SettlementResult;
  wallet: WalletSimResult;
  audit_id: string | null;
  latency: LatencyResult | null;
  ai_event: Record<string, unknown> | null;
}

// ── Policy ──────────────────────────────────────────────────────────────────
export interface PolicyResponse {
  policy_id: string;
  region_id: string;
  name: string;
  status: string;
  trigger_metric: string;
  trigger_threshold_mm: number;
  trigger_operator: string;
  observation_window_minutes: number;
  payout_amount_paise: number;
  payout_amount_inr_display: string;
  currency: string;
  valid_from: string | null;
  valid_until: string | null;
}

// ── Wallet ──────────────────────────────────────────────────────────────────
export interface WalletTransactionResponse {
  transaction_id: string;
  payout_id: string;
  amount_paise: number;
  balance_before_paise: number;
  balance_after_paise: number;
  created_at: string;
}

export interface WalletResponse {
  wallet_id: string;
  policy_id: string;
  balance_paise: number;
  balance_inr_display: string;
  currency: string;
  transactions: WalletTransactionResponse[];
}

// ── Payout ──────────────────────────────────────────────────────────────────
export interface PayoutResponse {
  payout_id: string;
  policy_id: string;
  trigger_evaluation_id: string;
  status: string;
  amount_paise: number;
  amount_inr_display: string;
  idempotency_key: string;
  failure_reason: string | null;
  created_at: string;
}

// ── Audit ────────────────────────────────────────────────────────────────────
export interface AuditEventResponse {
  audit_id: string;
  event_type: string;
  entity_type: string;
  entity_id: string;
  policy_id: string | null;
  correlation_id: string | null;
  status: string;
  message: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface AuditListResponse {
  policy_id: string;
  total: number;
  events: AuditEventResponse[];
}

// ── API Error ───────────────────────────────────────────────────────────────
export interface ApiErrorDetail {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

export class ApiError extends Error {
  status: number;
  detail: ApiErrorDetail | null;

  constructor(status: number, detail: ApiErrorDetail | null, message?: string) {
    super(message || detail?.message || `API error ${status}`);
    this.status = status;
    this.detail = detail;
    this.name = 'ApiError';
  }
}
