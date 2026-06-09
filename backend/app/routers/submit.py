from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Optional
from ..models.schemas import SubmitResponse
from ..database import get_db
import datetime
import json

router = APIRouter()

@router.post("/submit", response_model=SubmitResponse)
def submit_application(
    applicant_id: str = Form(...),
    email_id: str = Form(""),
    months_delayed: int = Form(...),
    overdue_amount: float = Form(...),
    current_salary: float = Form(...),
    remarks: str = Form(...),
    agreement: bool = Form(...),
    docs: Optional[List[UploadFile]] = File(None)
):
    status = "in_progress"
    explanation = "Your request is being reviewed."
    confidence = 0.0

    with get_db() as db:
        existing = db.execute("SELECT applicant_id FROM applicants WHERE applicant_id = ?", (applicant_id,)).fetchone()
        if not existing:
            db.execute(
                """
                INSERT INTO applicants (
                    applicant_id, EMAIL_ID, CURRENT_SALARY, OVER_DUE_AMT, OVER_DUE_MONTHS,
                    LOAN_AMOUNT, STATUS
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    applicant_id,
                    email_id,
                    current_salary,
                    overdue_amount,
                    months_delayed,
                    overdue_amount * 3,
                    "NEW"
                ]
            )

        cur = db.execute(
            """
            INSERT INTO applications (applicant_id, months_delayed, overdue_amount, current_salary, remarks, agreement, status, confidence, explanation, audit_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                applicant_id,
                months_delayed,
                overdue_amount,
                current_salary,
                remarks,
                agreement,
                status,
                confidence,
                explanation,
                json.dumps({"version": "1.0"}),
                datetime.datetime.utcnow().isoformat()
            ]
        )
        app_id = cur.lastrowid
        db.commit()
    return {
        "application_id": app_id,
        "status": status,
        "explanation": explanation,
        "confidence": confidence
    }

