# Edge Cases & Validation Comparison

This document maps the edge cases requested in the assignment to exactly how the system handles them.

## 1. The Five Core Claims
| Claim ID | Scenario | Expected Decision | Actual Decision (System Output) |
|----------|----------|-------------------|---------------------------------|
| **CLM-001** | Fully compliant, under limits, economy flight. | `APPROVE` | `APPROVE` |
| **CLM-002** | Spa and minibar (ineligible categories). | `REJECT` | `REJECT` |
| **CLM-003** | Valid items, but lodging is $250/night (Limit is $200). | `PARTIAL_APPROVE` | `PARTIAL_APPROVE` (Deducted $100) |
| **CLM-004** | Business class airfare, missing lodging receipt. | `MANUAL_REVIEW` | `MANUAL_REVIEW` |
| **CLM-005** | Total $220 meal without a receipt (> $25 limit). | `MANUAL_REVIEW` | `MANUAL_REVIEW` |

---

## 2. Specific Edge Cases Tested by the Deterministic Engine

| Edge Case | Handled By | Resulting Action |
|-----------|------------|------------------|
| **Meal exactly $75** | `check_limits()` | Approved in full. |
| **Meal $75.01** | `check_limits()` | $75 approved, $0.01 deducted (`PARTIAL_APPROVE`). |
| **Lodging exactly $200/night** | `check_limits()` | Approved in full. |
| **Lodging $200.01/night** | `check_limits()` | $200 approved, $0.01 deducted (`PARTIAL_APPROVE`). |
| **Total exactly $500** | `check_approval_threshold()` | `AUTO_APPROVE` tier. |
| **Total exactly $2,000** | `check_approval_threshold()` | `MANAGER_TIER` (Treated as `APPROVE`). |
| **Total $2,000.01** | `check_approval_threshold()` | `MANUAL_REVIEW`. |
| **Expense exactly $25** | `check_receipts()` | Receipt **not** required. |
| **Expense $25.01** | `check_receipts()` | Receipt **required**. If missing, `MANUAL_REVIEW`. |
| **Late by 30 days** | `check_timeliness()` | Accepted. |
| **Late by 31 days** | `check_timeliness()` | `MANUAL_REVIEW`. |
| **Missing required receipt** | `check_receipts()` | `MANUAL_REVIEW`. |
| **Business-class airfare** | `check_airfare_class()` | `MANUAL_REVIEW`. |
| **Invalid amount / Empty claim** | Pydantic Models (`models.py`) | Validation fails, schema correction defaults to `MANUAL_REVIEW`. |
| **Missing category** | Pydantic Models | Validation failure, caught safely by validator. |
| **All expenses ineligible** | `evaluate_claim()` | `REJECT` (Because calculated allowable amount is 0). |

## 3. Arithmetic Safety
Because Large Language Models (LLMs) are notoriously bad at arithmetic, **Groq NEVER calculates the reimbursement math**. 
All edge cases above are calculated by exact Python conditional math in `src/tools.py` and `src/policy_engine.py`. The LLM only receives the mathematical output to generate the textual explanation.
