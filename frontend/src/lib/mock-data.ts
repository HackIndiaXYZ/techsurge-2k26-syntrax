// ============================================================
// TERRAFLUX Mock Data Fixtures
// ============================================================

import type { DashboardData, ScenarioId, WeatherMetrics } from "./types";

const NOW = "2026-08-25T14:32:04Z";
const WINDOW_START = "2026-08-25T13:32:00Z";
const WINDOW_END = "2026-08-25T14:32:00Z";
const CORRELATION = "EVT-1042";

const BASE_POLICY: DashboardData["policy"] = {
  id: "SYN-F03-001",
  policyholder: "Sanju",
  policyholder_id: "ph-001",
  region_id: "reg-hyd",
  region_name: "Hyderabad (Synthetic Micro-Region)",
  metric: "RAINFALL_MM",
  trigger_rule: "≥ 100 mm / 60 minutes",
  threshold: 100,
  window_minutes: 60,
  payout_amount_paise: 1000000,
  currency: "INR",
  status: "ACTIVE",
  starts_at: "2025-01-01T00:00:00Z",
  ends_at: "2025-12-31T23:59:59Z",
};

const BASE_METRICS: WeatherMetrics = {
  rainfall_mm: 0,
  temperature_c: 28.5,
  humidity_percent: 85,
  wind_speed_kmh: 12,
  wind_direction_deg: 180,
  pressure_hpa: 1002,
};

const EVENT_LIST = [
  { id: "EVT-1042", timestamp: "2026-08-25T14:32:04Z", consensus_value: 102, decision: "Triggered", settlement_amount: 1000000, status: "Settled" },
  { id: "EVT-1041", timestamp: "2026-08-25T13:58:11Z", consensus_value: 74, decision: "Below threshold", settlement_amount: 0, status: "—" },
  { id: "EVT-1040", timestamp: "2026-08-25T13:21:32Z", consensus_value: null, decision: "No consensus", settlement_amount: 0, status: "—" },
];

const HISTORY_NORMAL = [
  { time: "13:40", source_a: 20, source_b: 22, source_c: 21, consensus: 21 },
  { time: "13:50", source_a: 45, source_b: 44, source_c: 46, consensus: 45 },
  { time: "14:00", source_a: 60, source_b: 58, source_c: 59, consensus: 59 },
  { time: "14:10", source_a: 85, source_b: 82, source_c: 84, consensus: 84 },
  { time: "14:20", source_a: 98, source_b: 95, source_c: 97, consensus: 97 },
  { time: "14:30", source_a: 110, source_b: 108, source_c: 111, consensus: 110 },
];

const HISTORY_CORRUPTED = [
  { time: "13:40", source_a: 20, source_b: 22, source_c: 19, consensus: 20 },
  { time: "13:50", source_a: 45, source_b: 44, source_c: 40, consensus: 44 },
  { time: "14:00", source_a: 60, source_b: 58, source_c: 6, consensus: 59 },
  { time: "14:10", source_a: 85, source_b: 82, source_c: 7, consensus: 83.5 },
  { time: "14:20", source_a: 98, source_b: 95, source_c: 7, consensus: 96.5 },
  { time: "14:30", source_a: 110, source_b: 108, source_c: 7, consensus: 109 },
];

const normalScenario: DashboardData = {
  scenario: "normal",
  policy: { ...BASE_POLICY, status: "TRIGGERED" },
  consensus: {
    state: "ACHIEVED",
    value: 110,
    quorum_required: 2,
    quorum_met: true,
    agreeing_sources: 3,
    total_sources: 3,
    window_start: WINDOW_START,
    window_end: WINDOW_END,
    sources: [
      { id: "SRC-A", name: "IMD", metrics: { ...BASE_METRICS, rainfall_mm: 110 }, observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
      { id: "SRC-B", name: "OpenWeather", metrics: { ...BASE_METRICS, rainfall_mm: 108 }, observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
      { id: "SRC-C", name: "Community", metrics: { ...BASE_METRICS, rainfall_mm: 111 }, observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
    ],
  },
  trigger: {
    state: "TRIGGERED",
    observed_value: 110,
    threshold: 100,
    reason: "Policy conditions met",
    evaluated_at: NOW,
    policy_id: "SYN-F03-001",
    trigger_rule_id: "rule-rainfall-v1",
  },
  settlement: {
    payout_id: "pay-1042",
    status: "SETTLED",
    payout_amount_paise: 1000000,
    currency: "INR",
    idempotency_key: "idem-pay-1042",
    transaction_id: "txn-1042",
    executed_at: NOW,
    is_duplicate: false,
    external_payout_status: "PROCESSED",
    external_reference: "pout_rzp_1042",
  },
  wallet: {
    wallet_id: "wal-demo",
    balance_paise: 1000000,
    currency: "INR",
    last_credit_paise: 1000000,
    last_transaction_id: "txn-1042",
    transactions: [
      { id: "tx-1", type: "CREDIT", amount_paise: 1000000, event_id: "EVT-1042", description: "Climate Event Settlement", timestamp: NOW, status: "Credited" }
    ]
  },
  audit: [
    { id: "a1", type: "TELEMETRY_RECEIVED", detail: "Weather observations received. Data from 3 sources ingested.", timestamp: "2026-08-25T14:32:01Z", correlation_id: CORRELATION, actor: "ingestion" },
    { id: "a2", type: "CONSENSUS_ACHIEVED", detail: "3/3 consensus established. Sources A, B, and C agree.", timestamp: "2026-08-25T14:32:02Z", correlation_id: CORRELATION, actor: "consensus" },
    { id: "a3", type: "POLICY_TRIGGERED", detail: "Policy threshold satisfied. 110 mm ≥ 100 mm.", timestamp: "2026-08-25T14:32:03Z", correlation_id: CORRELATION, actor: "policy" },
    { id: "a4", type: "SETTLEMENT_EXECUTED", detail: "Settlement authorized. Payout of ₹10,000.", timestamp: "2026-08-25T14:32:04Z", correlation_id: CORRELATION, actor: "settlement" },
    { id: "a5", type: "WALLET_CREDITED", detail: "Wallet credited. Simulated settlement completed.", timestamp: "2026-08-25T14:32:04Z", correlation_id: CORRELATION, actor: "wallet" }
  ],
  ai_insight: {
    explanations: {
      en: "All three weather sources reported rainfall above the policy threshold. The trusted rainfall value was 110 mm, which exceeds the 100 mm threshold. Therefore, the policy conditions were satisfied and a payout of ₹10,000 was automatically triggered.",
      hi: "तीनों मौसम स्रोतों ने पॉलिसी सीमा से अधिक वर्षा की सूचना दी। विश्वसनीय वर्षा का मान 110 मिमी था, जो 100 मिमी की सीमा से अधिक है। इसलिए, पॉलिसी की शर्तें पूरी हुईं और ₹10,000 का भुगतान स्वचालित रूप से हो गया।",
      te: "మూడు వాతావరణ మూలాలు పాలసీ పరిమితి కంటే ఎక్కువ వర్షపాతం నమోదు చేశాయి. విశ్వసనీయ వర్షపాతం 110 మి.మీ, ఇది 100 మి.మీ పరిమితిని మించిపోయింది. కాబట్టి, పాలసీ షరతులు నెరవేరాయి మరియు ₹10,000 చెల్లింపు స్వయంచాలకంగా జరిగింది."
    },
    anomaly_explanation: null,
    tts_available: true
  },
  history: {
    rainfall: HISTORY_NORMAL,
    temperature: []
  },
  event_list: EVENT_LIST
};

const corruptedSourceScenario: DashboardData = {
  ...normalScenario,
  scenario: "corrupted-source",
  consensus: {
    ...normalScenario.consensus,
    value: 109,
    agreeing_sources: 2,
    sources: [
      { id: "SRC-A", name: "IMD", metrics: { ...BASE_METRICS, rainfall_mm: 110 }, observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
      { id: "SRC-B", name: "OpenWeather", metrics: { ...BASE_METRICS, rainfall_mm: 108 }, observed_at: NOW, validation_status: "VALID", is_in_consensus_group: true },
      { id: "SRC-C", name: "Community", metrics: { ...BASE_METRICS, rainfall_mm: 7 }, observed_at: NOW, validation_status: "OUTLIER", is_in_consensus_group: false },
    ],
  },
  trigger: {
    ...normalScenario.trigger,
    observed_value: 109,
  },
  history: {
    rainfall: HISTORY_CORRUPTED,
    temperature: []
  },
  audit: [
    { id: "a1", type: "TELEMETRY_RECEIVED", detail: "Weather observations received. Data from 3 sources ingested.", timestamp: "2026-08-25T14:32:01Z", correlation_id: CORRELATION, actor: "ingestion" },
    { id: "a1b", type: "TELEMETRY_REJECTED", detail: "Source C flagged as inconsistent. Value outside expected range.", timestamp: "2026-08-25T14:32:02Z", correlation_id: CORRELATION, actor: "validation" },
    { id: "a2", type: "CONSENSUS_ACHIEVED", detail: "2/3 consensus established. Sources A and B agree.", timestamp: "2026-08-25T14:32:02Z", correlation_id: CORRELATION, actor: "consensus" },
    { id: "a3", type: "POLICY_TRIGGERED", detail: "Policy threshold satisfied. 109 mm ≥ 100 mm.", timestamp: "2026-08-25T14:32:03Z", correlation_id: CORRELATION, actor: "policy" },
    { id: "a4", type: "SETTLEMENT_EXECUTED", detail: "Settlement authorized. Payout of ₹10,000.", timestamp: "2026-08-25T14:32:04Z", correlation_id: CORRELATION, actor: "settlement" },
  ],
  ai_insight: {
    explanations: {
      en: "Two of the three weather sources reported rainfall above the policy threshold. Source C was identified as an outlier. The trusted rainfall value was 109 mm, which exceeds the 100 mm threshold. Therefore, the policy conditions were satisfied and a payout of ₹10,000 was automatically triggered.",
      hi: "तीन में से दो मौसम स्रोतों ने पॉलिसी सीमा से अधिक वर्षा की सूचना दी। स्रोत C को एक आउटलायर के रूप में पहचाना गया। विश्वसनीय वर्षा 109 मिमी थी, जो 100 मिमी की सीमा से अधिक है। इसलिए, ₹10,000 का भुगतान स्वचालित रूप से ट्रिगर किया गया।",
      te: "మూడు వాతావరణ మూలాలలో రెండు పాలసీ పరిమితి కంటే ఎక్కువ వర్షపాతం నమోదు చేశాయి. సోర్స్ C అవుట్‌లైయర్‌గా గుర్తించబడింది. విశ్వసనీయ వర్షపాతం 109 మి.మీ, ఇది 100 మి.మీ పరిమితిని మించిపోయింది. కాబట్టి, ₹10,000 చెల్లింపు ఆటోమేటిక్‌గా జరిగింది."
    },
    anomaly_explanation: "Source C reading was 7mm while others were ~110mm.",
    tts_available: true
  }
};

const noConsensusScenario: DashboardData = {
  ...normalScenario,
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
      { id: "SRC-A", name: "IMD", metrics: { ...BASE_METRICS, rainfall_mm: 120 }, observed_at: NOW, validation_status: "SOURCE_DISAGREEMENT", is_in_consensus_group: false },
      { id: "SRC-B", name: "OpenWeather", metrics: { ...BASE_METRICS, rainfall_mm: 50 }, observed_at: NOW, validation_status: "SOURCE_DISAGREEMENT", is_in_consensus_group: false },
      { id: "SRC-C", name: "Community", metrics: { ...BASE_METRICS, rainfall_mm: 5 }, observed_at: NOW, validation_status: "SOURCE_DISAGREEMENT", is_in_consensus_group: false },
    ],
  },
  trigger: {
    state: "NO_CONSENSUS",
    observed_value: null,
    threshold: 100,
    reason: "Insufficient agreement",
    evaluated_at: NOW,
    policy_id: "SYN-F03-001",
    trigger_rule_id: "rule-rainfall-v1",
  },
  settlement: {
    payout_id: "pay-none",
    status: "BLOCKED",
    payout_amount_paise: 0,
    currency: "INR",
    idempotency_key: "",
    transaction_id: null,
    executed_at: null,
    is_duplicate: false,
    external_payout_status: "UNAVAILABLE",
    external_reference: null,
  },
  wallet: {
    wallet_id: "wal-demo",
    balance_paise: 0,
    currency: "INR",
    last_credit_paise: null,
    last_transaction_id: null,
    transactions: []
  },
  history: {
    rainfall: [
      { time: "13:40", source_a: 20, source_b: 10, source_c: 2, consensus: null },
      { time: "14:30", source_a: 120, source_b: 50, source_c: 5, consensus: null },
    ],
    temperature: []
  },
  audit: [
    { id: "a1", type: "TELEMETRY_RECEIVED", detail: "Weather observations received.", timestamp: "2026-08-25T14:32:01Z", correlation_id: CORRELATION, actor: "ingestion" },
    { id: "a2", type: "CONSENSUS_FAILED", detail: "No pair of sources within 5 mm tolerance. A=120, B=50, C=5.", timestamp: "2026-08-25T14:32:02Z", correlation_id: CORRELATION, actor: "consensus" },
    { id: "a3", type: "POLICY_NOT_MET", detail: "No trusted value available.", timestamp: "2026-08-25T14:32:03Z", correlation_id: CORRELATION, actor: "policy" },
  ],
  ai_insight: {
    explanations: {
      en: "All three weather stations reported drastically different values (120mm, 50mm, 5mm). Because no two stations agreed within the acceptable tolerance, the system could not establish a trusted consensus value. As a safety measure, settlement was blocked.",
      hi: "तीनों मौसम स्टेशनों ने अलग-अलग मान (120mm, 50mm, 5mm) दर्ज किए। सहमति न होने के कारण, सिस्टम एक विश्वसनीय मान स्थापित नहीं कर सका। सुरक्षा उपाय के रूप में, भुगतान रोक दिया गया।",
      te: "మూడు వాతావరణ కేంద్రాలు వేర్వేరు విలువలను (120mm, 50mm, 5mm) నమోదు చేశాయి. అంగీకారం లేకపోవడం వల్ల, సిస్టమ్ నమ్మదగిన విలువను ఏర్పాటు చేయలేకపోయింది. కాబట్టి చెల్లింపు నిరోధించబడింది."
    },
    anomaly_explanation: "Total failure of environmental sensors or extreme microclimate event.",
    tts_available: true
  }
};

const duplicateSettlementScenario: DashboardData = {
  ...normalScenario,
  scenario: "duplicate-settlement",
  trigger: {
    ...normalScenario.trigger,
    state: "ALREADY_TRIGGERED",
  },
  settlement: {
    ...normalScenario.settlement,
    status: "DUPLICATE",
    is_duplicate: true,
  },
  wallet: {
    ...normalScenario.wallet,
    transactions: [
      { id: "tx-2", type: "BLOCKED", amount_paise: 0, event_id: "EVT-1042", description: "Duplicate settlement prevented", timestamp: "2026-08-25T14:32:42Z", status: "Blocked" },
      { id: "tx-1", type: "CREDIT", amount_paise: 1000000, event_id: "EVT-1042", description: "Climate Event Settlement", timestamp: NOW, status: "Credited" }
    ]
  },
  audit: [
    ...normalScenario.audit,
    { id: "a6", type: "SETTLEMENT_DUPLICATE", detail: "Duplicate request detected with identical idempotency key (idem-pay-1042).", timestamp: "2026-08-25T14:32:42Z", correlation_id: CORRELATION, actor: "settlement" }
  ],
  ai_insight: {
    explanations: {
      en: "The system detected multiple identical payout requests for this event. Using idempotency keys, the ledger successfully prevented duplicate settlements. Only one payout of ₹10,000 was executed.",
      hi: "सिस्टम ने इस घटना के लिए कई समान भुगतान अनुरोधों का पता लगाया। लेज़र ने सफलतापूर्वक डुप्लिकेट भुगतान को रोका। केवल ₹10,000 का एक भुगतान किया गया।",
      te: "సిస్టమ్ ఈ ఈవెంట్ కోసం బహుళ సారూప్య చెల్లింపు అభ్యర్థనలను గుర్తించింది. సిస్టమ్ నకిలీ చెల్లింపులను విజయవంతంగా నిరోధించింది. కేవలం ₹10,000 మాత్రమే చెల్లించబడింది."
    },
    anomaly_explanation: null,
    tts_available: true
  }
};

const SCENARIO_DATA: Record<ScenarioId, DashboardData> = {
  normal: normalScenario,
  "corrupted-source": corruptedSourceScenario,
  "no-consensus": noConsensusScenario,
  "duplicate-settlement": duplicateSettlementScenario,
};

export function getScenarioData(scenario: ScenarioId): DashboardData {
  return SCENARIO_DATA[scenario];
}
