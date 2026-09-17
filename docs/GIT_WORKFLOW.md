# Git Workflow

Git branches are for source-code isolation, not separate copies of the entire conceptual project.

## Branches
- **Main branch:** `main` (Stable)
- **Development branches:**
  - `frontend/nikhil`
  - `backend/ramraj`
  - `ai/sanju`
  - `infra/akshaya`

## Rules
- `main` is stable.
- Teammates normally work on their own branches.
- Commit frequently.
- Use meaningful commit messages.
- Pull/rebase or merge from `main` when appropriate.
- Avoid editing the same files concurrently.
- Use API contracts and shared docs to coordinate.
- Merge completed work carefully.
- Do not casually force-push shared branches.
- Before major integration, verify build/tests.

