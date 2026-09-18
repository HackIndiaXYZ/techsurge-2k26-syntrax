# Secrets Management

Keep `DATABASE_URL`, demo operator token, deployment tokens and any optional provider key in untracked local `.env` or provider secret stores. `.env.example` contains names only. Rotate an accidentally exposed token, revoke its deployment access, and replace it; never paste it into docs, issues, fixtures, client bundles or logs.
