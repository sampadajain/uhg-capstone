from __future__ import annotations

from typing import Any


class DummyAgent:
    def __init__(self, name: str, tools: list[str] | None = None, system_prompt: str = ""):
        self.name = name
        self.tools = tools or []
        self.system_prompt = system_prompt

    def invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"agent": self.name, "result": payload, "status": "ok"}


def build_specialist_agents() -> dict[str, DummyAgent]:
    return {
        "intake_agent": DummyAgent(
            "intake_agent",
            ["policy-mcp:get_policy", "policy-mcp:check_coverage", "case-mcp:register_case"],
            "Register the claim and check whether the policy covers the amount.",
        ),
        "document_agent": DummyAgent(
            "document_agent",
            ["documents-mcp:list_documents", "documents-mcp:extract_text", "documents-mcp:classify_document"],
            "Validate documents, extract text, and flag low-confidence or injected content.",
        ),
        "summary_agent": DummyAgent(
            "summary_agent",
            ["case-mcp:get_case", "documents-mcp:list_documents", "policy-mcp:search_policy_wording"],
            "Write a grounded summary that cites policy clauses and next steps.",
        ),
        "routing_agent": DummyAgent(
            "routing_agent",
            ["workflow-mcp:get_workload", "workflow-mcp:assign_case", "workflow-mcp:request_approval"],
            "Choose the suitable adjuster/approver and request approval.",
        ),
        "sla_agent": DummyAgent(
            "sla_agent",
            ["workflow-mcp:schedule_sla", "workflow-mcp:send_notification", "workflow-mcp:request_documents"],
            "Set SLA timers and notify relevant parties.",
        ),
    }


def route_decision(case_status: str, stage_results: dict[str, Any]) -> str:
    if stage_results.get("missing_documents"):
        return "await_documents"
    if stage_results.get("low_confidence"):
        return "manual_review"
    if case_status in {"intake", "new"}:
        return "intake_agent"
    if case_status == "document_review":
        return "summary_agent"
    if case_status == "summary_ready":
        return "routing_agent"
    if case_status == "awaiting_approval":
        return "sla_agent"
    return "finalize"
