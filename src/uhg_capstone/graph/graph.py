from __future__ import annotations

from typing import Any, TypedDict

try:
    from langgraph.graph import END, START, StateGraph
    from langgraph.types import interrupt
except Exception:  # pragma: no cover
    END = "__END__"
    START = "__START__"

    class StateGraph:  # type: ignore[no-redef]
        def __init__(self, state_schema: type[TypedDict] | None = None):
            self.nodes: dict[str, Any] = {}
            self.entry_point = START
            self.edges: dict[str, Any] = {}

        def add_node(self, name: str, fn):
            self.nodes[name] = fn

        def add_edge(self, source: str, target: str):
            self.edges.setdefault(source, []).append(target)

        def add_conditional_edges(self, source: str, fn, mapping):
            self.edges[source] = mapping

        def set_entry_point(self, name: str):
            self.entry_point = name

        def compile(self):
            return GraphRuntime(self)

    def interrupt(value: str):
        return {"status": "waiting_for_human", "message": value}

    class GraphRuntime:
        def __init__(self, graph):
            self.graph = graph

        def invoke(self, state: dict[str, Any]):
            current = state.copy()
            for node_name in self.graph.nodes:
                if node_name == self.entry_point:
                    continue
                fn = self.graph.nodes[node_name]
                current = fn(current)
                if current.get("case_status") == "awaiting_decision":
                    break
            return current


from uhg_capstone.agents.specialists import DummyAgent, route_decision
from uhg_capstone.store import build_seed_store


class ClaimState(TypedDict):
    case_id: str
    case_status: str
    next_step: str
    messages: list[str]
    agent_hops: list[str]
    stage_results: dict[str, Any]
    human_decision: str | None
    errors: list[str]
    token_usage: int


store = build_seed_store()


def intake_node(state: dict[str, Any]) -> dict[str, Any]:
    case = store.get_case(state["case_id"])
    if not case:
        return {**state, "errors": ["Case not found"], "case_status": "manual_review"}
    out = {**state, "case_status": "intake_complete", "next_step": "document_agent", "agent_hops": state.get("agent_hops", []) + ["intake_agent"], "messages": state.get("messages", []) + ["Intake complete and policy checked."], "stage_results": {**state.get("stage_results", {}), "coverage_ok": True}, "token_usage": state.get("token_usage", 0) + 120}
    return out


def document_node(state: dict[str, Any]) -> dict[str, Any]:
    case = store.get_case(state["case_id"])
    stage_results = {**state.get("stage_results", {})}
    for document in case.documents if case else []:
        if document.ocr_confidence < 0.8:
            stage_results["low_confidence"] = True
        if document.prompt_injection:
            stage_results["prompt_injection"] = True
    out = {**state, "case_status": "document_review", "next_step": "summary_agent", "agent_hops": state.get("agent_hops", []) + ["document_agent"], "messages": state.get("messages", []) + ["Documents classified and validated."], "stage_results": stage_results, "token_usage": state.get("token_usage", 0) + 210}
    return out


def summary_node(state: dict[str, Any]) -> dict[str, Any]:
    case = store.get_case(state["case_id"])
    if case:
        case.summary = "Claim summary: repair invoice for vehicle damage; coverage within policy; two risk flags: deductible and duplicate check pending."
    out = {**state, "case_status": "summary_ready", "next_step": "routing_agent", "agent_hops": state.get("agent_hops", []) + ["summary_agent"], "messages": state.get("messages", []) + ["Grounded summary generated."], "stage_results": {**state.get("stage_results", {}), "summary_ready": True}, "token_usage": state.get("token_usage", 0) + 310}
    return out


def routing_node(state: dict[str, Any]) -> dict[str, Any]:
    out = {**state, "case_status": "awaiting_approval", "next_step": "human_review", "agent_hops": state.get("agent_hops", []) + ["routing_agent"], "messages": state.get("messages", []) + ["Case routed to approver."], "stage_results": {**state.get("stage_results", {}), "approver_selected": True}, "token_usage": state.get("token_usage", 0) + 200}
    return out


def sla_node(state: dict[str, Any]) -> dict[str, Any]:
    out = {**state, "case_status": "sla_scheduled", "next_step": "finalize", "agent_hops": state.get("agent_hops", []) + ["sla_agent"], "messages": state.get("messages", []) + ["SLA scheduled and notifications sent."], "stage_results": {**state.get("stage_results", {}), "sla_set": True}, "token_usage": state.get("token_usage", 0) + 150}
    return out


def human_review_node(state: dict[str, Any]) -> dict[str, Any]:
    if state.get("human_decision"):
        case = store.get_case(state["case_id"])
        if case:
            store.record_decision(
                state["case_id"],
                state["human_decision"],
                state.get("decision_rationale", "System recorded a decision."),
                case.approver,
            )
        return {**state, "case_status": "decision_received", "next_step": "finalize", "messages": state.get("messages", []) + [f"Human decision recorded: {state['human_decision']}"], "agent_hops": state.get("agent_hops", []) + ["human_review"]}
    decision = interrupt("Approver decision required")
    if isinstance(decision, dict) and "decision" in decision:
        state = {**state, "human_decision": decision["decision"], "decision_rationale": decision.get("rationale", ""), "case_status": "decision_received", "next_step": "finalize"}
        case = store.get_case(state["case_id"])
        if case:
            store.record_decision(state["case_id"], state["human_decision"], state.get("decision_rationale", ""), case.approver)
        return state
    return {**state, "case_status": "awaiting_decision", "next_step": "human_review", "messages": state.get("messages", []) + ["Awaiting approval."], "agent_hops": state.get("agent_hops", []) + ["human_review"]}


def await_documents_node(state: dict[str, Any]) -> dict[str, Any]:
    return {**state, "case_status": "awaiting_documents", "next_step": "await_documents", "messages": state.get("messages", []) + ["Missing documents requested from claimant."], "stage_results": {**state.get("stage_results", {}), "missing_documents": True}, "token_usage": state.get("token_usage", 0) + 50}


def finalize_node(state: dict[str, Any]) -> dict[str, Any]:
    if state.get("human_decision") == "approve":
        case_status = "approved"
    elif state.get("human_decision") == "reject":
        case_status = "rejected"
    else:
        case_status = "finalized"
    return {**state, "case_status": case_status, "next_step": "END", "messages": state.get("messages", []) + ["Claim workflow finalized."], "token_usage": state.get("token_usage", 0) + 10}


def manual_review_node(state: dict[str, Any]) -> dict[str, Any]:
    return {**state, "case_status": "manual_review", "next_step": "END", "messages": state.get("messages", []) + ["Claim requires manual review due to low confidence or procedural issues."], "stage_results": {**state.get("stage_results", {}), "manual_review": True}, "token_usage": state.get("token_usage", 0) + 25}


def is_allowed_transition(current_status: str, next_step: str) -> bool:
    allowed = {
        "new": {"intake_agent"},
        "intake": {"intake_agent"},
        "intake_complete": {"document_agent", "manual_review"},
        "document_review": {"summary_agent", "manual_review", "await_documents"},
        "summary_ready": {"routing_agent", "manual_review"},
        "awaiting_approval": {"human_review", "manual_review"},
        "awaiting_decision": {"human_review", "manual_review"},
        "decision_received": {"finalize", "manual_review"},
        "finalized": {"END"},
        "approved": {"END"},
        "rejected": {"END"},
        "manual_review": {"END"},
    }
    return next_step in allowed.get(current_status, set())


def build_claim_graph() -> Any:
    workflow = StateGraph(ClaimState)
    workflow.add_node("intake_agent", intake_node)
    workflow.add_node("document_agent", document_node)
    workflow.add_node("summary_agent", summary_node)
    workflow.add_node("routing_agent", routing_node)
    workflow.add_node("sla_agent", sla_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("await_documents", await_documents_node)
    workflow.add_node("finalize", finalize_node)
    workflow.add_node("manual_review", manual_review_node)
    workflow.set_entry_point("intake_agent")

    workflow.add_conditional_edges(
        "intake_agent",
        lambda state: ("document_agent" if is_allowed_transition(state.get("case_status", "new"), "document_agent") else "manual_review"),
        {"document_agent": "document_agent", "manual_review": "manual_review"},
    )
    workflow.add_conditional_edges(
        "document_agent",
        lambda state: ("summary_agent" if is_allowed_transition(state.get("case_status", "document_review"), "summary_agent") else "manual_review"),
        {"summary_agent": "summary_agent", "manual_review": "manual_review"},
    )
    workflow.add_conditional_edges(
        "summary_agent",
        lambda state: ("routing_agent" if is_allowed_transition(state.get("case_status", "summary_ready"), "routing_agent") else "manual_review"),
        {"routing_agent": "routing_agent", "manual_review": "manual_review"},
    )
    workflow.add_conditional_edges(
        "routing_agent",
        lambda state: ("human_review" if is_allowed_transition(state.get("case_status", "awaiting_approval"), "human_review") else "manual_review"),
        {"human_review": "human_review", "manual_review": "manual_review"},
    )
    workflow.add_edge("human_review", "finalize")
    workflow.add_edge("await_documents", "finalize")
    workflow.add_edge("manual_review", END)
    workflow.add_edge("finalize", END)
    return workflow.compile()
