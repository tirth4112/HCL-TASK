from pydantic import BaseModel, Field
from typing import List, Optional

class ClaimItemModel(BaseModel):
    category: str
    description: str
    amount: float
    receipt_attached: bool

class ClaimModel(BaseModel):
    claim_id: str
    employee_name: str
    trip_start: str
    trip_end: str
    submitted_date: str
    total_claimed: float
    items: List[ClaimItemModel]

class ToolResultModel(BaseModel):
    tool_name: str
    result: dict

class AgentOutputModel(BaseModel):
    claim_id: str
    decision: str
    approved_amount: float
    deducted_amount: float
    missing_docs: List[str]
    policy_refs: List[str]
    confidence: float
    explanation: str
    tools_used: List[str]
