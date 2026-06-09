# AI Agent Challenge for Housing Loan Arrears Rescheduling Guide

# Sheikh Zayed Housing Programme | Ministry of Energy and Infrastructure

**What is this challenge?**

This is not a chatbot challenge.

The objective is to build an AI Agent that performs the role of a government officer reviewing housing loan arrears
rescheduling requests and providing recommendations automatically.

**Ultimate Goal**

Reduce service completion time from:

**Approximately 5 working days** to **Instant or near-instant service**

while maintaining:

- Fairness
- Transparency
- Governance
- Consistency

**Who is the beneficiary?**

The beneficiary is:

A UAE National

A housing loan beneficiary under the Sheikh Zayed Housing Programme

A citizen with accumulated loan arrears requesting rescheduling


**Current Challenge**

Today, the process relies heavily on manual review:

1. Receive request
2. Review documents
3. Validate information
4. Assess financial situation
5. Calculate repayment capacity
6. Make a recommendation

This results in:

- Longer processing times
- Increased manual workload
- Inconsistent decisions
- Limited ability to process straightforward cases instantly

**What should the AI Agent do?**

The Agent should:

**Validate**

- Applicant eligibility
- Existing active requests
- Completeness of required documents


**Retrieve Data**

Available Programme data such as:

- Original loan amount
- Remaining balance
- Arrears amount
- Number of unpaid installments
- Payment history
- Remaining repayment period
- Family information

**Analyze**

- Income
- Repayment capacity
- Family situation
- Income per family member
- Financial circumstances

**Decide**

- Approve
- Request additional information
- Reject
- Refer to a human officer


**Challenge Assumptions**

For the purpose of this challenge, assume the AI Agent can access:

**UAE PASS**

To retrieve:

- Identity information
- Personal profile
- Basic beneficiary information

**MOEI Systems**

To retrieve:

- Loan details
- Arrears information
- Payment history
- Previous applications

**Financial Services**

To validate:

- Salary certificates
- Income information
- Banking information where applicable

**Core Business Rules**

**Rule 1**

Monthly deduction must not exceed:

**20% of the beneficiary's income**


**Rule 2**

The proposed repayment schedule must not exceed:

**The original approved loan repayment period**

**Rule 3**

An existing active application may result in automatic rejection.

## Simple Rescheduling Assessment Matrix

The logic is flexible: the monthly installment may be increased or reduced based on the beneficiary’s actual repayment capacity,
provided that the total deduction does not exceed 20% of salary and financial obligations are considered.

```
Criterion What should the Agent check? Simplified decision logic
```
```
Income / Salary Certificate Has the salary increased or decreased? What is the current installment ratio?
```
```
If income increased, the installment may be
increased gradually up to 20%. If income
decreased, the increase is reduced or the current
installment is maintained.
```
```
Financial Obligations Total obligations compared with total income through system linkage or financial data.
```
```
If obligations are high, for example above 60%
of income, reduce the increase, maintain the
installment, or refer for human review.
```
```
Unemployment Proof of unemployment or lack of stable income.
```
```
Move arrears to the end of the repayment
period without increasing the current monthly
installment.
```
```
Temporary Supporting Circumstances
```
```
Documents such as medical treatment abroad,
official assignment, or any verified temporary
reason.
```
```
Move arrears to the end of the repayment
period or postpone any increase until the
circumstance ends.
```
```
Final Recommendation Income + obligations + arrears + remaining period + supporting documents.
```
```
Recommend one path: increase within 20%,
reduce the increase, maintain current
installment, move arrears to the end, or refer to
human review.
```

**Beneficiary Journey**

Login via UAE PASS
↓
Citizen profile auto-populated
↓
Upload Salary Certificate
↓
Automated Validation
↓
Financial Analysis
↓
Policy Rule Evaluation
↓
AI Recommendation
↓
Status Update

**What should the beneficiary see?**

The beneficiary does not need to see the internal calculations.

The applicant should simply see:

In Progress

Additional Information Required

Approved

Rejected

Human Review Required

Each status should include a clear explanation.

**What we don't want**


A chatbot that only answers questions

Manual entry of data already available in government systems

Human review of every application

Decisions without explanations

**What we want**

Autonomous AI Agent

Automated data retrieval

Automated document validation

Explainable decisions

Human intervention only for exceptional cases

**Bonus Innovation Opportunities**

**Accessibility**

- Screen readers
- Voice navigation
- High contrast mode
- Digital sign language support

**Proactive AI**

- Predict repayment difficulties
- Early intervention recommendations
- Proactive alerts


**Explainable AI**

- Clear reasoning behind recommendations

**Fraud Detection**

- Suspicious document identification
- Duplicate application detection

**Governance**

- Confidence scoring
- Human escalation when needed

**Evaluation Criteria**

**Final Message**

**Imagine you are replacing the government officer who currently spends five days reviewing the application.**

Your mission is to build an AI Agent capable of validating, analyzing, reasoning, and recommending decisions in
minutes or seconds instead of days.

That is the real challenge.