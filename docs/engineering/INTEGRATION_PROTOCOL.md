# Integration Protocol

1. Freeze the canonical entity and API fields.
2. Backend publishes OpenAPI plus seeded example responses.
3. Frontend builds the policy-to-audit flow against those fixtures.
4. Database owner validates migration and seed fixture compatibility.
5. Replace one mock endpoint at a time; run the clean trigger and retry scenarios after each merge.
6. Record any contract change in the decision log and update all consumers together.
