from __future__ import annotations

from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover - runtime fallback for lightweight local use
    class FastMCP:  # type: ignore[no-redef]
        def __init__(self, name: str):
            self.name = name
            self.tools = {}
            self.resources = {}
            self.prompts = {}

        def tool(self, *args, **kwargs):
            def decorator(fn):
                self.tools[fn.__name__] = fn
                return fn
            return decorator

        def resource(self, *args, **kwargs):
            def decorator(fn):
                self.resources[fn.__name__] = fn
                return fn
            return decorator

        def prompt(self, *args, **kwargs):
            def decorator(fn):
                self.prompts[fn.__name__] = fn
                return fn
            return decorator

from uhg_capstone.store import build_seed_store

store = build_seed_store()
server = FastMCP("case-mcp")


@server.tool()
def get_case(case_id: str) -> dict[str, Any]:
    case = store.get_case(case_id)
    if not case:
        return {"ok": False, "error": "Case not found"}
    return {"ok": True, "case": {"case_id": case.case_id, "status": case.status, "summary": case.summary}}


@server.tool()
def list_cases() -> dict[str, Any]:
    return {"ok": True, "cases": [
        {"case_id": case.case_id, "status": case.status, "claimant_name": case.claimant_name}
        for case in store.list_cases()
    ]}


@server.tool()
def find_similar_cases(policy_number: str, claimant_name: str, claim_amount: float) -> dict[str, Any]:
    matches = []
    for case in store.list_cases():
        if case.policy_number == policy_number and case.claimant_name.lower() == claimant_name.lower():
            matches.append({"case_id": case.case_id, "claim_amount": case.claim_amount, "status": case.status})
    return {"ok": True, "matches": matches}


@server.tool()
def register_case(claimant_name: str, claimant_email: str, policy_number: str, claim_amount: float, incident_date: str, case_id: str | None = None) -> dict[str, Any]:
    case = store.register_case(claimant_name, claimant_email, policy_number, claim_amount, incident_date, case_id)
    return {"ok": True, "case_id": case.case_id}


@server.tool()
def save_summary(case_id: str, summary: str, risks: list[str]) -> dict[str, Any]:
    case = store.save_summary(case_id, summary, risks)
    return {"ok": True, "case_id": case.case_id, "status": case.status}


@server.resource("case://{case_id}")
def case_resource(case_id: str) -> str:
    case = store.get_case(case_id)
    if not case:
        return "Case not found"
    return f"Case {case.case_id}: claimant={case.claimant_name}; policy={case.policy_number}; status={case.status}"


@server.resource("case://{case_id}/timeline")
def case_timeline(case_id: str) -> str:
    case = store.get_case(case_id)
    if not case:
        return "Case not found"
    events = "\n".join(f"- {item['action']} by {item['actor']}" for item in case.audit_log)
    return events or "No events recorded"


@server.prompt()
def case_summary(case_id: str) -> str:
    case = store.get_case(case_id)
    if not case:
        return "Case not found"
    return (
        f"Summarise the claim case {case_id}. Use only confirmed facts: claimant={case.claimant_name}, "
        f"policy={case.policy_number}, amount={case.claim_amount}, status={case.status}."
    )
