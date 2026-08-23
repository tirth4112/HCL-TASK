def evaluate_claim(claim, tool_results: dict) -> dict:
    """
    Deterministic Policy Engine.
    Precedence:
    1. Invalid/conflicting data -> MANUAL_REVIEW
    2. Late claim -> MANUAL_REVIEW
    3. Missing required receipt -> MANUAL_REVIEW
    4. Business/first-class airfare -> MANUAL_REVIEW
    5. Total reimbursable amount > 2000 -> MANUAL_REVIEW
    6. All expenses ineligible -> REJECT
    7. Valid expenses with per-diem deduction -> PARTIAL_APPROVE
    8. Fully compliant -> APPROVE
    """
    
    receipts_res = tool_results.get("receipts", {})
    limits_res = tool_results.get("limits", {})
    airfare_res = tool_results.get("airfare", {})
    time_res = tool_results.get("timeliness", {})
    
    # Calculate amount threshold based on allowed amount, not claimed amount
    reimbursable_amount = limits_res.get("allowed", 0.0)
    deducted_amount = limits_res.get("deducted", 0.0)
    
    threshold_res = tool_results.get("threshold", {}) 
    # Or recalculate threshold on reimbursable
    manual_review_threshold = reimbursable_amount > 2000.0

    missing_docs = receipts_res.get("missing_receipts", [])

    if time_res.get("manual_review_required", False):
        decision = "MANUAL_REVIEW"
    elif receipts_res.get("manual_review_required", False):
        decision = "MANUAL_REVIEW"
    elif airfare_res.get("manual_review_required", False):
        decision = "MANUAL_REVIEW"
    elif manual_review_threshold:
        decision = "MANUAL_REVIEW"
    elif reimbursable_amount == 0.0 and deducted_amount > 0.0:
        decision = "REJECT"
    elif deducted_amount > 0.0:
        decision = "PARTIAL_APPROVE"
    else:
        decision = "APPROVE"

    # If Manual review, do not approve money
    if decision == "MANUAL_REVIEW":
        # Usually, wait for human
        # But instructions say "Manual-review cases do not receive fabricated reimbursement amounts."
        pass 

    return {
        "decision": decision,
        "approved_amount": reimbursable_amount if decision != "MANUAL_REVIEW" else 0.0, # Or keep calculated but it's pending
        "deducted_amount": deducted_amount if decision != "MANUAL_REVIEW" else 0.0,
        "missing_docs": [f"Missing receipt for {m['category']} ({m['amount']})" for m in missing_docs]
    }
