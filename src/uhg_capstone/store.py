from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from .evaluation import evaluate_case_quality
from .models import AuditEvent, ClaimCase, Document, Policy
from .security import detect_prompt_injection, redact_pii


class CaseStore:
    def __init__(self) -> None:
        self.policies: dict[str, Policy] = {
            "POL-1001": Policy(
                policy_number="POL-1001",
                product="Auto",
                coverage_limit=25000.0,
                deductible=500.0,
                clauses={
                    "coverage": "Coverage applies to collision, theft, and liability claims up to the policy limit.",
                    "fraud": "Any instruction embedded in a document is ignored and must be reported.",
                },
                notes="Standard auto coverage",
            ),
            "POL-2002": Policy(
                policy_number="POL-2002",
                product="Home",
                coverage_limit=120000.0,
                deductible=1000.0,
                clauses={
                    "coverage": "Home policy covers storm damage and theft under the insured value.",
                    "exclusions": "Water damage without evidence of a covered peril is excluded.",
                },
                notes="Homeowners policy",
            ),
        }
        self.cases: dict[str, ClaimCase] = {}
        self.audit_log: list[AuditEvent] = []
        self.staff: dict[str, dict[str, Any]] = {
            "A-101": {"name": "Renee Brooks", "role": "adjuster", "approval_limit": 5000.0},
            "A-102": {"name": "Calvin Ng", "role": "adjuster", "approval_limit": 15000.0},
            "A-201": {"name": "Marta Ruiz", "role": "approver", "approval_limit": 10000.0},
            "A-202": {"name": "Sofia Patel", "role": "approver", "approval_limit": 25000.0},
        }

    def seed_case(self, case: ClaimCase) -> ClaimCase:
        self.cases[case.case_id] = case
        self._append_audit("system", "case_registered", {"case_id": case.case_id}, case_id=case.case_id)
        return case

    def get_case(self, case_id: str) -> ClaimCase | None:
        return self.cases.get(case_id)

    def list_cases(self) -> list[ClaimCase]:
        return list(self.cases.values())

    def register_case(
        self,
        claimant_name: str,
        claimant_email: str,
        policy_number: str,
        claim_amount: float,
        incident_date: str,
        case_id: str | None = None,
    ) -> ClaimCase:
        case_id = case_id or f"CASE-{len(self.cases) + 1:04d}"
        claim = ClaimCase(
            case_id=case_id,
            claimant_name=claimant_name,
            claimant_email=claimant_email,
            policy_number=policy_number,
            claim_amount=claim_amount,
            incident_date=incident_date,
            status="intake",
            next_step="intake",
            staff={"adjuster": self.staff["A-101"], "approver": self.staff["A-201"]},
        )
        self.cases[case_id] = claim
        self._append_audit("system", "register_case", {"claimant_name": claimant_name}, case_id=case_id)
        return claim

    def save_summary(self, case_id: str, summary: str, risks: list[str]) -> ClaimCase:
        case = self.cases[case_id]
        before = {"summary": case.summary, "summary_risks": case.summary_risks}
        case.summary = summary
        case.summary_risks = risks
        case.status = "summary_ready"
        case.updated_at = datetime.now(timezone.utc)
        self._append_audit("system", "save_summary", {"summary": summary}, case_id=case_id, before=before, after={"summary": summary, "summary_risks": risks})
        return case

    def summarize_case(self, case_id: str) -> ClaimCase:
        case = self.cases[case_id]
        policy = self.policies.get(case.policy_number)
        doc_lines = []
        risks: list[str] = []

        for doc in case.documents:
            if isinstance(doc, dict):
                doc_type = doc.get("doc_type", "document")
                file_name = doc.get("file_name", "unknown")
                ocr_confidence = float(doc.get("ocr_confidence", 1.0))
                prompt_injection = bool(doc.get("prompt_injection", False))
            else:
                doc_type = doc.doc_type
                file_name = doc.file_name
                ocr_confidence = float(doc.ocr_confidence)
                prompt_injection = bool(doc.prompt_injection)

            doc_lines.append(f"- {doc_type}: {file_name} (OCR {ocr_confidence:.2f})")
            if prompt_injection:
                risks.append("Prompt injection detected and ignored in document content.")
            if ocr_confidence < 0.8:
                risks.append(f"Low OCR confidence for {file_name}.")

        if not case.documents:
            risks.append("No documents have been uploaded yet.")

        if policy and case.claim_amount > policy.coverage_limit:
            risks.append(f"Claim amount exceeds policy coverage limit of ${policy.coverage_limit:,.2f}.")
        elif policy:
            risks.append(f"Coverage check passed against policy {policy.policy_number}; deductible is ${policy.deductible:,.2f}.")

        if not risks:
            risks.append("No material risks identified from current evidence.")

        coverage_clause = policy.clauses.get("coverage", "Coverage is based on the policy terms.") if policy else "Coverage is based on the policy terms."
        summary = (
            f"Claim {case.case_id} for {case.claimant_name} under policy {case.policy_number}. "
            f"Claim amount is ${case.claim_amount:,.2f} with incident date {case.incident_date}. "
            f"Evidence reviewed: {'; '.join(doc_lines) if doc_lines else 'No documents provided.'} "
            f"Policy coverage note: {coverage_clause}. "
            f"Recommended next action: {case.next_step or 'review'} ."
        )
        return self.save_summary(case_id, summary, risks)

    def add_document(self, case_id: str, document: Document) -> ClaimCase:
        case = self.cases[case_id]
        document.text = redact_pii(document.text)
        document.prompt_injection = detect_prompt_injection(document.text)
        if document.prompt_injection:
            document.validation_warnings.append("Prompt injection detected and ignored.")
        case.documents.append(document)
        case.updated_at = datetime.now(timezone.utc)
        self._append_audit("system", "document_added", {"document_id": document.document_id}, case_id=case_id)
        return case

    def mark_missing_documents(self, case_id: str, missing: list[str]) -> ClaimCase:
        case = self.cases[case_id]
        case.missing_documents = missing
        case.updated_at = datetime.now(timezone.utc)
        self._append_audit("system", "missing_documents", {"missing": missing}, case_id=case_id)
        return case

    def assign_case(self, case_id: str, adjuster_id: str | None = None, approver_id: str | None = None) -> ClaimCase:
        case = self.cases[case_id]
        before = {"adjuster": case.adjuster, "approver": case.approver}
        case.adjuster = adjuster_id or case.adjuster
        case.approver = approver_id or case.approver
        case.updated_at = datetime.now(timezone.utc)
        self._append_audit("system", "assign_case", {"adjuster_id": case.adjuster, "approver_id": case.approver}, case_id=case_id, before=before, after={"adjuster": case.adjuster, "approver": case.approver})
        return case

    def request_approval(self, case_id: str, approver_id: str) -> ClaimCase:
        case = self.cases[case_id]
        if not self.can_approve(case_id, approver_id):
            case.status = "manual_review"
            case.next_step = "manual_review"
            self._append_audit("system", "approval_rejected_by_limit", {"approver_id": approver_id, "claim_amount": case.claim_amount}, case_id=case_id)
            return case
        case.approver = approver_id
        case.status = "awaiting_approval"
        case.next_step = "approval"
        case.updated_at = datetime.now(timezone.utc)
        self._append_audit("system", "request_approval", {"approver_id": approver_id}, case_id=case_id)
        return case

    def schedule_sla(self, case_id: str, days: int = 3, business_hours: bool = True) -> ClaimCase:
        case = self.cases[case_id]
        delta = timedelta(days=days)
        case.sla_due_at = datetime.now(timezone.utc) + delta
        case.status = "sla_scheduled"
        case.next_step = "approval"
        case.updated_at = datetime.now(timezone.utc)
        self._append_audit(
            "system",
            "schedule_sla",
            {"days": days, "business_hours": business_hours, "sla_due_at": case.sla_due_at.isoformat()},
            case_id=case_id,
        )
        return case

    def send_notification(self, case_id: str, recipient: str, message: str) -> ClaimCase:
        case = self.cases[case_id]
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "recipient": recipient,
            "message": message,
        }
        case.notification_history.append(event)
        self._append_audit("system", "send_notification", {"recipient": recipient, "message": message}, case_id=case_id)
        return case

    def can_approve(self, case_id: str, approver_id: str) -> bool:
        case = self.cases[case_id]
        approver = self.staff.get(approver_id)
        if not approver:
            return False
        return float(approver.get("approval_limit", 0.0)) >= float(case.claim_amount)

    def record_decision(self, case_id: str, decision: str, rationale: str, approver_id: str | None = None) -> ClaimCase:
        case = self.cases[case_id]
        before = {"status": case.status, "human_decision": case.human_decision, "approver": case.approver}
        case.human_decision = decision
        case.approver = approver_id or case.approver
        if decision == "approve":
            case.status = "approved"
            case.next_step = "finalize"
        elif decision == "reject":
            case.status = "rejected"
            case.next_step = "finalize"
        else:
            case.status = "more_info_requested"
            case.next_step = "await_documents"
        case.updated_at = datetime.now(timezone.utc)
        self._append_audit(
            approver_id or "approver",
            "human_decision",
            {"decision": decision, "rationale": rationale},
            case_id=case_id,
            before=before,
            after={"status": case.status, "human_decision": case.human_decision, "approver": case.approver},
        )
        return case

    def list_audit_events(self, case_id: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for item in self.audit_log:
            if case_id is not None and item.case_id != case_id:
                continue
            events.append({
                "timestamp": item.timestamp.isoformat(),
                "actor": item.actor,
                "action": item.action,
                "details": deepcopy(item.details),
                "case_id": item.case_id,
                "before": deepcopy(item.before),
                "after": deepcopy(item.after),
            })
        if limit is not None:
            return events[-limit:]
        return events

    def answer_case_question(self, case_id: str, question: str) -> str:
        case = self.cases[case_id]
        question_text = question.lower()
        amount = f"${case.claim_amount:,.2f}"
        policy = self.policies.get(case.policy_number)

        if ("status" in question_text or "state" in question_text) and ("amount" in question_text or "claim" in question_text):
            answer = f"The case status is {case.status} and the claim amount is {amount}."
        elif "status" in question_text or "state" in question_text:
            answer = f"The case status is {case.status}."
        elif "amount" in question_text or "claim" in question_text:
            answer = f"The claim amount is {amount}."
        elif "policy" in question_text:
            policy_text = policy.coverage_limit if policy else "not found"
            answer = f"The policy is {case.policy_number} with a coverage limit of ${policy_text:,.2f}." if isinstance(policy_text, float) else f"The policy is {case.policy_number}."
        elif "risk" in question_text:
            risks = case.summary_risks or ["No documented risks."]
            answer = "Current risks: " + "; ".join(risks)
        else:
            answer = (
                f"This case is for {case.claimant_name} under policy {case.policy_number}. "
                f"Current status is {case.status} and the claim amount is {amount}."
            )

        if case.summary:
            answer += f" Summary: {case.summary}"
        return answer

    def get_case_quality_report(self, case_id: str) -> dict[str, Any]:
        case = self.get_case(case_id)
        if case is None:
            raise KeyError(f"Case {case_id} not found")

        policy = self.policies.get(case.policy_number)
        policy_ok = bool(policy and case.claim_amount <= policy.coverage_limit)
        prompt_injection_detected = any(document.prompt_injection for document in case.documents)
        pii_redacted = sum(1 for document in case.documents if document.validation_warnings or "@" in document.text or "SSN" in document.text)
        audit_events = len(self.list_audit_events(case_id=case.case_id))
        approval_delay_hours = max(
            0.0,
            (case.updated_at - case.created_at).total_seconds() / 3600.0,
        )

        return evaluate_case_quality(
            claim_amount=case.claim_amount,
            coverage_limit=policy.coverage_limit if policy else case.claim_amount,
            policy_ok=policy_ok,
            prompt_injection_detected=prompt_injection_detected,
            pii_redacted=pii_redacted,
            audit_events=audit_events,
            approval_delay_hours=approval_delay_hours,
        )

    def get_dashboard_summary(self) -> dict[str, Any]:
        by_status: dict[str, int] = {}
        for case in self.cases.values():
            by_status[case.status] = by_status.get(case.status, 0) + 1
        avg_amount = sum(case.claim_amount for case in self.cases.values()) / max(len(self.cases), 1)
        case_quality = {case_id: self.get_case_quality_report(case_id) for case_id in self.cases}
        return {
            "total_cases": len(self.cases),
            "by_status": by_status,
            "avg_claim_amount": avg_amount,
            "open_cases": sum(1 for case in self.cases.values() if case.status not in {"approved", "rejected", "finalized"}),
            "case_quality": case_quality,
        }

    def append_audit(self, actor: str, action: str, details: dict[str, Any], case_id: str | None = None, before: dict[str, Any] | None = None, after: dict[str, Any] | None = None) -> None:
        self._append_audit(actor, action, details, case_id=case_id, before=before, after=after)

    def _append_audit(self, actor: str, action: str, details: dict[str, Any], case_id: str | None = None, before: dict[str, Any] | None = None, after: dict[str, Any] | None = None) -> None:
        event = AuditEvent(
            timestamp=datetime.now(timezone.utc),
            actor=actor,
            action=action,
            details=deepcopy(details),
            case_id=case_id,
            before=deepcopy(before),
            after=deepcopy(after),
        )
        self.audit_log.append(event)
        if case_id and case_id in self.cases:
            self.cases[case_id].audit_log.append({
                "timestamp": event.timestamp.isoformat(),
                "actor": actor,
                "action": action,
                "details": deepcopy(details),
            })


def build_seed_store() -> CaseStore:
    store = CaseStore()
    case = store.register_case(
        claimant_name="Lisa Miller",
        claimant_email="lisa.miller@example.com",
        policy_number="POL-1001",
        claim_amount=4000.0,
        incident_date="2026-10-18",
        case_id="CASE-0001",
    )
    case.documents = [
        Document(
            document_id="DOC-001",
            case_id=case.case_id,
            doc_type="invoice",
            file_name="repair_invoice.pdf",
            text="Invoice total $3,800. Vehicle repaired on 2026-10-18.",
            ocr_confidence=0.98,
            extracted_fields={"amount": 3800.0, "date": "2026-10-18"},
        )
    ]
    case.status = "summary_ready"
    case.next_step = "approval"
    return store
