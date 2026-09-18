# PS-F03 Integration Map

| Integration | MVP posture | Boundary |
| --- | --- | --- |
| Synthetic telemetry generator | Required | Emits canonical request-shaped fixtures only |
| Optional public weather dataset | Optional reference/comparison | Read-only and clearly labeled; no provider contract claim |
| PostgreSQL / Supabase | Selected persistence service | Stores synthetic data; service role remains server-side |
| Vercel | Selected frontend host when deploying | Hosts UI only |
| Render | Selected FastAPI host when deploying | Holds backend environment secrets |
| UPI / bank / wallet provider | Not used | Public documentation may inform a future production gap only |
| LLM / agent / RAG provider | Not used in MVP | Never receives payment authority or sensitive data |
