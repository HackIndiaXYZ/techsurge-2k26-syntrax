# Synthetic Data and Seed Strategy

Use deterministic, versioned fixtures with the prefix `SYN-`. Examples: `SYN-REGION-001`, `SYN-HOLDER-001`, `SYN-WALLET-001`, `SYN-POLICY-RAIN-001`, and sources `SYN-SRC-A/B/C`. Never seed real people, addresses, account identifiers, weather-provider credentials, or real balances.

Required scenario fixture sets are normal weather, genuine synthetic flood, corrupted source, conflicting sources/no quorum, duplicate event, missing source, barely crossed threshold, threshold not crossed, extreme invalid value, payout timeout, and payout retry. Each fixture includes expected validation, consensus, trigger, payout, audit, and metric labels. `clean-trigger` uses values 101, 102, and 103 mm for a 100 mm rainfall policy. The first corrupt-source preview uses 101, 102, and 500 mm to demonstrate outlier handling without being presented as a real weather event.
