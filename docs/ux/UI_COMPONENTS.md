# PS-F03 MVP UI Components

| Component | Required states | API dependency |
| --- | --- | --- |
| System banner | synthetic/no real money | static configuration |
| Policy card | active, expired, triggered, paid | policy read |
| Telemetry feed | loading, accepted, rejected, duplicate, stale | dashboard/telemetry projection |
| Source comparison | pending, achieved, no consensus, outlier | consensus read |
| Trigger card | not met, triggered, already triggered, no consensus | evaluation read |
| Payout and wallet | pending, completed, failed, retry safe | payout/wallet read |
| Audit timeline | empty, correlated events, API error | audit read |
| Simulation controls | disabled while running, success/failure | simulation command |

The first screen can be one dashboard; separate pages are only needed if the evidence becomes unreadable.
