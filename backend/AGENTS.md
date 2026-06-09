# Backend – FastAPI + AI Agent Pipeline

## Stack & State

- **Framework**: FastAPI (Python 3.13)
- **Database**: SQLite via python sqlite3, seeded from `housing_reschedule_with_english.csv` (28 cols, 37 KB, 100 rows)
- **AI Agent**: Pure Python rule-based modules (no external AI APIs)
- **IMPORTANT: Not yet built.** The planned `app/agent/` directory does not exist. `app/` with config, DB, init/seed, models, routes, mock submit. Agent pipeline (`app/agent/`) files pending.

## Commands

```bash
uv run uvicorn app.main:app --reload --port 8000    # dev
# Swagger at http://localhost:8000/docs
```

## Database

### `applicants` (seeded from CSV)
Key fields: `applicant_id` (TEXT PK, mapped from `EDB_CUSTOMER_ID`), `current_salary` (REAL), `over_due_amt` (REAL), `over_due_months` (INT), `deduct_from_salary` (TEXT), `remarks` (TEXT), `status` (TEXT). All 28 CSV columns stored.

### `applications` (per submission)
`id` (INT PK AUTO), `applicant_id`, `remarks`, `agreement` (bool), `status` (one of 5), `confidence` (0.0–1.0), `explanation`, `audit_data` (JSON), `created_at`.

## API Endpoints

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/submit` | Run agent pipeline, return decision (mock currently) |
| GET | `/api/applications/{id}` | Check submission status |
| GET | `/api/applicants` | List all applicants (admin) |
| GET | `/api/applicants/{id}` | Get single applicant (admin) |

## Agent Pipeline (design intent — not yet built)

Sequential per submission: **Retriever** (fetch applicant data) → **Validator** (eligibility + active app check) → **Analyzer** (financial indicators) → **Decider** (rules engine) → **Explainer** (status + plain language). Stored to `applications` table, returned as `{ application_id, status, explanation, confidence }`.

### Rules
- **R1**: Deduction ≤ 20% of income (hard)
- **R2**: New term ≤ original term (hard)
- **R3**: Active application → auto reject (hard)

### Confidence
- Range 0.0–1.0, computed from data completeness + rule match clarity
- Threshold 0.7 (configurable via `CONFIDENCE_THRESHOLD`)

## Citizen Statuses (only 5)
| Status | Trigger |
|---|---|
| In Progress | Initial |
| Additional Information Required | Agent needs more data |
| Approved | All rules pass, confidence high |
| Rejected | Rules violated |
| Human Review Required | Confidence < 0.7 or edge case |

## Audit Trail
Each submission stores JSON `audit_data`: rules checked (R1–R3), matrix path, validation results, analysis metrics, confidence breakdown. Not exposed to citizens.

## Configuration (env vars)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data.db` (resolved to backend/) | SQLite path |
| `CORS_ORIGIN` | `http://localhost:3000` | Allowed frontend origin |
| `CSV_PATH` | `housing_reschedule_with_english.csv` (resolved to backend/) | Seed CSV path |
| `CONFIDENCE_THRESHOLD` | `0.7` | Escalation threshold |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Listen port |

## File structure

```
backend/
├── pyproject.toml
├── housing_reschedule_with_english.csv
├── .venv/                          # uv-managed venv (gitignored)
├── data.db                         # SQLite (gitignored)
└── app/
    ├── __init__.py
    ├── config.py                   # pydantic-settings env config
    ├── database.py                 # sqlite3 init + CSV seed
    ├── main.py                     # FastAPI app, CORS, lifespan, routers
    ├── models/
    │   ├── __init__.py
    │   └── schemas.py              # Pydantic request/response models
    ├── routers/
    │   ├── __init__.py
    │   ├── submit.py               # POST /api/submit (mock)
    │   ├── applications.py         # GET /api/applications/{id}
    │   └── applicants.py           # GET /api/applicants, /api/applicants/{id}
    └── agent/                      # NOT YET BUILT
        ├── __init__.py
        ├── pipeline.py             # run_pipeline() — chain of stages
        ├── retriever.py
        ├── validator.py
        ├── analyzer.py
        ├── decider.py
        └── explainer.py
```
