# Deployment and Operations Runbook

## Local Setup
1. Create and activate a virtual environment.
2. Install requirements.
3. Run the Streamlit app.
4. Verify the dashboard loads successfully.
5. Run tests to confirm regression safety.

## Run Commands
```bash
cd /home/labuser/uhg-capstone
source .venv/bin/activate
streamlit run src/uhg_capstone/streamlit_app.py --server.headless true --server.address 0.0.0.0 --server.port 8501
```

## Validation Command
```bash
cd /home/labuser/uhg-capstone
source .venv/bin/activate
pytest -q
```

## Operational Notes
- Monitor queue health and approval backlog.
- Review audit logs frequently.
- Validate that sensitive content is redacted before storage or output.
- Escalate unclear or risky decisions to a human reviewer.

## Rollback Strategy
If workflow quality falls below expected thresholds:
- pause automation routing,
- revert to manual review,
- inspect audit logs and case summaries,
- re-run quality and safety checks before re-enabling automation.
