def compute_extended_months(
    overdue_amount: float,
    current_emi: float,
    new_emi: float,
    scenario: str,
) -> int:
    """Compute additional months to extend the loan term.

    For unemployment/temporary hardship → move arrears to end.
    For reduced EMI → proportionally extend.
    """
    if scenario in ("unemployment", "temporary", "medical"):
        if current_emi > 0:
            return max(1, round(overdue_amount / current_emi))
        return 0

    if new_emi < current_emi and current_emi > 0:
        monthly_diff = current_emi - new_emi
        if monthly_diff > 0:
            return round(overdue_amount / monthly_diff)
    return 0
