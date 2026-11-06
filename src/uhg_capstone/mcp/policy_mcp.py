from __future__ import annotations

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

from uhg_capstone.store import build_seed_store

store = build_seed_store()
server = FastMCP("policy-mcp")


@server.tool()
def get_policy(policy_number: str) -> dict[str, Any]:
    policy = store.policies.get(policy_number)
    if not policy:
        return {"ok": False, "error": "Policy not found"}
    return {"ok": True, "policy": {"policy_number": policy.policy_number, "product": policy.product, "coverage_limit": policy.coverage_limit}}


@server.tool()
def check_coverage(policy_number: str, claim_amount: float) -> dict[str, Any]:
    policy = store.policies.get(policy_number)
    if not policy:
        return {"ok": False, "error": "Policy not found"}
    in_force = claim_amount <= policy.coverage_limit
    return {"ok": True, "in_force": in_force, "coverage_limit": policy.coverage_limit, "deductible": policy.deductible}


@server.tool()
def search_policy_wording(query: str, product: str | None = None) -> dict[str, Any]:
    matches = []
    for policy in store.policies.values():
        if product and policy.product.lower() != product.lower():
            continue
        for clause_name, clause_text in policy.clauses.items():
            if query.lower() in clause_text.lower():
                matches.append({"policy_number": policy.policy_number, "clause_name": clause_name, "text": clause_text})
    return {"ok": True, "matches": matches}


@server.resource("policy://{policy_number}")
def policy_resource(policy_number: str) -> str:
    policy = store.policies.get(policy_number)
    if not policy:
        return "Policy not found"
    return f"Policy {policy.policy_number}: product={policy.product}, limit={policy.coverage_limit}, deductible={policy.deductible}"


@server.resource("policy-wording://{product}")
def policy_wording(product: str) -> str:
    matches = [
        f"{policy.policy_number}: {clause_name} -> {clause_text}"
        for policy in store.policies.values()
        for clause_name, clause_text in policy.clauses.items()
        if policy.product.lower() == product.lower()
    ]
    return "\n".join(matches) if matches else "No wording available"
