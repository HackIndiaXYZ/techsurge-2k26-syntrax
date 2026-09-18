// ============================================================
// SYNTRAX Mock Data Fixtures — deterministic demo scenarios
// Each fixture returns the exact DashboardData shape.
// The frontend consumes these identically to a real backend.
// ============================================================

import type { DashboardData, ScenarioId } from "./types";

const NOW = "2026-09-18T10:30:00Z";
const WINDOW_START = "2026-09-18T09:30:00Z";
const WINDOW_END = "2026-09-18T10:30:00Z";
const CORRELATION = "corr-demo-001";

// ---- Shared policy (identical across all scenarios) ----

const BASE_POLICY: DashboardData["policy"] = {
  id: "pol-syn-777",
  policyholder: "Kisan Demo User",
  policyholder_id: "ph-demo-001",
  region_id: "reg-ind-mh-001",
  region_name: "Pune Rural (Synthetic)",
  metric: "RAINFALL_MM",
  trigger_rule: "RAINFALL_MM >= 100",
  threshold: 100,
  window_minutes: 60,
  payout_amount_paise: 1000000,
  currency: "INR",
  status: "ACTIVE",
  starts_at: "2026-09-18T00:00:00Z",
  ends_at: "2026-09-19T00:00:00Z",
};

// ---- SCENARIO 1: Normal Success ----

const normalScenario: DashboardData = {
  scenario: "normal",
  policy: { ...BASE_POLICY, status: "TRIGGERED" },
  consensus: {
    state: "ACHIEVED",
    value: 102,
    quorum_required: 2,
    quorum_met: true,
    agreeing_sources: 3,
    total_sources: 3,
    window_start: WINDOW_START,
    window_end: WINDOW_END,
    sources: [
      { id: "SRC-A", name: "Weather Station Alpha", value: 103, unit: "mm", observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
      { id: "SRC-B", name: "Weather Station Beta", value: 101, unit: "mm", observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
      { id: "SRC-C", name: "Weather Station Gamma", value: 102, unit: "mm", observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
    ],
  },
  trigger: {
    state: "TRIGGERED",
    observed_value: 102,
    threshold: 100,
    reason: "Consensus value (102 mm) >= Threshold (100 mm)",
    evaluated_at: NOW,
    policy_id: "pol-syn-777",
    trigger_rule_id: "rule-rainfall-v1",
  },
  settlement: {
    payout_id: "pay-001",
    status: "SETTLED",
    payout_amount_paise: 1000000,
    currency: "INR",
    idempotency_key: "idem-pay-001-v1",
    transaction_id: "txn-synth-88001",
    executed_at: NOW,
    is_duplicate: false,
  },
  wallet: {
    wallet_id: "wal-demo-001",
    balance_paise: 1000000,
    currency: "INR",
    last_credit_paise: 1000000,
    last_transaction_id: "txn-synth-88001",
  },
  audit: [
    { id: "a1", type: "TELEMETRY_RECEIVED", detail: "Source Alpha reported 103 mm", timestamp: "2026-09-18T10:25:00Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "a2", type: "TELEMETRY_RECEIVED", detail: "Source Beta reported 101 mm", timestamp: "2026-09-18T10:25:01Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "a3", type: "TELEMETRY_RECEIVED", detail: "Source Gamma reported 102 mm", timestamp: "2026-09-18T10:25:02Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "a4", type: "TELEMETRY_VALIDATED", detail: "All 3 readings validated (0–400 mm, not stale, not future)", timestamp: "2026-09-18T10:25:03Z", correlation_id: CORRELATION, actor: "validation-service" },
    { id: "a5", type: "CONSENSUS_ACHIEVED", detail: "3/3 sources agree (max diff ≤ 5 mm). Median = 102 mm", timestamp: "2026-09-18T10:25:04Z", correlation_id: CORRELATION, actor: "consensus-engine" },
    { id: "a6", type: "POLICY_TRIGGERED", detail: "102 mm >= 100 mm threshold — policy triggered", timestamp: "2026-09-18T10:25:05Z", correlation_id: CORRELATION, actor: "trigger-engine" },
    { id: "a7", type: "SETTLEMENT_EXECUTED", detail: "₹10,000 settled to synthetic wallet (idem-pay-001-v1)", timestamp: "2026-09-18T10:25:06Z", correlation_id: CORRELATION, actor: "settlement-service" },
    { id: "a8", type: "WALLET_CREDITED", detail: "Wallet wal-demo-001 credited ₹10,000. Balance: ₹10,000", timestamp: "2026-09-18T10:25:07Z", correlation_id: CORRELATION, actor: "wallet-service" },
  ],
  ai_insight: {
    summary: "All three weather stations reported consistent heavy rainfall between 101–103 mm within the 60-minute window. Consensus was achieved unanimously. The policy trigger condition was met, and settlement was executed successfully.",
    anomaly_explanation: null,
    local_language_note: "भारी बारिश की पुष्टि — बीमा राशि आपके वॉलेट में जमा हो गई है।",
  },
};

// ---- SCENARIO 2: Corrupted / Outlier Source ----

const corruptedSourceScenario: DashboardData = {
  scenario: "corrupted-source",
  policy: { ...BASE_POLICY, status: "TRIGGERED" },
  consensus: {
    state: "ACHIEVED",
    value: 102,
    quorum_required: 2,
    quorum_met: true,
    agreeing_sources: 2,
    total_sources: 3,
    window_start: WINDOW_START,
    window_end: WINDOW_END,
    sources: [
      { id: "SRC-A", name: "Weather Station Alpha", value: 103, unit: "mm", observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
      { id: "SRC-B", name: "Weather Station Beta", value: 101, unit: "mm", observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
      { id: "SRC-C", name: "Weather Station Gamma", value: 7, unit: "mm", observed_at: NOW, validation_status: "OUTLIER", is_in_consensus_group: false },
    ],
  },
  trigger: {
    state: "TRIGGERED",
    observed_value: 102,
    threshold: 100,
    reason: "Consensus value (102 mm) >= Threshold (100 mm). Source Gamma excluded as outlier.",
    evaluated_at: NOW,
    policy_id: "pol-syn-777",
    trigger_rule_id: "rule-rainfall-v1",
  },
  settlement: {
    payout_id: "pay-002",
    status: "SETTLED",
    payout_amount_paise: 1000000,
    currency: "INR",
    idempotency_key: "idem-pay-002-v1",
    transaction_id: "txn-synth-88002",
    executed_at: NOW,
    is_duplicate: false,
  },
  wallet: {
    wallet_id: "wal-demo-001",
    balance_paise: 1000000,
    currency: "INR",
    last_credit_paise: 1000000,
    last_transaction_id: "txn-synth-88002",
  },
  audit: [
    { id: "b1", type: "TELEMETRY_RECEIVED", detail: "Source Alpha reported 103 mm", timestamp: "2026-09-18T10:25:00Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "b2", type: "TELEMETRY_RECEIVED", detail: "Source Beta reported 101 mm", timestamp: "2026-09-18T10:25:01Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "b3", type: "TELEMETRY_RECEIVED", detail: "Source Gamma reported 7 mm", timestamp: "2026-09-18T10:25:02Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "b4", type: "TELEMETRY_VALIDATED", detail: "Alpha, Beta validated. Gamma flagged: value 7 mm is >5 mm deviation from group", timestamp: "2026-09-18T10:25:03Z", correlation_id: CORRELATION, actor: "validation-service" },
    { id: "b5", type: "TELEMETRY_REJECTED", detail: "Source Gamma (7 mm) classified as OUTLIER — excluded from consensus", timestamp: "2026-09-18T10:25:03Z", correlation_id: CORRELATION, actor: "consensus-engine" },
    { id: "b6", type: "CONSENSUS_ACHIEVED", detail: "2/3 sources agree (Alpha 103, Beta 101). Median = 102 mm", timestamp: "2026-09-18T10:25:04Z", correlation_id: CORRELATION, actor: "consensus-engine" },
    { id: "b7", type: "POLICY_TRIGGERED", detail: "102 mm >= 100 mm threshold — policy triggered", timestamp: "2026-09-18T10:25:05Z", correlation_id: CORRELATION, actor: "trigger-engine" },
    { id: "b8", type: "SETTLEMENT_EXECUTED", detail: "₹10,000 settled to synthetic wallet (idem-pay-002-v1)", timestamp: "2026-09-18T10:25:06Z", correlation_id: CORRELATION, actor: "settlement-service" },
    { id: "b9", type: "WALLET_CREDITED", detail: "Wallet wal-demo-001 credited ₹10,000. Balance: ₹10,000", timestamp: "2026-09-18T10:25:07Z", correlation_id: CORRELATION, actor: "wallet-service" },
  ],
  ai_insight: {
    summary: "Two of three weather stations reported heavy rainfall (101–103 mm). Station Gamma reported only 7 mm — a significant deviation. The system correctly identified Gamma as an outlier and excluded it from consensus. The remaining two sources met the quorum requirement.",
    anomaly_explanation: "Station Gamma's reading of 7 mm differs from Alpha (103 mm) and Beta (101 mm) by more than the 5 mm tolerance. This may indicate a sensor malfunction, communication error, or localized microclimate effect. The reading was retained for audit but excluded from the consensus calculation.",
    local_language_note: "एक सेंसर ने गलत रीडिंग दी — सिस्टम ने उसे पहचान कर अलग कर दिया। बाकी दो सेंसर सहमत हैं।",
  },
};

// ---- SCENARIO 3: No Consensus ----

const noConsensusScenario: DashboardData = {
  scenario: "no-consensus",
  policy: { ...BASE_POLICY },
  consensus: {
    state: "NO_CONSENSUS",
    value: null,
    quorum_required: 2,
    quorum_met: false,
    agreeing_sources: 0,
    total_sources: 3,
    window_start: WINDOW_START,
    window_end: WINDOW_END,
    sources: [
      { id: "SRC-A", name: "Weather Station Alpha", value: 120, unit: "mm", observed_at: NOW, validation_status: "SOURCE_DISAGREEMENT", is_in_consensus_group: false },
      { id: "SRC-B", name: "Weather Station Beta", value: 50, unit: "mm", observed_at: NOW, validation_status: "SOURCE_DISAGREEMENT", is_in_consensus_group: false },
      { id: "SRC-C", name: "Weather Station Gamma", value: 5, unit: "mm", observed_at: NOW, validation_status: "SOURCE_DISAGREEMENT", is_in_consensus_group: false },
    ],
  },
  trigger: {
    state: "NO_CONSENSUS",
    observed_value: null,
    threshold: 100,
    reason: "No consensus achieved — all sources disagree beyond 5 mm tolerance. Settlement not authorized.",
    evaluated_at: NOW,
    policy_id: "pol-syn-777",
    trigger_rule_id: "rule-rainfall-v1",
  },
  settlement: {
    payout_id: "pay-003",
    status: "BLOCKED",
    payout_amount_paise: 0,
    currency: "INR",
    idempotency_key: "",
    transaction_id: null,
    executed_at: null,
    is_duplicate: false,
  },
  wallet: {
    wallet_id: "wal-demo-001",
    balance_paise: 0,
    currency: "INR",
    last_credit_paise: null,
    last_transaction_id: null,
  },
  audit: [
    { id: "c1", type: "TELEMETRY_RECEIVED", detail: "Source Alpha reported 120 mm", timestamp: "2026-09-18T10:25:00Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "c2", type: "TELEMETRY_RECEIVED", detail: "Source Beta reported 50 mm", timestamp: "2026-09-18T10:25:01Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "c3", type: "TELEMETRY_RECEIVED", detail: "Source Gamma reported 5 mm", timestamp: "2026-09-18T10:25:02Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "c4", type: "TELEMETRY_VALIDATED", detail: "All readings are within valid range (0–400 mm)", timestamp: "2026-09-18T10:25:03Z", correlation_id: CORRELATION, actor: "validation-service" },
    { id: "c5", type: "CONSENSUS_FAILED", detail: "No pair of sources within 5 mm tolerance. Alpha=120, Beta=50, Gamma=5", timestamp: "2026-09-18T10:25:04Z", correlation_id: CORRELATION, actor: "consensus-engine" },
    { id: "c6", type: "POLICY_NOT_MET", detail: "No trusted value available — trigger evaluation cannot proceed", timestamp: "2026-09-18T10:25:05Z", correlation_id: CORRELATION, actor: "trigger-engine" },
  ],
  ai_insight: {
    summary: "All three weather stations reported dramatically different rainfall values (120 mm, 50 mm, 5 mm). No pair of readings falls within the 5 mm agreement threshold. Without consensus, the system cannot produce a trusted weather value, and the policy trigger cannot be evaluated. Settlement is blocked as a safety measure.",
    anomaly_explanation: "The extreme disagreement between all three sources may indicate widespread sensor issues, a highly localized weather event, or communication corruption. Manual investigation may be warranted.",
    local_language_note: "तीनों सेंसर अलग-अलग रीडिंग दे रहे हैं — भुगतान सुरक्षित रूप से रोक दिया गया है।",
  },
};

// ---- SCENARIO 4: Duplicate / Replay Settlement ----

const duplicateSettlementScenario: DashboardData = {
  scenario: "duplicate-settlement",
  policy: { ...BASE_POLICY, status: "PAID" },
  consensus: {
    state: "ACHIEVED",
    value: 102,
    quorum_required: 2,
    quorum_met: true,
    agreeing_sources: 3,
    total_sources: 3,
    window_start: WINDOW_START,
    window_end: WINDOW_END,
    sources: [
      { id: "SRC-A", name: "Weather Station Alpha", value: 103, unit: "mm", observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
      { id: "SRC-B", name: "Weather Station Beta", value: 101, unit: "mm", observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
      { id: "SRC-C", name: "Weather Station Gamma", value: 102, unit: "mm", observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
    ],
  },
  trigger: {
    state: "ALREADY_TRIGGERED",
    observed_value: 102,
    threshold: 100,
    reason: "Policy already triggered and settled. Re-evaluation confirms original decision.",
    evaluated_at: NOW,
    policy_id: "pol-syn-777",
    trigger_rule_id: "rule-rainfall-v1",
  },
  settlement: {
    payout_id: "pay-001",
    status: "DUPLICATE",
    payout_amount_paise: 1000000,
    currency: "INR",
    idempotency_key: "idem-pay-001-v1",
    transaction_id: "txn-synth-88001",
    executed_at: "2026-09-18T10:25:06Z",
    is_duplicate: true,
  },
  wallet: {
    wallet_id: "wal-demo-001",
    balance_paise: 1000000,
    currency: "INR",
    last_credit_paise: 1000000,
    last_transaction_id: "txn-synth-88001",
  },
  audit: [
    { id: "d1", type: "TELEMETRY_RECEIVED", detail: "Source Alpha reported 103 mm", timestamp: "2026-09-18T10:25:00Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "d2", type: "TELEMETRY_RECEIVED", detail: "Source Beta reported 101 mm", timestamp: "2026-09-18T10:25:01Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "d3", type: "TELEMETRY_RECEIVED", detail: "Source Gamma reported 102 mm", timestamp: "2026-09-18T10:25:02Z", correlation_id: CORRELATION, actor: "ingestion-service" },
    { id: "d4", type: "CONSENSUS_ACHIEVED", detail: "3/3 sources agree. Median = 102 mm", timestamp: "2026-09-18T10:25:04Z", correlation_id: CORRELATION, actor: "consensus-engine" },
    { id: "d5", type: "POLICY_TRIGGERED", detail: "102 mm >= 100 mm threshold — policy triggered", timestamp: "2026-09-18T10:25:05Z", correlation_id: CORRELATION, actor: "trigger-engine" },
    { id: "d6", type: "SETTLEMENT_EXECUTED", detail: "₹10,000 settled to synthetic wallet (idem-pay-001-v1)", timestamp: "2026-09-18T10:25:06Z", correlation_id: CORRELATION, actor: "settlement-service" },
    { id: "d7", type: "WALLET_CREDITED", detail: "Wallet wal-demo-001 credited ₹10,000. Balance: ₹10,000", timestamp: "2026-09-18T10:25:07Z", correlation_id: CORRELATION, actor: "wallet-service" },
    { id: "d8", type: "SETTLEMENT_DUPLICATE", detail: "Duplicate execute request received with same idempotency key (idem-pay-001-v1). Original settlement returned. No additional payout.", timestamp: "2026-09-18T10:26:00Z", correlation_id: CORRELATION, actor: "settlement-service" },
  ],
  ai_insight: {
    summary: "A duplicate settlement request was received. The system detected the same idempotency key (idem-pay-001-v1) and returned the original settlement result without executing a second payout. The wallet balance remains unchanged at ₹10,000.",
    anomaly_explanation: "Duplicate settlement requests can occur due to network retries, client-side double-clicks, or replayed API calls. The idempotency mechanism ensures the payout is executed exactly once.",
    local_language_note: "डुप्लीकेट अनुरोध आया — सिस्टम ने इसे पहचान लिया। पहले से जमा राशि में कोई बदलाव नहीं।",
  },
};

// ---- Scenario lookup ----

const SCENARIO_DATA: Record<ScenarioId, DashboardData> = {
  normal: normalScenario,
  "corrupted-source": corruptedSourceScenario,
  "no-consensus": noConsensusScenario,
  "duplicate-settlement": duplicateSettlementScenario,
};

export function getScenarioData(scenario: ScenarioId): DashboardData {
  return SCENARIO_DATA[scenario];
}

