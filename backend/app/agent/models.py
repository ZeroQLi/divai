from pydantic import BaseModel


class AgentResult(BaseModel):
    new_emi: float
    extended_months: int
    confidence: float
    status: str
    explanation: str
    justification: str


class AgentProposal(BaseModel):
    scenario: str
    proposed_new_emi: float
    status: str
    confidence: float
    explanation: str
    justification: str
