from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover
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
server = FastMCP("workflow-mcp")


@server.tool()
def get_workload(role: str) -> dict[str, Any]:
    return {"ok": True, "workers": [
        {"worker_id": worker_id, "role": data["role"], "name": data["name"]}
        for worker_id, data in store.staff.items()
        if data["role"] == role
    ]}


@server.tool()
def assign_case(case_id: str, adjuster_id: str | None = None, approver_id: str | None = None) -> dict[str, Any]:
    case = store.assign_case(case_id, adjuster_id, approver_id)
    return {"ok": True, "case_id": case.case_id, "adjuster": case.adjuster, "approver": case.approver}


@server.tool()
def request_approval(case_id: str, approver_id: str) -> dict[str, Any]:
    case = store.request_approval(case_id, approver_id)
    return {"ok": True, "case_id": case.case_id, "status": case.status, "approver": case.approver}


@server.tool()
def schedule_sla(case_id: str, business_hours: bool = True) -> dict[str, Any]:
    case = store.get_case(case_id)
    if not case:
        return {"ok": False, "error": "Case not found"}
    due = datetime.utcnow() + timedelta(days=3)
    return {"ok": True, "case_id": case.case_id, "sla_due": due.isoformat(), "business_hours": business_hours}


@server.tool()
def send_notification(case_id: str, recipient: str, message: str) -> dict[str, Any]:
    return {"ok": True, "case_id": case_id, "recipient": recipient, "message": message, "sent_at": datetime.utcnow().isoformat()}


@server.tool()
def request_documents(case_id: str, document_names: list[str]) -> dict[str, Any]:
    case = store.mark_missing_documents(case_id, document_names)
    return {"ok": True, "case_id": case.case_id, "missing": case.missing_documents}


@server.resource("staff://directory")
def staff_directory() -> str:
    return "\n".join(f"{worker_id}: {data['name']} ({data['role']}, limit={data['approval_limit']})" for worker_id, data in store.staff.items())


@server.resource("sla://rules")
def sla_rules() -> str:
    return "Metrics: standard approval SLA is 3 business days; escalations after 1 day of inactivity; claimant notifications sent on assignment and decision."


@server.prompt()
def claimant_letter(case_id: str) -> str:
    case = store.get_case(case_id)
    if not case:
        return "Case not found"
    return f"Dear {case.claimant_name}, we are reviewing your claim {case.case_id}. Additional information may be requested while we complete review."


@server.prompt()
def approver_brief(case_id: str) -> str:
    case = store.get_case(case_id)
    if not case:
        return "Case not found"
    return f"Approver brief for {case.case_id}: claimant={case.claimant_name}, claim_amount={case.claim_amount}, status={case.status}."
