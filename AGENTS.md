# divai – Monorepo

Housing Loan Arrears Rescheduling AI Agent: FastAPI rule-based backend + Next.js bilingual citizen portal.

## Layout

| Directory | Stack | Notes |
|---|---|---|
| `backend/` | Python 3.13, FastAPI, SQLite, uv | Config, DB, routes built. Agent pipeline (`app/agent/`) **not yet built** — POST `/api/submit` returns mock. |
| `frontend/` | Next.js 14 (pages router), pnpm, next-auth v4, i18n (en/ar) | Form POSTs directly to `NEXT_PUBLIC_API_URL` (no local `/api/submit` stub). |
| `ai/` | — | Scratch CSV analysis / ML experiments. Gitignored, not part of the pipeline. |

## Commands

```bash
# Backend
cd backend && uv run dev                    # or: uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && pnpm dev                     # http://localhost:3000
pnpm build
pnpm start
```

Backend Swagger at `http://localhost:8000/docs`.

## Essentials

- **Agent pipeline** (planned): Retriever → Validator → Analyzer → Decider → Explainer. Not yet built; backend returns mock.
- **5 statuses**: `in_progress`, `additional_info`, `approved`, `rejected`, `human_review`. Confidence < 0.7 → human review.
- **Business rules spec**: `backend/resources/AGENT_GUIDE.md` — normative source for R1–R3 rules, assessment matrix, decision logic.
- **Auth**: GitHub (dev) + UAE PASS (sandbox OAuth2/OIDC). `.env.local` has committed sandbox creds — treat as dev-only.
- **No tests, no CI/CD, no lint/typecheck commands.** No pre-commit hooks.
- **CORS**: whitelisted for frontend origin only. Frontend at `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).
- **Per-package details**: See `backend/AGENTS.md` (pipeline spec, DB schema, env vars) and `frontend/AGENTS.md` (form fields, component tree, i18n).
