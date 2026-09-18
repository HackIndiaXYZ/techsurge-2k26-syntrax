# Deployment Checklist

- Confirm all data is synthetic and secrets are not committed.
- Apply migration and load deterministic seed only.
- Set backend CORS to the actual frontend origin.
- Verify policy, dashboard, corrupt-source, clean-trigger and retry flows.
- Verify synthetic/basis-risk labels and measured metric display.
- Prepare local fallback and document active demo URL/version.
