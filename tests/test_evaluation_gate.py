from __future__ import annotations

from uhg_capstone.evaluation import evaluate_case_quality, evaluate_release


def test_case_quality_metrics_are_calculated() -> None:
    result = evaluate_case_quality(
        claim_amount=2500.0,
        coverage_limit=25000.0,
        policy_ok=True,
        prompt_injection_detected=False,
        pii_redacted=3,
        audit_events=6,
        approval_delay_hours=2,
    )

    assert result["pass"] is True
    assert result["overall_score"] >= 0.8
    assert result["case_readiness"] in {"ready", "review"}


def test_release_gate_blocks_below_threshold() -> None:
    metrics = {
        "coverage": 0.89,
        "safety": 0.98,
        "workflow_quality": 0.82,
    }

    result = evaluate_release(metrics, {"coverage": 0.9, "safety": 0.95, "workflow_quality": 0.85})

    assert result["pass"] is False
    assert "coverage" in result["failed_metrics"]
    assert result["release_status"] == "blocked"


def test_eval_report_builds_threshold_summary() -> None:
    report = evaluate_release({"coverage": 0.96, "safety": 0.97, "workflow_quality": 0.90}, {"coverage": 0.9, "safety": 0.95, "workflow_quality": 0.85})

    assert report["pass"] is True
    assert report["release_status"] == "approved"
    assert report["failed_metrics"] == []
    assert report["pass_rate"] == 1.0
    assert "summary" in report
    assert report["thresholds"]["coverage"] == 0.9
