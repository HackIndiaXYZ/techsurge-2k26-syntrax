# Architecture

> **TBD — DECIDE AFTER PROBLEM STATEMENT:** The final architecture must be selected after the PS is revealed.

## Technology-Agnostic Architecture Template

1. **Frontend**
   ↓
2. **API / Backend**
   ↓
3. **Business Logic**
   ↓
4. **Database / Storage**
   ↓
5. **AI / ML services** (where required)
   ↓
6. **External APIs / services** (where required)
   ↓
7. **Deployment / infrastructure**

## Preferred Candidate Technologies (Do Not Install Yet)

**Frontend candidates:**
- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui

**Backend candidates:**
- Python
- FastAPI
- Pydantic
- SQLAlchemy

**Database candidates:**
- PostgreSQL
- Supabase
- pgvector (when vector search is actually needed)

**AI candidates:**
- OpenRouter
- Gemini
- OpenAI-compatible APIs
- LangGraph/LangChain/LlamaIndex (only when justified)

**Deployment candidates:**
- Vercel
- Render
- Supabase

## Technology Matrix

- **Required:** Standard web technologies (HTTP, JSON).
- **Optional:** Specific UI components or utility libraries.
- **Only-if-needed:** Vector databases, complex AI agents, specialized infrastructure.

