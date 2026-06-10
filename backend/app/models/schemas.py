from pydantic import BaseModel
from typing import Optional

class SubmitRequest(BaseModel):
    applicant_id: str
    email_id: str
    months_delayed: int
    overdue_amount: float
    current_salary: float
    remarks: str
    agreement: bool

class SubmitResponse(BaseModel):
    application_id: int
    status: str
    explanation: str
    confidence: float
    extended_months: int = 0
    new_emi: float = 0
    old_emi: Optional[float] = None

class ApplicationOut(BaseModel):
    id: int
    applicant_id: str
    status: str
    explanation: str
    confidence: float
    extended_months: int = 0
    created_at: str

class ApplicantOut(BaseModel):
    applicant_id: str
    email_id: Optional[str] = None
    current_salary: Optional[float] = None
    over_due_amt: Optional[float] = None
    over_due_months: Optional[int] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

class DecisionOut(BaseModel):
    id: int
    application_id: int
    applicant_id: str
    loan_amount: Optional[float] = None
    old_emi: Optional[float] = None
    new_emi: float
    extended_months: int = 0
    confidence: float
    justification: str
    status: str
    explanation: str
    created_at: str