# AI AGENT RULES

AI coding agents (Antigravity, Claude Code, Codex, Copilot) must adhere to these rules:

1. **Inspect First:** Always inspect the repository and read the relevant documentation in docs/ before acting.
2. **Respect the Source of Truth:** GitHub documentation is the source of truth, not previous ChatGPT conversational memory.
3. **No Speculation:** Do NOT invent Round 2 requirements, APIs, architectures, or schemas before the PS is officially revealed and documented.
4. **Boundary Respect:** Do not modify files outside your assigned domain (e.g., i/sanju should not rewrite rontend/nikhil files) without explicit coordination.
5. **No Secrets:** Never commit passwords, API keys, or tokens.
6. **No Destructive Operations:** Do not run m, Remove-Item, git clean, DROP, DELETE, or docker rm without explicit human approval.
7. **Verify Changes:** Ensure generated code is reviewed and tested.
