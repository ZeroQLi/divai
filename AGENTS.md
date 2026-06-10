# divai – Monorepo

Housing Loan Arrears Rescheduling AI Agent: FastAPI backend + Next.js bilingual citizen portal.

## Monorepo Structure & Ownership

**Critical architecture boundaries:**
- `backend/` → Python rule-based AI agent system
- `frontend/` → Next.js bilingual citizen portal  
- `ai/` → Gitignored ML experiments (not part of pipeline)
- **No shared code** – separate ecosystems (uv vs pnpm, Python vs Node)

**Real entrypoints:**
- Backend: `backend/app/main.py:11` (startup), `backend/app/agent/pipeline.py:100` (agent)
- Frontend: `frontend/pages/index.js:46` (dashboard), `frontend/pages/login.js:8` (auth), `frontend/pages/admin.js` (admin decisions view)

## Setup & Development Commands

**Exact developer sequence (order matters):**

```bash
# Clone and initial setup (ONE TIME ONLY)
git clone <repo-url> && cd divai
cd backend && uv sync                    # install Python dependencies
cd frontend && pnpm install              # install Node.js dependencies
touch backend/.env && touch frontend/.env.local  # create env files

# Backend (port 8000) - separate terminal
cd backend
uv run uvicorn app.main:app --reload --port 8000
# OR: uv run dev

# Frontend (port 3000) - separate terminal  
cd frontend
pnpm dev
```

**Database setup (auto-run on first backend start):**
```bash
# To re-seed: delete data.db and restart backend
rm -f backend/data.db
# Manual database inspection:
cd backend && uv run sqlite_web data.db --port 8080
```

## Framework Quirks & Gotchas

**Backend (Python):**
- Uses `uv` for dependency management (pip equivalent)
- SQLite via python's built-in sqlite3 (not SQLAlchemy/ORM)
- Agent pipeline uses pydantic-ai v1 with OpenRouter (`google/gemma-4-26b-a4b-it`)
- **Critical**: Database path resolution (`DATABASE_URL` resolves to backend/)

**Frontend (Next.js):**
- Pages router (not app router) – `pages/` directory
- i18n: locale detection OFF, manual language switching via `LangToggle`
- Form posts multipart FormData directly to backend (no `/api/submit` stub)
- Auth: Next.js v4 with GitHub + UAE PASS (sandbox OAuth2/OIDC)
- **Critical**: CORS whitelisted for frontend origin only (`NEXT_PUBLIC_API_URL`)

## Agent Pipeline Architecture

**Hybrid approach: LLM for judgment + deterministic math for rules:**
1. **Pre-LLM** (deterministic): Retrieve applicant, delete any old `in_progress`/`additional_info` applications for same applicant
2. **Single LLM call** (zero tools, `output_type=AgentProposal`): Reads Arabic/English remarks, identifies hardship, proposes decision + new EMI + confidence
3. **Post-LLM** (deterministic): Apply R1 cap (20% of salary), compute extended months via calculator, apply term cap (`ADDITIONAL_MONTHS`), override status to `human_review` if confidence < `settings.confidence_threshold` (0.7)
4. **5 possible outcomes**: `approved`, `rejected`, `additional_info`, `human_review`, `in_progress`
5. **No infinite loops**: No tool-calling — single LLM output, then deterministic enforcement

**Key agent files:**
- Pipeline logic: `backend/app/agent/pipeline.py:100` (`run_pipeline`)
- Business rules: `backend/app/agent/rules.py` (`apply_r1`, `apply_term_cap`)
- Calculations: `backend/app/agent/calculator.py` (extended months math)

**Debug mode:**
- `DEBUG = True` in `pipeline.py:10` prints user prompt, raw LLM conversation, structured proposal, and final AgentResult to console
- Set to `False` to silence

**R3 handling (active application):**
- Instead of rejecting new submissions, the pipeline **deletes** old pending applications (and their decisions) for the same applicant, then processes the new one normally
- Fixed in `pipeline.py:121-130`

## API Integration Details

**Critical endpoints:**
- Frontend calls: `POST {NEXT_PUBLIC_API_URL}/api/submit` (multipart FormData)
- Status polling: `GET {host}/api/applications/{id}`
- Admin access (unprotected): `GET {host}/api/decisions` (audit trail)
- Admin page: `GET /admin` at frontend

**Submit response includes:** `application_id`, `status`, `explanation`, `confidence`, `extended_months`, `new_emi`, `old_emi`

**Form submission complexity:**
- 7 fields including file uploads (PDF/JPG/PNG, ≤5 files, ≤15MB each)
- Remarks: min 20 characters required
- Agreement: checkbox for 20% salary deduction consent
- Hidden fields: `applicant_id` + `email_id` from NextAuth session
- **Docs are uploaded but not saved to disk** (accepted but discarded)

**New-applicant INSERT formula (submit.py:26-28):**
- `CURRENT_EMI_AMT = overdue_amount / max(months_delayed, 1)` (monthly rate)
- `LOAN_AMOUNT = current_emi * 12` (monthly rate × default term)
- `ADDITIONAL_MONTHS = 12` (hardcoded default term)

**CSV seeding LOAN_AMOUNT formula (database.py:118-125):**
- `LOAN_AMOUNT = CURRENT_EMI_AMT * ADDITIONAL_MONTHS` (when both available)
- Fallback: `CURRENT_EMI_AMT * max(OVER_DUE_MONTHS, 12)`

## Operational Gotchas

**Environment quirks:**
- Backend `.env`: `OPENROUTER_API_KEY` only (no other secrets)
- Frontend `.env.local`: GitHub OAuth + UAE PASS + NextAuth secrets
- Both `.env` files are **committed** (dev-only)

**No CI/CD, no tests, no lint/typecheck** – manual verification only

**Data flow:** CSV seed → SQLite (`applicants`) → Agent pipeline → `applications` + `decisions` tables

**Business logic spec:** `backend/resources/AGENT_GUIDE.md`
