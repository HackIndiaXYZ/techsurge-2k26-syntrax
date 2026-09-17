# Security

**NEVER PUT REAL CREDENTIALS IN GIT.**

## Hackathon Security Rules

- **Secrets:** Never commit secrets to the repository.
- **.env files:** Add `.env` to `.gitignore`. Only commit `.env.example`.
- **API keys:** Rotate compromised keys immediately.
- **Authentication:** Verify user identity for protected routes.
- **Authorization:** Ensure users can only access their own data.
- **RBAC (where required):** Role-Based Access Control for different user types.
- **Database RLS (where required):** Row Level Security to protect data at the database level.
- **Input validation:** Always validate data from the client.
- **SQL injection:** Use parameterized queries or ORMs.
- **XSS:** Sanitize user input before rendering.
- **CORS:** Restrict cross-origin requests to known domains.
- **CSRF (where applicable):** Protect against cross-site request forgery.
- **Rate limiting:** Protect APIs from abuse.
- **HTTPS:** Ensure secure communication.
- **Secure cookies/sessions (where applicable):** Use secure, HTTP-only flags.
- **Logging:** Log security-relevant events without exposing sensitive data.
- **Error handling:** Do not expose stack traces or sensitive internal details to the client.
- **Dependency security:** Run basic checks on dependencies (e.g., `npm audit`).

