# Documentation Inventory and Classification

This inventory classifies every pre-existing Markdown/configuration documentation file inspected before the PS-F03 rewrite. No placeholder is retained. A file marked **MUST REWRITE** contained obsolete live-problem framing or no useful implementation content. **MUST UPDATE** preserves its purpose but now points to or contains PS-F03 guidance. **HISTORICAL** is intentionally isolated. **NOT APPLICABLE** has a concrete MVP reason. **STILL VALID** was preserved.

| File | Classification | Disposition |
| --- | --- | --- |
| `.agents/rules/.gitkeep` | STILL VALID | Empty directory-retention file; no product guidance |
| `.agents/rules/00_GLOBAL_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.agents/rules/01_PROJECT_CONTEXT_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.agents/rules/02_ARCHITECTURE_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.agents/rules/03_CODE_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.agents/rules/04_GIT_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.agents/rules/05_API_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.agents/rules/06_DATABASE_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.agents/rules/07_AI_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.agents/rules/08_SECURITY_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.agents/rules/09_TESTING_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.agents/rules/10_DEPLOYMENT_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.agents/rules/11_HACKATHON_RULES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `.env.example` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `.gitignore` | STILL VALID | No PS-specific conflict; preserve ignore rules |
| `README.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/00_INDEX.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/01_HACKATHON_CONTEXT.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/02_TEAM.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/03_PROJECT_IDENTITY.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/04_ENGINEERING_OPERATING_MODEL.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/05_KNOWN_VS_UNKNOWN.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/AI_RULES.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/AI_SYSTEM.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/API_CONTRACTS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ARCHITECTURE.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/DATABASE_SCHEMA.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/DEPLOYMENT.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/GIT_WORKFLOW.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/HANDOFF.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/PROJECT_CONTEXT.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/PROJECT_MEMORY.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/SECURITY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/TEAM_ROLES.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ai/AGENT_ARCHITECTURE.md` | NOT APPLICABLE | Explicit PS-F03 non-selection with rationale |
| `docs/ai/AI_AGENT_RULES.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ai/AI_ARCHITECTURE.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ai/AI_CONTEXT_PROTOCOL.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ai/AI_EVALUATION.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ai/AI_HANDOFFS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ai/AI_SYSTEM.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ai/AI_TOOL_ASSIGNMENTS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ai/AI_WORKFLOW.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ai/MCP_STRATEGY.md` | NOT APPLICABLE | Explicit PS-F03 non-selection with rationale |
| `docs/ai/PROMPTING_GUIDELINES.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ai/RAG_STRATEGY.md` | NOT APPLICABLE | Explicit PS-F03 non-selection with rationale |
| `docs/architecture/API_CONTRACTS.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/architecture/ARCHITECTURE_DECISIONS.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/architecture/COMPONENT_MAP.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/architecture/DATA_FLOW.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/architecture/INTEGRATION_MAP.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/architecture/SYSTEM_ARCHITECTURE.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/database/DATABASE_SCHEMA.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/database/DATA_MODEL.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/database/DATA_SEEDING.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/database/MIGRATIONS.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/database/RLS_AND_AUTHORIZATION.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/decisions/ASSUMPTIONS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/decisions/DECISION_LOG.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/decisions/OPEN_QUESTIONS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/decisions/TRADEOFFS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/deployment/CI_CD.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/deployment/DEPLOYMENT.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/deployment/DEPLOYMENT_CHECKLIST.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/deployment/DOCKER.md` | NOT APPLICABLE | Explicit PS-F03 non-selection with rationale |
| `docs/deployment/ENVIRONMENT_STRATEGY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/deployment/RENDER_DEPLOYMENT.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/deployment/SUPABASE_DEPLOYMENT.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/deployment/VERCEL_DEPLOYMENT.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/engineering/BRANCH_STRATEGY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/engineering/CODE_REVIEW.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/engineering/CODE_STANDARDS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/engineering/DEVELOPMENT_RULES.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/engineering/ERROR_HANDLING.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/engineering/GIT_WORKFLOW.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/engineering/INTEGRATION_PROTOCOL.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/engineering/PARALLEL_DEVELOPMENT.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/engineering/PROJECT_STRUCTURE.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/engineering/TECH_STACK.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/fintech/BANKING.md` | NOT APPLICABLE | Explicit PS-F03 non-selection with rationale |
| `docs/fintech/CREDIT_AND_LENDING.md` | NOT APPLICABLE | Explicit PS-F03 non-selection with rationale |
| `docs/fintech/FINANCIAL_INCLUSION.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/fintech/FINTECH_FOUNDATIONS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/fintech/FINTECH_SECURITY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/fintech/FRAUD_AND_RISK.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/fintech/PAYMENT_ARCHITECTURE.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/fintech/SANDBOX_TESTING.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/hackathon/17_HOUR_ENGINEERING_PLAN.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/hackathon/BUILD_TIMELINE.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/hackathon/DEMO_STRATEGY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/hackathon/EMERGENCY_PROTOCOL.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/hackathon/JUDGE_DEMO_FLOW.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/hackathon/PITCH_STRUCTURE.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/hackathon/PRESENTATION_STRATEGY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/hackathon/ROUND_TRANSITION_PROTOCOL.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/history/PREPARATION_JOURNEY.md` | HISTORICAL | Retained only as clearly superseded Round 1 record |
| `docs/history/ROUND_1_JOURNEY.md` | HISTORICAL | Retained only as clearly superseded Round 1 record |
| `docs/history/ROUND_1_LESSONS.md` | HISTORICAL | Retained only as clearly superseded Round 1 record |
| `docs/history/ROUND_1_PROBLEM.md` | HISTORICAL | Retained only as clearly superseded Round 1 record |
| `docs/history/ROUND_1_RESEARCH.md` | HISTORICAL | Retained only as clearly superseded Round 1 record |
| `docs/history/ROUND_1_SOLUTION_NEXTRA.md` | HISTORICAL | Retained only as clearly superseded Round 1 record |
| `docs/operations/BLOCKERS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/operations/DAILY_STATUS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/operations/HANDOFF.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/operations/INTEGRATION_STATUS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/operations/RELEASE_STATUS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/reference/API_REFERENCE.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/reference/QUICK_REFERENCE.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/reference/SOURCE_MATERIAL_INDEX.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/reference/TERMINOLOGY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/reference/TOOL_REFERENCE.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/round2/ACCEPTANCE_CRITERIA.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/round2/MVP_SCOPE.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/round2/OUT_OF_SCOPE.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/round2/PROBLEM_STATEMENT.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/round2/PS_ANALYSIS.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/round2/REQUIREMENTS.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/round2/ROUND_2_CONTEXT.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/round2/SUCCESS_METRICS.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/round2/USER_JOURNEYS.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/round2/USER_PERSONAS.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/round2/USE_CASES.md` | MUST REWRITE | PS-F03-specific content or compatibility pointer added |
| `docs/security/API_SECURITY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/security/AUTHENTICATION.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/security/AUTHORIZATION.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/security/DATA_PRIVACY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/security/INPUT_VALIDATION.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/security/SECRETS_MANAGEMENT.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/security/SECURITY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/security/SECURITY_CHECKLIST.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/services/EXTERNAL_SERVICES.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/services/GEMINI.md` | NOT APPLICABLE | Explicit PS-F03 non-selection with rationale |
| `docs/services/OPENROUTER.md` | NOT APPLICABLE | Explicit PS-F03 non-selection with rationale |
| `docs/services/PAYMENT_INTEGRATIONS.md` | NOT APPLICABLE | Explicit PS-F03 non-selection with rationale |
| `docs/services/RENDER.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/services/SUPABASE.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/services/VERCEL.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/services/WEBHOOKS.md` | NOT APPLICABLE | Explicit PS-F03 non-selection with rationale |
| `docs/testing/AI_TESTING.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/testing/API_TESTING.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/testing/DEMO_TEST_CHECKLIST.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/testing/E2E_TESTING.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/testing/FRONTEND_TESTING.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/testing/TESTING_STRATEGY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/testing/TEST_PLAN.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ux/ACCESSIBILITY.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ux/DESIGN_SYSTEM.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ux/MOTION_AND_INTERACTION.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ux/RESPONSIVE_DESIGN.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ux/UI_COMPONENTS.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |
| `docs/ux/UX_PRINCIPLES.md` | MUST UPDATE | PS-F03-specific content or compatibility pointer added |

New canonical documents added during this rewrite include the consensus/trigger specification, failure/metrics plan, evaluation traceability matrix, and ADR set.
