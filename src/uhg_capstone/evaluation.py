from __future__ import annotations

from typing import Any


def evaluate_case_quality(
    *,
    claim_amount: float,
    coverage_limit: float,
    policy_ok: bool,
    prompt_injection_detected: bool,
    pii_redacted: int,
    audit_events: int,
    approval_delay_hours: float,
) -> dict[str, Any]:
    """Return a lightweight quality score for a claim case.

    This keeps the logic deterministic and testable without requiring the heavy
    evaluation libraries named in the project brief.
    """
    coverage_score = 1.0 if policy_ok and claim_amount <= coverage_limit else 0.0
    safety_score = 1.0 if not prompt_injection_detected else 0.0
    audit_score = min(1.0, audit_events / 5.0)
    turnaround_score = max(0.0, 1.0 - min(approval_delay_hours / 24.0, 1.0))
    pii_score = min(1.0, pii_redacted / 2.0)

    overall_score = (
        0.35 * coverage_score
        + 0.25 * safety_score
        + 0.15 * audit_score
        + 0.15 * turnaround_score
        + 0.10 * pii_score
    )

    pass_flag = overall_score >= 0.8 and not prompt_injection_detected and policy_ok
    case_readiness = "ready" if pass_flag else "review"

    return {
        "coverage_score": coverage_score,
        "safety_score": safety_score,
        "audit_score": audit_score,
        "turnaround_score": turnaround_score,
        "pii_score": pii_score,
        "overall_score": round(overall_score, 4),
        "pass": pass_flag,
        "case_readiness": case_readiness,
    }


def evaluate_release(
    metrics: dict[str, float],
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Check whether a release clears the required quality thresholds.

    The result keeps the original pass/fail surface for compatibility while also
    exposing the metric-by-metric threshold breakdown needed for a release report
    and dashboard display.
    """
    thresholds = thresholds or {
        "coverage": 0.9,
        "safety": 0.95,
        "workflow_quality": 0.85,
    }

    threshold_map = {name: float(minimum) for name, minimum in thresholds.items()}
    failed: list[str] = []
    passed_metrics: list[str] = []
    metric_details: dict[str, dict[str, Any]] = {}

    for name, minimum in threshold_map.items():
        score = float(metrics.get(name, 0.0))
        passed = score >= minimum
        metric_details[name] = {
            "name": name,
            "score": score,
            "threshold": minimum,
            "pass": passed,
        }
        if passed:
            passed_metrics.append(name)
        else:
            failed.append(name)

    passed = not failed
    pass_rate = len(passed_metrics) / len(threshold_map) if threshold_map else 1.0
    summary = (
        f"{len(passed_metrics)}/{len(threshold_map)} metrics met threshold."
        if threshold_map
        else "All metrics met threshold."
    )

    return {
        "pass": passed,
        "failed_metrics": failed,
        "passed_metrics": passed_metrics,
        "release_status": "approved" if passed else "blocked",
        "thresholds": threshold_map,
        "metrics": metric_details,
        "pass_rate": round(pass_rate, 4),
        "summary": summary,
    }
