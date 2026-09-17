# GIT AND GITHUB WORKFLOW

The GitHub repository is the shared engineering brain and source of truth.

## Branching Strategy
- main: The stable, integrated, and deployable branch.
- Role branches: rontend/nikhil, ackend/ramraj, i/sanju, infra/akshaya.

## Workflow Rules
1. Each person works primarily on their dedicated branch.
2. Nobody directly modifies another person's active feature without coordination.
3. No direct pushes to main without coordination. Use Pull Requests for controlled integration.
4. main must remain deployable at all times.
5. Shared interfaces (like API_CONTRACTS.md or docker-compose.yml) are agreed upon before implementation.
6. Never rewrite another person's work without discussion.
