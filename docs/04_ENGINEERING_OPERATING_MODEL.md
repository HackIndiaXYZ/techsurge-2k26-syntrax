# Engineering Operating Model

Work in thin vertical slices, starting with a fixed mock response and ending with the displayed audit evidence. The order is: freeze canonical schemas; publish FastAPI/OpenAPI contracts; provide mock fixtures; implement direct ingestion-to-ledger flow; wire the dashboard; then rehearse failure and retry paths. This lets frontend and backend work independently until integration.

The core path stays deterministic and synchronous for the MVP. Any optional component must be behind an interface and must not delay policy adjudication. Each PR changes one owner area, names the contract it implements, and includes its applicable scenario from [Test Plan](testing/TEST_PLAN.md).

The selected stack and deliberate exclusions are in [Tech Stack](engineering/TECH_STACK.md). Team workflow is in [Git Workflow](engineering/GIT_WORKFLOW.md).
