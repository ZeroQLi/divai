# Backend – FastAPI + AI Agent Pipeline

## Stack
- **Framework**: FastAPI (Python 3.13)
- **Database**: SQLite via python sqlite3, seeded from `housing_reschedule_with_english.csv` (16 cols, 100 rows)
- **Agent**: pydantic-ai v1 with OpenRouter (`openai/gpt-4o-mini` via OpenAI-compatible API). Deterministic rule-based pipeline using an LLM for hardship context understanding (Arabic/English remarks).

## Commands

```bash
uv run uvicorn app.main:app --reload --port 8000
# Swagger at http://localhost:8000/docs
```

## Database

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

## Agent Pipeline

Sequential per submission: **Retrieve** (DB lookup) → **Check R3** (active app?) → **Read remarks** (LLM-driven Arabic/English hardship detection) → **Apply rules** (R1 cap, assessment matrix) → **Compute EMI** (deterministic tools) → **Decide** (LLM sets status + confidence).

Pipeline uses pydantic-ai `Agent` with OpenRouter (`openai/gpt-4o-mini`). The LLM reads remarks in Arabic/English for hardship context, proposes decisions, and calls Python tools for deterministic math (R1 cap, EMI, extended months).

## Environment

Create `backend/.env` (committed, dev-only) with your OpenRouter key:

```env
OPENROUTER_API_KEY=sk-or-v1-...
```

## Configuration (env vars)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data.db` (resolved to backend/) | SQLite path |
| `CORS_ORIGIN` | `http://localhost:3000` | Allowed frontend origin |
| `CSV_PATH` | `housing_reschedule_with_english.csv` (resolved to backend/) | Seed CSV path |
| `CONFIDENCE_THRESHOLD` | `0.7` | Escalation threshold |
| `OPENROUTER_API_KEY` | `""` | OpenRouter key (required for agent) |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | OpenRouter API endpoint |
| `OPENROUTER_MODEL` | `openai/gpt-4o-mini` | Model name on OpenRouter |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Listen port |

## File structure

```
backend/
├── pyproject.toml
├── housing_reschedule_with_english.csv
├── .venv/
├── data.db
└── app/
    ├── __init__.py
    ├── config.py
    ├── database.py
    ├── main.py
    ├── agent/                   # Agent pipeline (built)
    │   ├── __init__.py
    │   ├── pipeline.py          # pydantic-ai Agent + tools + run_pipeline()
    │   ├── models.py            # AgentResult, AgentDeps
    │   ├── rules.py             # R1, R3, confidence scoring
    │   └── calculator.py        # Extended months computation
    ├── models/
    │   ├── __init__.py
    │   └── schemas.py
    └── routers/
        ├── __init__.py
        ├── submit.py            # POST /api/submit (+ GET /api/decisions)
        ├── applications.py
        └── applicants.py
```
