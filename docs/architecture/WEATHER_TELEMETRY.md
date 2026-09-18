# Canonical Weather Telemetry Model

A `TelemetryEvent` represents one source’s measurement for one already-defined region and aggregation window. Required fields are `event_id` (server UUID), `source_id`, `source_event_id`, `region_id`, `metric`, `value`, `unit`, `observed_at`, `window_start`, `window_end`, `received_at`, `metadata`, and `validation_state`.

The MVP accepts `RAINFALL_MM` in `mm`. It rejects malformed structure, unknown source/region, unsupported unit, negative or greater-than-400-mm value for the 60-minute demo window, end-before-start window, stale observation, excessive future skew, duplicate `(source_id, source_event_id)`, and incompatible replay. It stores out-of-order valid events but only consensus-matches exact windows; it never silently reuses a reading from a different window. Missing data yields pending/no-consensus rather than a guessed value.

Metadata is non-authoritative source context such as scenario name or simulated device note. It is size-limited and retained for audit, but cannot override canonical metric, unit, time, value or identity fields.
