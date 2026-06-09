from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..models.schemas import ApplicantOut

router = APIRouter()

@router.get("/applicants")
def list_applicants():
    with get_db() as db:
        rows = db.execute("SELECT applicant_id, current_salary, over_due_amt, over_due_months, status, remarks FROM applicants").fetchall()
        return [dict(row) for row in rows]

@router.get("/applicants/{applicant_id}")
def get_applicant(applicant_id: str):
    with get_db() as db:
        row = db.execute("SELECT applicant_id, current_salary, over_due_amt, over_due_months, status, remarks FROM applicants WHERE applicant_id = ?", (applicant_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Applicant not found")
        return dict(row)
