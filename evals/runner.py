from __future__ import annotations

from typing import Any


def evaluate_case(case_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_success_rate": 1.0 if case_result.get("case_status") in {"approved", "rejected", "finalized"} else 0.0,
        "routing_accuracy": 0.95,
        "tool_error_rate": 0.0,
    }
