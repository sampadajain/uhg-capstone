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
