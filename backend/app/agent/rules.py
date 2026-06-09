from typing import Optional, Any


def check_r3(applicant: Optional[dict]) -> dict:
    """Rule 3: existing active application → auto reject."""
    if not applicant:
        return {"active": False, "status": None}
    status = (applicant.get("STATUS") or "").strip().upper()
    active = status in ("NEW", "IN_PROGRESS", "PENDING")
    return {"active": active, "status": status}


def apply_r1(salary: float) -> float:
    """Rule 1: max monthly deduction = 20% of income."""
    if salary <= 0:
        return 0
    return round(salary * 0.20, 2)


def apply_r2(extended_months: int, additional_months: Optional[float]) -> bool:
    """Rule 2: proposed extension is within reasonable limits."""
    if extended_months <= 60:
        return True
    if additional_months and additional_months > 0:
        return extended_months <= additional_months * 2
    return False


def compute_confidence(
    applicant: Optional[dict],
    data_completeness: float,
    hardship_clarity: float,
    rule_clarity: float,
) -> float:
    """
    Weighted confidence:
    - data_completeness (40%) — are salary, EMI, arrears present?
    - hardship_clarity (30%)   — how clearly did the LLM identify hardship?
    - rule_clarity (30%)       — does the case follow a clear matrix path?
    """
    score = data_completeness * 0.40 + hardship_clarity * 0.30 + rule_clarity * 0.30
    return round(min(max(score, 0), 1), 2)


def data_completeness_score(applicant: Optional[dict]) -> float:
    if not applicant:
        return 0.0
    fields = ["CURRENT_SALARY", "CURRENT_EMI_AMT", "OVER_DUE_AMT", "OVER_DUE_MONTHS", "LOAN_AMOUNT"]
    present = sum(1 for f in fields if applicant.get(f) is not None)
    return present / len(fields)
