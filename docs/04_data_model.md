# Data Model

## Core Domain Objects

### ClaimCase
Represents a single claim with the following major attributes:
- case_id
- claimant_name
- claimant_email
- policy_number
- claim_amount
- incident_date
- status
- summary
- approver
- created_at

### Document
Represents supporting material associated with the case.
- document_id
- case_id
- file_name
- content
- metadata

### Policy
Represents policy context used for decisioning.
- policy_id
- policy_number
- coverage_summary
- terms

### AuditEvent
Tracks operational and decision activity.
- timestamp
- actor
- action
- case_id
- details

## Relationship Summary
- One claim can have many documents.
- One claim may be associated with one policy or policy context.
- Every operational action is recorded in the audit log.
- The workflow and dashboard aggregate across multiple claims.

## Why This Model Fits the Use Case
The schema is compact but expressive enough to support:
- case tracking,
- quality evaluation,
- human decision flows,
- operational summaries,
- safety and compliance checks.
