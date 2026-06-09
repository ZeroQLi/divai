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
    remarks: str = Form(...),
    agreement: bool = Form(...),
    docs: Optional[List[UploadFile]] = File(None)
):
    # Mock agent logic — update to real agent later
    status = "in_progress"
    explanation = "Your request is being reviewed. (mock)"
    confidence = 0.0

    # Insert application
    with get_db() as db:
        cur = db.execute(
            """
            INSERT INTO applications (applicant_id, remarks, agreement, status, confidence, explanation, audit_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                applicant_id,
                remarks,
                agreement,
                status,
                confidence,
                explanation,
                json.dumps({"phase": "mock"}),
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

# To use real agent, replace above logic with:
# from app.agent.pipeline import run_pipeline
# result = run_pipeline(applicant_id, ...)
