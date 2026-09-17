# Team Roles

*Ownership is not a hard restriction; teammates can help each other when necessary.*

## Nikhil
**Frontend + Product Experience + Integration Lead**
- **Ownership:** Frontend application, UI/UX, user flow, final product integration.
- **Typical files/directories:** `frontend/`
- **Responsibilities:** Building the UI, integrating backend APIs, ensuring a smooth user experience.
- **Integration Dependencies:** Requires API contracts and backend implementation from Ramraj.
- **Avoid modifying without coordination:** Backend API routes, database schemas.

## Ramraj
**Backend / Financial Systems**
- **Ownership:** Backend APIs, core business logic.
- **Typical files/directories:** `backend/`
- **Responsibilities:** Implementing API endpoints, data processing, business rules.
- **Integration Dependencies:** Requires database schema from Akshaya, UI requirements from Nikhil.
- **Avoid modifying without coordination:** Frontend components, infrastructure configuration.

## Sanju
**AI/ML + Agents + RAG**
- **Ownership:** AI integrations, prompts, ML models, vector search (if applicable).
- **Typical files/directories:** `ai/`
- **Responsibilities:** Implementing AI features, optimizing prompts, managing AI provider interactions.
- **Integration Dependencies:** Requires data from Ramraj/Akshaya, UI hooks from Nikhil.
- **Avoid modifying without coordination:** Core database schema, core frontend layout.

## Akshaya
**Infrastructure + Database + Security + Testing**
- **Ownership:** Database setup, deployment, security rules, testing frameworks.
- **Typical files/directories:** `infra/`, `database/`
- **Responsibilities:** Managing schemas, migrations, cloud deployments, security audits, test CI.
- **Integration Dependencies:** Needs requirements from the whole team to provision the right infrastructure.
- **Avoid modifying without coordination:** Application business logic.

