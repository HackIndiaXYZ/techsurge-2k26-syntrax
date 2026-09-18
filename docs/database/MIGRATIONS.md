# Migration Strategy

Akshaya owns migrations. Establish schema in dependency order: lookup entities, policyholder/region/source/rule/policy, telemetry and validation, consensus, trigger evaluation, wallet, payout/transaction, audit. Every migration has an upgrade and a tested rollback where safe; do not roll back financial-audit rows by deleting evidence in a shared environment.

Before merging a migration, apply it to an empty database, seed the canonical scenario set, and run the duplicate-payout retry test. Schema changes that rename canonical fields require coordinated API, frontend, fixture, and documentation updates in the same PR.
