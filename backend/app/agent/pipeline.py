from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from ..config import settings
from .models import AgentResult, AgentDeps
from . import rules, calculator


SYSTEM_PROMPT = """You are a loan rescheduling officer for the Sheikh Zayed Housing Programme (Ministry of Energy and Infrastructure, UAE).

Your task is to evaluate each rescheduling request step by step:

1. **RETRIEVE** — Call `retrieve_applicant` to fetch the applicant's loan record.
2. **CHECK R3 (active application)** — If the applicant already has a NEW/IN_PROGRESS/PENDING application, the status must be `rejected`.
3. **READ THE REMARKS** — The applicant's stored remarks (`REMARKS`, `REMARKS_EN`) and their new form submission (`remarks`) may contain hardship context. Read them carefully — they may be in **Arabic or English**. Identify the scenario:
   - `unemployment` — lost job, no stable income
   - `medical` — health treatment, medical bills
   - `temporary` — travel, official assignment, temporary circumstance
   - `financial_difficulty` — high obligations, debt, over 60% income-to-obligation
   - `normal` — no special hardship
4. **APPLY THE MATRIX**:
   - Income increased → EMI may increase up to the R1 cap (20% of salary)
   - Income decreased → maintain or reduce current EMI
   - Obligations > 60% → reduce increase or route to human_review
   - Unemployment → keep current EMI, move arrears to end of term
   - Temporary circumstances → keep current EMI, postpone increase
   - Medical / hardship → keep current EMI, extend term
5. **USE TOOLS FOR MATH** — Call `apply_r1_cap`, `compute_new_emi_amount`, and `compute_extended_months_count` for all financial calculations. Do not compute these yourself.
6. **DECIDE** — Set `status`, `confidence`, `explanation`, and `justification`:
   - Status must be one of: `approved`, `rejected`, `additional_info`, `human_review`, `in_progress`
   - `confidence`: 0.0–1.0 based on data completeness, clarity of the case, and hardship clarity
   - If hardship is detected but unclear → `human_review`
   - If R3 active → `rejected`
   - If rules pass clearly → `approved`
   - `explanation` is a short citizen-facing message in plain English
   - `justification` is a 2–3 sentence internal audit remark explaining what was decided and why

IMPORTANT: The applicant's remarks may be in Arabic. Read them with the same care as English text.
"""


_agent = None


def _get_agent() -> Agent:
    global _agent
    if _agent is not None:
        return _agent

    if not settings.openrouter_api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Add it to backend/.env: "
            "OPENROUTER_API_KEY=sk-or-v1-..."
        )

    model = OpenAIChatModel(
        settings.openrouter_model,
        provider=OpenAIProvider(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
        ),
    )

    agent = Agent(
        model,
        output_type=AgentResult,
        deps_type=AgentDeps,
        system_prompt=SYSTEM_PROMPT,
        model_settings={"max_tokens": 2000},
    )

    @agent.tool
    async def retrieve_applicant(ctx: RunContext[AgentDeps]) -> dict | None:
        """Fetch the applicant's full loan record from the database.

        Returns a dict with keys: applicant_id, CURRENT_SALARY, CURRENT_EMI_AMT,
        OVER_DUE_AMT, OVER_DUE_MONTHS, LOAN_AMOUNT, REMARKS, REMARKS_EN,
        STATUS, ADDITIONAL_MONTHS, NEW_EMI_AMT, JUSTIFICATIONS, EMAIL_ID.
        Returns None if the applicant is not found.
        """
        row = ctx.deps.db.execute(
            """SELECT applicant_id, EMAIL_ID, LOAN_AMOUNT, CURRENT_SALARY,
                      OVER_DUE_AMT, OVER_DUE_MONTHS, CURRENT_EMI_AMT, NEW_EMI_AMT,
                      STATUS, JUSTIFICATIONS, REMARKS, ADDITIONAL_MONTHS, REMARKS_EN
               FROM applicants WHERE applicant_id = ?""",
            (ctx.deps.applicant_id,),
        ).fetchone()
        if not row:
            return None
        return dict(row)

    @agent.tool
    async def check_r3(ctx: RunContext[AgentDeps], applicant: dict) -> dict:
        """Check if the applicant has an active application (Rule 3).

        Args:
            applicant: The applicant dict from retrieve_applicant.
        Returns:
            {'active': bool, 'status': str or None}
        """
        return rules.check_r3(applicant)

    @agent.tool
    async def apply_r1_cap(ctx: RunContext[AgentDeps], salary: float) -> float:
        """Compute the maximum allowed monthly EMI under Rule 1 (20% of salary).

        Args:
            salary: The applicant's monthly income.
        Returns:
            Maximum permitted EMI amount.
        """
        return rules.apply_r1(salary)

    @agent.tool
    async def compute_new_emi_amount(
        ctx: RunContext[AgentDeps],
        current_emi: float,
        proposed_emi: float,
        max_allowed: float,
    ) -> float:
        """Compute the final new EMI, capped at max_allowed by Rule 1.

        Args:
            current_emi: The applicant's current monthly EMI.
            proposed_emi: The officer's proposed new EMI.
            max_allowed: The R1 cap (20% of salary).
        Returns:
            The final new EMI amount.
        """
        return round(min(proposed_emi, max_allowed), 2)

    @agent.tool
    async def compute_extended_months_count(
        ctx: RunContext[AgentDeps],
        overdue_amount: float,
        current_emi: float,
        new_emi: float,
        scenario: str,
    ) -> int:
        """Compute how many additional months to extend the loan term.

        Args:
            overdue_amount: Total overdue amount.
            current_emi: Current monthly EMI.
            new_emi: The proposed new EMI.
            scenario: The hardship scenario (unemployment, temporary, medical, etc.).
        Returns:
            Number of additional months to extend.
        """
        return calculator.compute_extended_months(
            overdue_amount, current_emi, new_emi, scenario
        )

    _agent = agent
    return agent


def run_pipeline(
    applicant_id: str,
    form_data: dict,
    db,
) -> AgentResult:
    """Run the agent pipeline for a rescheduling application.

    Args:
        applicant_id: The applicant's ID.
        form_data: Dict with keys: email_id, months_delayed, overdue_amount,
                   current_salary, remarks, agreement.
        db: An active sqlite3 connection (dict cursor).
    Returns:
        An AgentResult with new_emi, extended_months, confidence, status,
        explanation, and justification.
    """
    agent = _get_agent()
    deps = AgentDeps(db=db, applicant_id=applicant_id, form_data=form_data)

    user_prompt = (
        f"Process rescheduling for applicant {applicant_id}.\n\n"
        f"Form submission:\n"
        f"- Salary: {form_data.get('current_salary')}\n"
        f"- Overdue amount: {form_data.get('overdue_amount')}\n"
        f"- Months delayed: {form_data.get('months_delayed')}\n"
        f"- Remarks: {form_data.get('remarks', '')}\n"
        f"- Agreement (deduct up to 20%): {form_data.get('agreement')}"
    )

    result = agent.run_sync(user_prompt, deps=deps)
    return result.output
