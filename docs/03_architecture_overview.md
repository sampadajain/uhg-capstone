# Architecture Overview

## System Goals
The solution is a lightweight claims operations platform designed to simulate a real-world, human-in-the-loop workflow for case intake, review, routing, and approval. The design prioritizes operational clarity, auditable decisions, and safe handling of sensitive information.

## Architectural Approach
The platform follows a layered architecture:

1. Presentation Layer
   - Streamlit-based dashboard and operational console
   - Case intake, queue monitoring, approvals, and chat-style case interaction

2. Application Layer
   - Business logic in the case store
   - Workflow orchestration through a LangGraph-based graph
   - Decision routing and state transitions

3. Security Layer
   - PII redaction
   - Prompt injection detection
   - Safe handling of user inputs and external content

4. Data Layer
   - In-memory workflow store for claims state
   - Audit trail and case context metadata
   - Operational summary and quality metrics

## Component Responsibilities
### Streamlit UI
Provides the user-facing interface for:
- dashboard overview
- claim intake
- case queue
- approval review
- case chat

### Case Store
Acts as the central state manager for:
- case registration
- document attachments
- summary generation
- status transitions
- audit records
- dashboard metrics

### Workflow Graph
Coordinates the end-to-end claims process using a stateful graph approach:
- intake
- document review
- summary generation
- routing
- human review
- closure or escalation

### Security Module
Protects system integrity by screening inputs and handling sensitive data appropriately.

### Evaluation Layer
Measures operational effectiveness and release readiness using thresholds and quality metrics.

## Design Rationale
This architecture is intentionally practical and deployable for a forward-deployed engineering environment. It delivers:
- strong operational visibility,
- a real workflow model,
- minimal complexity without sacrificing traceability,
- a direct bridge from prototype to production-ready decision support.

## Architecture Principles
- Human-in-the-loop decisions remain central.
- Data and actions are auditable.
- Safety controls are part of the workflow, not an afterthought.
- Metrics are used to monitor quality and operational readiness.
