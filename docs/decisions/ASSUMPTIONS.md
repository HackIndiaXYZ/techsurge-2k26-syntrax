# PS-F03 Assumptions Register

| Assumption | Why needed | Effect if false |
| --- | --- | --- |
| Demo region, people, policies, sources and balances are synthetic | No organizer data or real accounts are provided | Replace only through a separately approved data-governance decision |
| 17 effective hours are available | Drives MVP-first design | De-scope optional deployment/UI features first |
| Three independent logical sources can be simulated | Allows a readable quorum demo | Use deterministic fixture adapters, not real provider contracts |
| INR is a display currency only | Makes payout intuitive | Store integer paise but label every amount synthetic |
| One 60-minute rainfall trigger is enough | Meets minimum telemetry-to-payout proof | Do not add multi-trigger policies unless core path passes |
