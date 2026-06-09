# divai

Housing Loan Arrears Rescheduling AI Agent.

## Prerequisites

- Python 3.13+, [uv](https://docs.astral.sh/uv/)
- Node.js 18+, [pnpm](https://pnpm.io/) (or npm)

## Quick Start

```bash
# 1. Clone
git clone <repo-url> && cd divai

# 2. Backend — install & start (port 8000)
cd backend
uv sync                    # install dependencies
uv run dev                 # starts uvicorn with hot reload

# 3. Frontend — install & start (port 3000, separate terminal)
cd frontend
pnpm install               # install dependencies
pnpm dev
```

Open `http://localhost:3000` (frontend) and `http://localhost:8000/docs` (Swagger).

## Database

The backend uses SQLite (`backend/data.db`, gitignored). To browse it with a web UI:

```bash
cd backend
uv run sqlite_web data.db --port 8080
# open http://localhost:8080
```

### Seeding

On first startup the backend reads `backend/housing_reschedule_with_english.csv` (28 columns, 100 rows) and populates the `applicants` table automatically.
