# Architecture Decision Record (ADR)

## ADR 1: Use Streamlit as the operational interface
Decision: Use a lightweight UI for analyst interaction and dashboarding.

Reason:
- fast to prototype,
- familiar for operational teams,
- suitable for rapid stakeholder review and iteration.

## ADR 2: Use a graph-based workflow for orchestration
Decision: Implement the core workflow with a stateful graph structure.

Reason:
- explicit state transitions,
- clear routing and escalation paths,
- easier to reason about and extend.

## ADR 3: Keep a human in the approval loop
Decision: AI-generated recommendations are not final decisions by themselves.

Reason:
- healthcare workflow requires accountability,
- reduces automation risk,
- supports trust and governance.

## ADR 4: Prioritize safety and auditability
Decision: Embed PII handling and prompt injection checks early in the workflow.

Reason:
- data sensitivity requires strong controls,
- audit logs are necessary for compliance and confidence.
