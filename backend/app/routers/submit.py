from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from ..models.schemas import SubmitResponse, DecisionOut
from ..database import get_db
from ..agent import run_pipeline
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
    with get_db() as db:
        existing = db.execute("SELECT applicant_id FROM applicants WHERE applicant_id = ?", (applicant_id,)).fetchone()
        if not existing:
            monthly_rate = overdue_amount / max(months_delayed, 1)
            current_emi = round(monthly_rate, 2)
            loan_amount = round(current_emi * 12, 2)
            db.execute(
                """
                INSERT INTO applicants (
                    applicant_id, EMAIL_ID, CURRENT_SALARY, OVER_DUE_AMT, OVER_DUE_MONTHS,
                    LOAN_AMOUNT, STATUS, ADDITIONAL_MONTHS, CURRENT_EMI_AMT,
                    REMARKS, REMARKS_EN
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    applicant_id,
                    email_id,
                    current_salary,
                    overdue_amount,
                    months_delayed,
                    loan_amount,
                    "NEW",
                    12,
                    current_emi,
                    remarks,
                    remarks,
                ]
            )

        form_data = {
            "email_id": email_id,
            "months_delayed": months_delayed,
            "overdue_amount": overdue_amount,
            "current_salary": current_salary,
            "remarks": remarks,
            "agreement": agreement,
        }

        result = run_pipeline(applicant_id, form_data, db)

        audit = json.dumps({
            "justification": result.justification,
            "new_emi": result.new_emi,
            "extended_months": result.extended_months,
        })

        cur = db.execute(
            """
            INSERT INTO applications (applicant_id, months_delayed, overdue_amount, current_salary, remarks, agreement, status, confidence, explanation, extended_months, audit_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                applicant_id,
                months_delayed,
                overdue_amount,
                current_salary,
                remarks,
                agreement,
                result.status,
                result.confidence,
                result.explanation,
                result.extended_months,
                audit,
                datetime.datetime.utcnow().isoformat()
            ]
        )
        app_id = cur.lastrowid

        applicant_row = db.execute(
            "SELECT LOAN_AMOUNT, CURRENT_EMI_AMT FROM applicants WHERE applicant_id = ?",
            (applicant_id,),
        ).fetchone()
        loan_amount = dict(applicant_row)["LOAN_AMOUNT"] if applicant_row else None
        old_emi = dict(applicant_row)["CURRENT_EMI_AMT"] if applicant_row else None

        db.execute(
            """
            INSERT INTO decisions (application_id, applicant_id, loan_amount, old_emi, new_emi, extended_months, confidence, justification, status, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                app_id,
                applicant_id,
                loan_amount if loan_amount else None,
                old_emi if old_emi else None,
                result.new_emi,
                result.extended_months,
                result.confidence,
                result.justification,
                result.status,
                result.explanation,
            ]
        )

        db.execute(
            "UPDATE applicants SET NEW_EMI_AMT = ?, STATUS = ? WHERE applicant_id = ?",
            [result.new_emi, result.status, applicant_id],
        )

        db.commit()

    return {
        "application_id": app_id,
        "status": result.status,
        "explanation": result.explanation,
        "confidence": result.confidence,
        "extended_months": result.extended_months,
        "new_emi": result.new_emi,
        "old_emi": old_emi,
    }


@router.get("/decisions", response_model=List[DecisionOut])
def list_decisions():
    """List all decisions (for admin dashboard)."""
    with get_db() as db:
        rows = db.execute(
            """SELECT id, application_id, applicant_id,
                      NULLIF(loan_amount, '') AS loan_amount,
                      NULLIF(old_emi, '') AS old_emi,
                      new_emi, extended_months, confidence, justification,
                      status, explanation, created_at
               FROM decisions ORDER BY created_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]


@router.get("/decisions/{decision_id}", response_model=DecisionOut)
def get_decision(decision_id: int):
    """Get a single decision by ID."""
    with get_db() as db:
        row = db.execute(
            """SELECT id, application_id, applicant_id,
                      NULLIF(loan_amount, '') AS loan_amount,
                      NULLIF(old_emi, '') AS old_emi,
                      new_emi, extended_months, confidence, justification,
                      status, explanation, created_at
               FROM decisions WHERE id = ?""",
            (decision_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Decision not found")
        return dict(row)

