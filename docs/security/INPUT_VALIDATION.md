# Input Validation

Validate telemetry schema, allowlisted source ID, source-event ID length, UUID region, metric enum, unit, decimal bounds, time-window order, timestamp freshness, future skew, and metadata size before persistence. Reject malformed, stale, duplicate, impossible, region-mismatched and unit-mismatched input with a recorded reason. Parameterize all SQL through the ORM and escape/render all UI text safely to prevent SQL injection and XSS.
