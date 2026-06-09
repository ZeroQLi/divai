# divai – Monorepo

Housing Loan Arrears Rescheduling AI Agent: FastAPI rule-based backend + Next.js bilingual citizen portal.

## Layout

| Directory | Stack | Notes |
|---|---|---|---|
| `backend/` | Python 3.13, FastAPI, SQLite, uv | Config, DB, routes, submit endpoint — 16-col `applicants` + 12-col `applications` table. |
| `frontend/` | Next.js 14 (pages router), pnpm, next-auth v4, i18n (en/ar) | Dashboard form POSTs multipart form-data to backend. |
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

- **Agent pipeline NOT built.** POST `/api/submit` just stores the application — no AI/rule-based decision runs yet.
- **5 statuses**: `in_progress`, `additional_info`, `approved`, `rejected`, `human_review`. Confidence < 0.7 → human review.
- **Business rules spec**: `backend/resources/AGENT_GUIDE.md`.
- **Auth**: GitHub (dev) + UAE PASS (sandbox OAuth2/OIDC). `.env.local` has committed sandbox creds — treat as dev-only.
- **No tests, no CI/CD, no lint/typecheck commands.** No pre-commit hooks.
- **CORS**: whitelisted for frontend origin only. Frontend at `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).
- **Per-package details**: See `backend/AGENTS.md` (pipeline spec, DB schema, env vars) and `frontend/AGENTS.md` (form fields, component tree, i18n).
