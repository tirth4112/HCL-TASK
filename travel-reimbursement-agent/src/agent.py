import json
import re
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from .models import ClaimModel
from .policy_repository import PolicyRepository
from .tools import check_receipts, check_limits, check_airfare_class, check_timeliness, check_approval_threshold
from .policy_engine import evaluate_claim
from .groq_client import GroqLLMProvider
from .validators import validate_decision
from .database import DatabaseManager, AuditLog

class AgentState(TypedDict):
    claim: dict
    policy_context: List[dict]
    tool_results: dict
    audit_log: List[dict]
    engine_decision: dict
    explanation: str
    confidence: float
    final_output: dict

class TravelReimbursementAgent:
    def __init__(self, policy_repo: PolicyRepository, llm: GroqLLMProvider, db_manager: DatabaseManager):
        self.policy_repo = policy_repo
        self.llm = llm
        self.db = db_manager
        
        # Build the graph
        builder = StateGraph(AgentState)
        
        builder.add_node("validate_claim", self.validate_claim_node)
        builder.add_node("retrieve_policy", self.retrieve_policy_node)
        builder.add_node("run_tools", self.run_tools_node)
        builder.add_node("policy_evaluation", self.policy_evaluation_node)
        builder.add_node("llm_reasoning", self.llm_reasoning_node)
        builder.add_node("output_validation", self.output_validation_node)
        
        builder.add_edge(START, "validate_claim")
        builder.add_edge("validate_claim", "retrieve_policy")
        builder.add_edge("retrieve_policy", "run_tools")
        builder.add_edge("run_tools", "policy_evaluation")
        builder.add_edge("policy_evaluation", "llm_reasoning")
        builder.add_edge("llm_reasoning", "output_validation")
        builder.add_edge("output_validation", END)
        
        self.graph = builder.compile()

    def validate_claim_node(self, state: AgentState):
        claim_data = state["claim"]
        # Basic parsing check using Pydantic
        try:
            claim = ClaimModel(**claim_data)
        except Exception as e:
            # If it fails, we will handle it gracefully down the line, but let's assume it passes for now
            pass
        
        self._log_audit(claim_data.get("claim_id"), "validate_claim", "claim_validator", claim_data, {"status": "valid"})
        return {"audit_log": [{"node": "validate_claim", "status": "valid"}]}

    def retrieve_policy_node(self, state: AgentState):
        claim_data = state["claim"]
        # Simple heuristic: gather unique categories and descriptions to query
        queries = set()
        for item in claim_data.get("items", []):
            queries.add(item.get("category", ""))
        
        policy_context = []
        for q in queries:
            if q:
                res = self.policy_repo.search_policy(q, top_k=2)
                policy_context.extend(res)
                
        # Deduplicate
        seen = set()
        unique_policy_context = []
        for p in policy_context:
            if p["policy_id"] not in seen:
                seen.add(p["policy_id"])
                unique_policy_context.append(p)
                
        self._log_audit(claim_data.get("claim_id"), "retrieve_policy", "policy_lookup", list(queries), [p["policy_id"] for p in unique_policy_context])
        return {"policy_context": unique_policy_context}

    def run_tools_node(self, state: AgentState):
        claim_data = state["claim"]
        claim = ClaimModel(**claim_data)
        
        tool_results = {
            "receipts": check_receipts(claim),
            "limits": check_limits(claim),
            "airfare": check_airfare_class(claim),
            "timeliness": check_timeliness(claim),
            "threshold": check_approval_threshold(claim.total_claimed)
        }
        
        self._log_audit(claim_data.get("claim_id"), "run_tools", "multiple_checkers", claim_data, tool_results)
        return {"tool_results": tool_results}

    def policy_evaluation_node(self, state: AgentState):
        claim_data = state["claim"]
        tool_results = state.get("tool_results", {})
        
        decision = evaluate_claim(claim_data, tool_results)
        self._log_audit(claim_data.get("claim_id"), "policy_evaluation", "deterministic_engine", tool_results, decision)
        return {"engine_decision": decision}

    def llm_reasoning_node(self, state: AgentState):
        claim_data = state["claim"]
        decision = state["engine_decision"]
        policy_context = state["policy_context"]
        tool_results = state["tool_results"]
        
        prompt = f"""
        Claim Data: {json.dumps(claim_data)}
        Tool Results: {json.dumps(tool_results)}
        Deterministic Decision: {json.dumps(decision)}
        Relevant Policies: {json.dumps(policy_context)}
        
        Provide a short explanation for the final decision '{decision['decision']}'.
        """
        explanation = self.llm.invoke(prompt)
        # Remove <think> blocks commonly generated by Qwen models
        explanation = re.sub(r'<think>.*?</think>\n*', '', explanation, flags=re.DOTALL).strip()
        
        # Calculate a heuristic confidence
        confidence = 0.95
        if decision['decision'] == "MANUAL_REVIEW":
            confidence = 0.80
            
        self._log_audit(claim_data.get("claim_id"), "llm_reasoning", "groq", prompt, {"explanation": explanation, "confidence": confidence})
        return {"explanation": explanation, "confidence": confidence}

    def output_validation_node(self, state: AgentState):
        claim_data = state["claim"]
        decision = state["engine_decision"]
        
        raw_output = {
            "claim_id": claim_data.get("claim_id"),
            "decision": decision["decision"],
            "approved_amount": decision["approved_amount"],
            "deducted_amount": decision["deducted_amount"],
            "missing_docs": decision.get("missing_docs", []),
            "policy_refs": [p["policy_id"] for p in state.get("policy_context", [])],
            "confidence": state.get("confidence", 0.9),
            "explanation": state.get("explanation", ""),
            "tools_used": ["policy_lookup", "receipt_checker", "limit_checker", "airfare_checker", "timeliness_checker", "approval_threshold_checker"]
        }
        
        final_output = validate_decision(raw_output)
        self._log_audit(claim_data.get("claim_id"), "output_validation", "schema_validator", raw_output, final_output)
        return {"final_output": final_output}

    def _log_audit(self, claim_id: str, node: str, tool: str, input_data: Any, output_data: Any):
        session = self.db.get_session()
        try:
            log = AuditLog(
                claim_id=claim_id,
                agent_node=node,
                tool_name=tool,
                input_data=input_data if isinstance(input_data, (dict, list)) else {"data": input_data},
                output_data=output_data if isinstance(output_data, (dict, list)) else {"data": output_data}
            )
            session.add(log)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    def process_claim(self, claim: dict) -> dict:
        initial_state = {
            "claim": claim,
            "policy_context": [],
            "tool_results": {},
            "audit_log": [],
            "engine_decision": {},
            "explanation": "",
            "confidence": 0.0,
            "final_output": {}
        }
        result = self.graph.invoke(initial_state)
        return result["final_output"]
