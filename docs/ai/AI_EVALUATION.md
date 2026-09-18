# Optional AI Evaluation

Evaluate optional anomaly detection offline against labelled synthetic scenarios: precision/recall for known outliers, false-positive rate for normal weather, explanation consistency with stored values, latency, and graceful fallback when the model is unavailable. Do not report a model metric as consensus accuracy; consensus accuracy is evaluated independently by deterministic expected outcomes.

Reject an AI feature if it obscures the source comparison, cannot explain its score, increases the critical-path latency, or creates any ability to influence a payout.
