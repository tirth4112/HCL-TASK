from pydantic import ValidationError
import json
from .models import AgentOutputModel

def validate_decision(result: dict) -> dict:
    """
    Validate exact output schema.
    If invalid: attempt safe normalization.
    If still invalid: return MANUAL_REVIEW format safely.
    """
    try:
        validated = AgentOutputModel(**result)
        return validated.model_dump()
    except ValidationError as e:
        # Attempt safe normalization
        try:
            safe_result = {
                "claim_id": result.get("claim_id", "UNKNOWN"),
                "decision": "MANUAL_REVIEW", # Default to safe manual review
                "approved_amount": 0.0,
                "deducted_amount": 0.0,
                "missing_docs": result.get("missing_docs", []),
                "policy_refs": result.get("policy_refs", []),
                "confidence": 0.0,
                "explanation": f"Schema validation failed. Escalating to MANUAL_REVIEW. Errors: {str(e)}",
                "tools_used": result.get("tools_used", [])
            }
            return safe_result
        except Exception:
            return {
                "claim_id": "UNKNOWN",
                "decision": "MANUAL_REVIEW",
                "approved_amount": 0.0,
                "deducted_amount": 0.0,
                "missing_docs": [],
                "policy_refs": [],
                "confidence": 0.0,
                "explanation": "Catastrophic validation failure.",
                "tools_used": []
            }
