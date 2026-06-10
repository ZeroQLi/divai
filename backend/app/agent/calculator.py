from . import rules


def compute_extended_months(
    overdue_amount: float,
    current_emi: float,
    new_emi: float,
    scenario: str,
    original_term_months: float = 0,
) -> int:
    """Compute additional months to extend the loan term.

    For unemployment/temporary hardship → move arrears to end.
    For reduced EMI → proportionally extend.
    Capped by the original loan term (ADDITIONAL_MONTHS).
    """
    if scenario in ("unemployment", "temporary", "medical"):
        if current_emi > 0:
            months = max(1, round(overdue_amount / current_emi))
        else:
            months = 0
    elif new_emi < current_emi and current_emi > 0:
        monthly_diff = current_emi - new_emi
        if monthly_diff > 0:
            months = round(overdue_amount / monthly_diff)
        else:
            months = 0
    else:
        months = 0

    return rules.apply_term_cap(months, original_term_months)
