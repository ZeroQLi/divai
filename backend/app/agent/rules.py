def apply_r1(salary: float) -> float:
    """Rule 1: max monthly deduction = 20% of income."""
    if salary <= 0:
        return 0
    return round(salary * 0.20, 2)


def apply_term_cap(extended_months: int, original_term_months: float) -> int:
    """Cap extended months so total repayment period doesn't exceed original term.
    
    Args:
        extended_months: Proposed extension in months.
        original_term_months: Original loan term from ADDITIONAL_MONTHS.
    Returns:
        Capped extended months (0 if original term is unknown/0).
    """
    if original_term_months <= 0:
        return extended_months
    return min(extended_months, int(original_term_months))
