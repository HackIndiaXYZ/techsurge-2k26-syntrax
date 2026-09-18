# Telemetry Integrity, Fraud, and Risk

**Spoofed or corrupted telemetry** is an input designed to misrepresent weather conditions. The MVP defends by accepting only known demo source IDs, validating event shape, timestamp freshness, region/metric/unit, plausible range, and duplicate identity before consensus. Consensus makes a single discrepant source visible and prevents it from alone determining the outcome.

This does not prove immunity to collusion, sensor compromise, provider outage, model error, or real-world adversaries. The MVP tracks source reliability only as a fixed note; it does not silently learn trust weights. A future system would need provider governance, signed payloads, monitoring, and incident response.
