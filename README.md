# UHG Account FDE Capstone

This repository implements a simplified end-to-end claims-processing agent system aligned to the design in the project brief. It includes MCP-style server modules, specialist agents, a LangGraph workflow, a Streamlit UI, ledger/audit primitives, and an evaluation harness.

## Project layout

- `src/uhg_capstone/mcp/` – MCP server definitions for case, policy, document, and workflow capabilities.
- `src/uhg_capstone/agents/` – specialist agent wrappers and policy prompts.
- `src/uhg_capstone/graph/` – LangGraph orchestration and state model.
- `src/uhg_capstone/streamlit_app.py` – Streamlit user interface.
- `tests/` – smoke tests for imports and the happy path.
- `evals/` – evaluation harness scaffolding.

## Run locally

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Start infrastructure:

   ```bash
   docker compose up -d postgres mailpit phoenix
   ```

3. Run the Streamlit app:

   ```bash
   streamlit run src/uhg_capstone/streamlit_app.py
   ```

4. Run tests:

   ```bash
   pytest -q
   ```

## Design notes

- The system follows the required human-in-the-loop pattern: no agent can approve or settle a claim. The approval pause is a LangGraph interrupt.
- MCP tools are kept behind a consistent server interface with tool names that match the brief.
- A lightweight in-memory case store is used in this starter implementation to keep local execution simple while preserving the required architecture.
- The project includes a Docker Compose file for PostgreSQL, Mailpit, and Phoenix for the enterprise deployment pattern described in the brief.

## Documentation and submission pack

### Core architecture and submission documents

- [ARCHITECTURE.md](ARCHITECTURE.md) – high-level system architecture and design rationale.
- [COURSE_SUBMISSION_REPORT.md](COURSE_SUBMISSION_REPORT.md) – single submission-ready report for an FDE-style review.
- [docs/01_problem_statement.md](docs/01_problem_statement.md) – business problem and objectives.
- [docs/02_requirements.md](docs/02_requirements.md) – functional and non-functional requirements.
- [docs/03_architecture_overview.md](docs/03_architecture_overview.md) – layered architecture and component responsibilities.
- [docs/04_data_model.md](docs/04_data_model.md) – core domain model and schema.
- [docs/05_security_privacy.md](docs/05_security_privacy.md) – privacy, PII handling, and safety controls.
- [docs/06_workflow.md](docs/06_workflow.md) – end-to-end claim workflow.
- [docs/07_evaluation_plan.md](docs/07_evaluation_plan.md) – testing and quality gates.
- [docs/08_runbook.md](docs/08_runbook.md) – deployment and operations guidance.
- [docs/09_adrs.md](docs/09_adrs.md) – architecture decisions and rationale.
- [docs/10_executive_summary.md](docs/10_executive_summary.md) – executive-facing overview.
- [docs/11_presentation_outline.md](docs/11_presentation_outline.md) – 5-minute presentation outline.

## Presentation assets

This section gathers the presentation materials for quick access and a clean handoff to reviewers, faculty, or stakeholders.

- [UHG_FDE_CAPSTONE_PRESENTATION.pptx](UHG_FDE_CAPSTONE_PRESENTATION.pptx) – final polished deck for the course presentation.
- [COURSE_SUBMISSION_REPORT.md](COURSE_SUBMISSION_REPORT.md) – single-page narrative and submission-ready write-up.
- [docs/11_presentation_outline.md](docs/11_presentation_outline.md) – concise 5-minute presentation flow and speaker guide.
- [ARCHITECTURE.md](ARCHITECTURE.md) – architecture overview for explaining the system design.
- [docs/10_executive_summary.md](docs/10_executive_summary.md) – executive summary for a brief stakeholder update.

### Quick summary

Use the deck for the live presentation, the outline for the delivery flow, and the report for the written rationale. Together, these files provide a complete presentation package with business context, architecture explanation, and the supporting narrative.
