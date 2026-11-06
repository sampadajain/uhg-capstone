from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


@dataclass
class Policy:
    policy_number: str
    product: str
    coverage_limit: float
    deductible: float
    clauses: dict[str, str] = field(default_factory=dict)
    notes: str = ""


@dataclass
class Document:
    document_id: str
    case_id: str
    doc_type: str
    file_name: str
    status: str = "uploaded"
    text: str = ""
    ocr_confidence: float = 1.0
    extracted_fields: dict[str, Any] = field(default_factory=dict)
    classification_confidence: float = 1.0
    prompt_injection: bool = False
    validation_warnings: list[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ClaimCase:
    case_id: str
    claimant_name: str
    claimant_email: str
    policy_number: str
    claim_amount: float
    incident_date: str
    status: str = "new"
    summary: str = ""
    summary_risks: list[str] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    staff: dict[str, Any] = field(default_factory=dict)
    approval_limit: float | None = None
    duplicate_of: str | None = None
    missing_documents: list[str] = field(default_factory=list)
    audit_log: list[dict[str, Any]] = field(default_factory=list)
    next_step: str = "intake"
    workflow_stage: str = "intake"
    approver: str | None = None
    adjuster: str | None = None
    human_decision: str | None = None
    sla_due_at: datetime | None = None
    notification_history: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AuditEvent:
    timestamp: datetime
    actor: str
    action: str
    details: dict[str, Any]
    case_id: str | None = None
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    level: Literal["info", "warning", "error"] = "info"
