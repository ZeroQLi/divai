# Backend – FastAPI + AI Agent Pipeline

## Critical Commands & Setup

**Exact startup commands:**
```bash
uv run uvicorn app.main:app --reload --port 8000
# Swagger: http://localhost:8000/docs
```

**Database setup (auto-run):**
- First backend start reads `housing_reschedule_with_english.csv` (28 cols, 100 rows) into `applicants` table
- LOAN_AMOUNT is calculated as `CURRENT_EMI_AMT * ADDITIONAL_MONTHS` (fallback: `CURRENT_EMI_AMT * max(OVER_DUE_MONTHS, 12)`)
- Manual inspection: `uv run sqlite_web data.db --port 8080`

**Environment setup:**
- Create `backend/.env` with ONLY: `OPENROUTER_API_KEY=sk-or-v1-...`
- Environment resolves paths to backend/ directory automatically

## Agent Pipeline Mechanics

**Hybrid approach (no tools):**
1. **Pre-LLM** → Retrieve applicant from DB
2. **Pre-LLM** → Delete old pending applications (`in_progress`/`additional_info`) for same applicant
3. **Single LLM call** → Read Arabic/English remarks, identify hardship scenario, propose status + new EMI + confidence (output_type=AgentProposal)
4. **Post-LLM** → Apply R1 cap (20% of salary via `rules.apply_r1`)
5. **Post-LLM** → Compute extended months via `calculator.compute_extended_months` + `rules.apply_term_cap`
6. **Post-LLM** → Override status to `human_review` if confidence < `settings.confidence_threshold` (default 0.7)

**Agent architecture quirks:**
- Uses pydantic-ai v1 with OpenRouter (`google/gemma-4-26b-a4b-it`)
- Zero tools — single LLM call with `output_type=AgentProposal`
- LLM reads Arabic/English remarks for hardship context (scenarios: unemployment, medical, temporary, financial_difficulty, normal)
- All financial math is deterministic post-LLM (not embedded in LLM response)
- 5 statuses: `in_progress`, `additional_info`, `approved`, `rejected`, `human_review`
- **Critical**: Confidence < `settings.confidence_threshold` (0.7) → `human_review`

## Framework-Specific Implementation

**Python/fastapi quirks:**
- Uses `uv` for dependency management (not pip)
- SQLite via python's built-in sqlite3 (not SQLAlchemy/ORM)
- Database path resolution: `DATABASE_URL` resolves to backend/
- No type checking or linting pipeline

**Critical file locations:**
```
backend/app/agent/pipeline.py:100  # run_pipeline()
backend/app/agent/rules.py:1       # apply_r1, apply_term_cap
backend/app/agent/calculator.py:1  # compute_extended_months
backend/app/routers/submit.py:12   # POST /api/submit
```

**Debug mode:**
- `DEBUG = True` in `pipeline.py:10` prints user prompt, raw LLM conversation, AgentProposal, and final AgentResult to console
- Set to `False` to silence

## Database Schema

### `applicants` (seeded from CSV)
`applicant_id` (TEXT PK from `EDB_CUSTOMER_ID`), `EMAIL_ID`, `APPLICATION_ID`, `LOAN_AMOUNT`, `CURRENT_SALARY`, `OVER_DUE_AMT`, `OVER_DUE_MONTHS`, `CURRENT_EMI_AMT`, `NEW_EMI_AMT`, `CREATED_DATE`, `STATUS`, `APPROVED_DATE`, `JUSTIFICATIONS`, `REMARKS`, `ADDITIONAL_MONTHS`, `REMARKS_EN`.

### `applications` (per submission)
`id` (INT PK AUTO), `applicant_id`, `months_delayed`, `overdue_amount`, `current_salary`, `remarks`, `agreement`, `status`, `confidence`, `explanation`, `extended_months` (INT, default 0), `audit_data` (JSON), `created_at`.

### `decisions` (agent output audit trail)
`id` (INT PK AUTO), `application_id` (FK → applications), `applicant_id`, `loan_amount`, `old_emi`, `new_emi`, `extended_months`, `confidence`, `justification`, `status`, `explanation`, `created_at`.

## API Endpoints

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/submit` | Run agent pipeline, store result, return decision |
| GET | `/api/applications/{id}` | Check submission status |
| GET | `/api/applicants` | List all applicants |
| GET | `/api/applicants/{id}` | Get single applicant |
| GET | `/api/decisions` | List all decisions (for admin dashboard — no auth) |
| GET | `/api/decisions/{id}` | Get single decision |

## Framework Quirks & Gotchas

**Python/fastapi specifics:**
- Uses `uv` for dependency management (not pip)
- SQLite via python's built-in sqlite3 (not SQLAlchemy/ORM)
- Agent pipeline uses pydantic-ai v1 with OpenRouter (`google/gemma-4-26b-a4b-it`)
- **Critical**: Database path resolution (`DATABASE_URL` resolves to backend/)

**Agent implementation quirks:**
- Hybrid pre/post LLM architecture with zero tools
- Confidence threshold via `settings.confidence_threshold` (not hardcoded)
- 5 possible outcomes: `approved`, `rejected`, `additional_info`, `human_review`, `in_progress`
- LLM reads Arabic/English for hardship context
- Old pending applications are DELETED (not rejected) when new submission arrives
- Unprotected admin endpoint: `GET /api/decisions`

**New-applicant INSERT formula (submit.py:26-28):**
- `CURRENT_EMI_AMT = overdue_amount / max(months_delayed, 1)` (monthly rate)
- `LOAN_AMOUNT = current_emi * 12` (monthly rate × default term)
- `ADDITIONAL_MONTHS = 12` (hardcoded default term)

**Submit response includes:** `application_id`, `status`, `explanation`, `confidence`, `extended_months`, `new_emi`, `old_emi`
