# Backend – FastAPI + AI Agent Pipeline

## State
**Agent pipeline NOT built.** `app/agent/` does not exist. The POST `/api/submit` endpoint inserts an application row with `status="in_progress"` — no AI decision logic runs. That is the next thing to implement.

## Stack

- **Framework**: FastAPI (Python 3.13)
- **Database**: SQLite via python sqlite3, seeded from `housing_reschedule_with_english.csv` (16 cols, 100 rows)

## Commands

```bash
uv run uvicorn app.main:app --reload --port 8000
# Swagger at http://localhost:8000/docs
```

## Database

### `applicants` (seeded from CSV)
`applicant_id` (TEXT PK from `EDB_CUSTOMER_ID`), `EMAIL_ID`, `APPLICATION_ID`, `LOAN_AMOUNT`, `CURRENT_SALARY`, `OVER_DUE_AMT`, `OVER_DUE_MONTHS`, `CURRENT_EMI_AMT`, `NEW_EMI_AMT`, `CREATED_DATE`, `STATUS`, `APPROVED_DATE`, `JUSTIFICATIONS`, `REMARKS`, `ADDITIONAL_MONTHS`, `REMARKS_EN`.

### `applications` (per submission)
`id` (INT PK AUTO), `applicant_id`, `months_delayed`, `overdue_amount`, `current_salary`, `remarks`, `agreement`, `status`, `confidence`, `explanation`, `audit_data` (JSON), `created_at`.

## API Endpoints

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/submit` | Accept form-data, create applicant (if new), insert application row |
| GET | `/api/applications/{id}` | Check submission status |
| GET | `/api/applicants` | List all applicants |
| GET | `/api/applicants/{id}` | Get single applicant |

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
├── .venv/
├── data.db
└── app/
    ├── __init__.py
    ├── config.py
    ├── database.py
    ├── main.py
    ├── models/
    │   ├── __init__.py
    │   └── schemas.py
    └── routers/
        ├── __init__.py
        ├── submit.py
        ├── applications.py
        └── applicants.py
```
