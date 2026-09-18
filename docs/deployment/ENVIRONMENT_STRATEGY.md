# Environment Strategy

Use `local`, `preview`, and optional `demo` environments. Each has a separate synthetic database/schema and unique reset seed. `.env.example` lists names only; real values live in provider secrets or untracked local files. Never share a development database with a live presentation after a rehearsal without resetting fixtures.
