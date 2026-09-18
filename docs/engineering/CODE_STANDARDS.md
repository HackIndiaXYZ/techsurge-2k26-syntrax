# Code Standards

Keep modules named after the canonical domain model. Pure functions should compute validation, consensus and trigger results from explicit arguments; database and HTTP adapters stay thin. Version policy rules, return typed errors, and avoid hidden defaults. Tests name the scenario and expected business outcome, for example `test_retry_creates_one_wallet_credit`.
