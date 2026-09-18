# Git Workflow

`main` remains deployable and integration-ready. Nikhil owns `frontend/nikhil`, Ramraj `backend/ramraj`, Sanju `ai/sanju`, and Akshaya `infra/akshaya`. Do not commit to another person’s branch.

Before coding, link the branch task to canonical schemas and API contracts. Frontend works against fixtures/mocks while backend completes endpoints. Each PR states scope, test scenario, migration impact, API impact, and whether the demo flow changes. Rebase or merge current `main` before review; resolve conflicts with the owning author, never by silently changing shared contracts. Main merges only after the affected critical path passes.
