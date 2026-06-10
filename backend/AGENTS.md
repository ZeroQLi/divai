# Backend – FastAPI + AI Agent Pipeline

## Critical Commands & Setup

**Exact startup commands:**
```bash
uv run uvicorn app.main:app --reload --port 8000
# Swagger: http://localhost:8000/docs
```

**Database setup (auto-run):**
- First backend start reads `housing_reschedule_with_english.csv` (28 cols, 100 rows) into `applicants` table
- Manual inspection: `uv run sqlite_web data.db --port 8080`

**Environment setup:**
- Create `backend/.env` with ONLY: `OPENROUTER_API_KEY=sk-or-v1-...`
- Environment resolves paths to backend/ directory automatically

## Agent Pipeline Mechanics

**6-step sequential process:**
1. **Retrieve** → DB lookup (`retrieve_applicant` tool)
2. **Check R3** → Active application detection (`check_r3` tool) 
3. **Read remarks** → Arabic/English hardship detection (LLM-driven)
4. **Apply rules** → R1 cap, assessment matrix (`apply_r1_cap` tool)
5. **Compute EMI** → Capped new EMI (`compute_new_emi_amount` tool)
6. **Decide** → Status + confidence + justification

**Agent architecture quirks:**
- Uses pydantic-ai v1 with OpenRouter (`openai/gpt-4o-mini`)
- LLM reads Arabic/English remarks for hardship context
- All calculations are tools (not embedded in LLM response)
- 5 statuses: `in_progress`, `additional_info`, `approved`, `rejected`, `human_review`
- **Critical**: Confidence <0.7 automatically → `human_review`

## Framework-Specific Implementation

**Python/fastapi quirks:**
- Uses `uv` for dependency management (not pip)
- SQLite via python's built-in sqlite3 (not SQLAlchemy/ORM)
- Database path resolution: `DATABASE_URL` resolves to backend/
- No type checking or linting pipeline

**Critical file locations:**
```
backend/app/agent/pipeline.py:158  # run_pipeline()
backend/app/agent/rules.py:4      # R1, R2, R3, confidence scoring
backend/app/agent/calculator.py:1  # Extended months math
backend/app/routers/submit.py:15   # POST /api/submit
```

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
- Agent pipeline uses pydantic-ai v1 with OpenRouter (`openai/gpt-4o-mini`)
- **Critical**: Database path resolution (`DATABASE_URL` resolves to backend/)

**Agent implementation quirks:**
- Sequential 6-step pipeline with deterministic tools
- Confidence threshold: <0.7 → `human_review`
- 5 possible outcomes: `approved`, `rejected`, `additional_info`, `human_review`, `in_progress`
- LLM reads Arabic/English for hardship context
- Unprotected admin endpoint: `GET /api/decisions`
