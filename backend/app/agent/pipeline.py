import json

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from ..config import settings
from .models import AgentResult, AgentProposal
from . import rules, calculator

DEBUG = True


SYSTEM_PROMPT = """You are a loan rescheduling officer for the Sheikh Zayed Housing Programme (Ministry of Energy and Infrastructure, UAE).

Evaluate the rescheduling request and output your proposal.

1. **IDENTIFY THE SCENARIO** from the applicant's stored remarks and their new form submission. Remarks may be in **Arabic or English**. Choose one:
   - `unemployment` — lost job, no stable income
   - `medical` — health treatment, medical bills
   - `temporary` — travel, official assignment, temporary circumstance
   - `financial_difficulty` — high obligations, debt
   - `normal` — no special hardship

2. **PROPOSE A DECISION**:
   - Status must be one of: `approved`, `rejected`, `additional_info`, `human_review`, `in_progress`
   - `confidence`: 0.0–1.0 based on data completeness, clarity of the case, and hardship clarity
   - If hardship is detected but unclear → `human_review`

3. **PROPOSE A NEW EMI** — Based on the applicant's salary, current EMI, and hardship, propose a reasonable new monthly payment amount.

4. **OUTPUT** your proposal as structured data. The system will handle all financial calculations (R1 cap, EMI computation, extended months)."""


def _debug_log(label: str, content: str):
    if not DEBUG:
        return
    border = "=" * 70
    print(f"\n{border}")
    print(f"  {label}")
    print(border)
    print(content)
    print()


def _debug_messages(messages):
    if not DEBUG:
        return
    for msg in messages:
        for part in msg.parts:
            kind = part.part_kind
            if kind == "system-prompt":
                continue
            if kind == "user-prompt":
                print(f"\n--- USER ---\n{part.content}")
            elif kind == "model-text":
                print(f"\n--- MODEL TEXT ---\n{part.content}")
            elif kind == "tool-call":
                print(f"\n--- STRUCTURED OUTPUT ({part.tool_name}) ---")
                try:
                    parsed = json.loads(part.args)
                    print(json.dumps(parsed, indent=2))
                except (json.JSONDecodeError, TypeError):
                    print(part.args)
    if DEBUG:
        print()

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
        output_type=AgentProposal,
        system_prompt=SYSTEM_PROMPT,
        model_settings={"max_tokens": 1000},
    )

    _agent = agent
    return agent


def run_pipeline(
    applicant_id: str,
    form_data: dict,
    db,
) -> AgentResult:
    """Run the agent pipeline for a rescheduling application.

    Pre-LLM (deterministic): Retrieve applicant, check R3.
    LLM (single call): Identify hardship scenario, propose decision.
    Post-LLM (deterministic): Apply R1 cap, compute extended months, term cap.
    """
    # --- Pre-LLM: retrieve applicant ---
    row = db.execute(
        """SELECT applicant_id, EMAIL_ID, LOAN_AMOUNT, CURRENT_SALARY,
                  OVER_DUE_AMT, OVER_DUE_MONTHS, CURRENT_EMI_AMT, NEW_EMI_AMT,
                  STATUS, JUSTIFICATIONS, REMARKS, ADDITIONAL_MONTHS, REMARKS_EN
           FROM applicants WHERE applicant_id = ?""",
        (applicant_id,),
    ).fetchone()
    applicant = dict(row) if row else None

    # --- Pre-LLM: clear old pending applications for this applicant ---
    old = db.execute(
        "SELECT id FROM applications WHERE applicant_id = ? AND status IN ('in_progress', 'additional_info')",
        (applicant_id,),
    ).fetchall()
    if old:
        old_ids = [row["id"] for row in old]
        placeholders = ",".join("?" for _ in old_ids)
        db.execute(f"DELETE FROM decisions WHERE application_id IN ({placeholders})", old_ids)
        db.execute(f"DELETE FROM applications WHERE id IN ({placeholders})", old_ids)

    # --- Build user prompt ---
    if applicant:
        applicant_info = (
            f"Applicant: {applicant_id}\n"
            f"Loan amount: {applicant.get('LOAN_AMOUNT')}\n"
            f"Current salary: {applicant.get('CURRENT_SALARY')}\n"
            f"Current EMI: {applicant.get('CURRENT_EMI_AMT')}\n"
            f"Overdue amount: {applicant.get('OVER_DUE_AMT')}\n"
            f"Overdue months: {applicant.get('OVER_DUE_MONTHS')}\n"
            f"Stored remarks: {applicant.get('REMARKS') or ''}\n"
            f"Stored remarks (EN): {applicant.get('REMARKS_EN') or ''}\n"
        )
    else:
        applicant_info = f"Applicant: {applicant_id} (no existing record)\n"

    user_prompt = (
        f"{applicant_info}\n"
        f"Form submission:\n"
        f"- Salary: {form_data.get('current_salary')}\n"
        f"- Overdue amount: {form_data.get('overdue_amount')}\n"
        f"- Months delayed: {form_data.get('months_delayed')}\n"
        f"- Remarks: {form_data.get('remarks', '')}\n"
        f"- Agreement (deduct up to 20%): {form_data.get('agreement')}"
    )

    # --- LLM call: single call, no tools ---
    _debug_log("USER PROMPT TO LLM", user_prompt)

    agent = _get_agent()
    result = agent.run_sync(user_prompt)

    _debug_log("RAW LLM CONVERSATION", "")
    _debug_messages(result.all_messages())

    proposal = result.output
    _debug_log("STRUCTURED OUTPUT (AgentProposal)", json.dumps(proposal.model_dump(), indent=2))

    # --- Post-LLM: deterministic financial calculations ---
    current_emi = (applicant.get("CURRENT_EMI_AMT") or 0.0) if applicant else 0.0
    salary = (
        (applicant.get("CURRENT_SALARY") or form_data.get("current_salary", 0.0))
        if applicant
        else form_data.get("current_salary", 0.0)
    )
    r1_cap = rules.apply_r1(salary)
    new_emi = round(min(proposal.proposed_new_emi, r1_cap), 2)

    overdue_amount = form_data.get("overdue_amount", 0.0)
    original_term = (applicant.get("ADDITIONAL_MONTHS") or 0.0) if applicant else 0.0
    extended_months = calculator.compute_extended_months(
        overdue_amount, current_emi, new_emi, proposal.scenario, original_term
    )

    confidence = proposal.confidence
    status = proposal.status
    if confidence < settings.confidence_threshold:
        status = "human_review"

    final_result = AgentResult(
        new_emi=new_emi,
        extended_months=extended_months,
        confidence=confidence,
        status=status,
        explanation=proposal.explanation,
        justification=proposal.justification,
    )

    _debug_log("FINAL RESULT (AgentResult)", json.dumps(final_result.model_dump(), indent=2))

    return final_result
