# End-to-End Testing

Playwright covers the dashboard’s visible proof: synthetic label, active policy, incoming source cards, validation/rejection state, consensus value, trigger outcome, wallet balance change, audit timeline and idempotency retry. Run against seeded deterministic scenarios; do not rely on wall-clock weather or a remote provider.

The key assertion after retry is not just a success toast: it is the unchanged synthetic wallet balance and one displayed transaction ID.
