# Known Facts and Explicit Decisions

| Classification | PS-F03 fact or decision |
| --- | --- |
| Official PS requirement | Stream multi-source weather telemetry; validate/consense it; deterministically adjudicate pre-agreed triggers; execute an idempotent simulated payout; retain audit evidence. |
| Official safety boundary | Use public or synthetic inputs and synthetic wallets only. No real money, accounts, payment rails, telemetry contracts, licensing, or production-security claims. |
| Team design decision | Three simulated sources, 2-of-3 quorum, median of agreeing values, 5 mm agreement tolerance per 60-minute rainfall window. |
| Team design decision | One rainfall policy: 100 mm or more accumulated rainfall in 60 minutes pays INR 10,000 in synthetic money once. |
| Team assumption | A named demo micro-region, policyholder, wallets, and weather events are synthetic fixtures rather than real people, contracts, or field telemetry. |
| Optional idea | Offline anomaly scoring or a plain-language explanation assistant. Neither may decide a trigger or payout. |
| Out of scope | Blockchain, Kafka, real UPI/stablecoin rails, algorithmic liquidity management, provider contracts, real onboarding, and production compliance. |

Unresolved items are limited to deployment credentials and the final choice of a public-data citation, neither of which blocks the synthetic demo. See [Open Questions](decisions/OPEN_QUESTIONS.md).
