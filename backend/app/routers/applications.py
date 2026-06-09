from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..models.schemas import ApplicationOut

router = APIRouter()

@router.get("/applications/{id}", response_model=ApplicationOut)
def get_application(id: int):
    with get_db() as db:
        row = db.execute("SELECT id, applicant_id, status, explanation, confidence, created_at FROM applications WHERE id = ?", (id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Application not found")
        return dict(row)
