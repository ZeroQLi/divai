from pydantic import BaseModel
from typing import Optional

class SubmitRequest(BaseModel):
    applicant_id: str
    remarks: str
    agreement: bool
    # For future: allow form overrides
    months_delayed: Optional[int] = None
    overdue_amount: Optional[float] = None
    current_salary: Optional[float] = None

class SubmitResponse(BaseModel):
    application_id: int
    status: str
    explanation: str
    confidence: float

class ApplicationOut(BaseModel):
    id: int
    applicant_id: str
    status: str
    explanation: str
    confidence: float
    created_at: str

class ApplicantOut(BaseModel):
    applicant_id: str
    # Add other CSV fields as needed
    current_salary: Optional[float]
    over_due_amt: Optional[float]
    over_due_months: Optional[int]
    status: Optional[str]
    remarks: Optional[str]