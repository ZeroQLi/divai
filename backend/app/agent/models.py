from pydantic import BaseModel
from typing import Optional, Any


class AgentResult(BaseModel):
    new_emi: float
    extended_months: int
    confidence: float
    status: str
    explanation: str
    justification: str


class AgentDeps:
    def __init__(self, db: Any, applicant_id: str, form_data: dict):
        self.db = db
        self.applicant_id = applicant_id
        self.form_data = form_data
