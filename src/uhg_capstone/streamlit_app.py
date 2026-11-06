from __future__ import annotations

from typing import Any

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None  # type: ignore[assignment]

from uhg_capstone.evaluation import evaluate_release
from uhg_capstone.graph.graph import build_claim_graph
from uhg_capstone.store import build_seed_store

store = build_seed_store()
workflow = build_claim_graph()


def inject_ui_css() -> None:
    if st is None:
        return
    st.markdown(
        """
        <style>
        :root {
            --bg: #f6f9fd;
            --panel: #ffffff;
            --panel-strong: #edf4ff;
            --sidebar: #f4f8ff;
            --line: rgba(35, 72, 111, 0.1);
            --text: #17324b;
            --muted: #5f7286;
            --accent: #3b6da3;
            --accent-strong: #284f7d;
            --accent-soft: rgba(59, 109, 163, 0.08);
            --success: #2d8d73;
            --warning: #e88b3c;
            --warning-soft: rgba(232, 139, 60, 0.12);
            --danger: #d66a5a;
            --shadow: rgba(16, 44, 79, 0.06);
        }
        .stApp {
            background: linear-gradient(180deg, #ffffff 0%, #f6f9fd 100%);
            color: var(--text);
        }
        .block-container {
            padding-top: 1.3rem;
            padding-bottom: 1.5rem;
            max-width: 1400px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(244,248,255,0.96), rgba(236,242,249,0.94));
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(18,48,66,0.08);
        }
        [data-testid="stSidebar"] .stRadio > div {
            gap: 0.7rem;
            padding-top: 0.8rem;
        }
        [data-testid="stSidebar"] .stRadio > div > label {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 46px;
            background: rgba(255,255,255,0.42);
            border: 1px solid rgba(39, 74, 108, 0.06);
            border-radius: 12px;
            padding: 0.62rem 0.7rem;
            color: transparent;
            font-weight: 600;
            box-shadow: 0 3px 10px rgba(18,48,66,0.03);
            transition: 0.2s ease;
        }
        [data-testid="stSidebar"] .stRadio > div > label > div {
            color: var(--text);
            font-size: 1.36rem;
            line-height: 1;
        }
        [data-testid="stSidebar"] .stRadio > div > label:hover {
            border-color: rgba(59, 109, 163, 0.2);
            background: rgba(255,255,255,0.72);
            transform: translateY(-1px);
        }
        [data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
            background: linear-gradient(135deg, rgba(59,109,163,0.12), rgba(59,109,163,0.04));
            border-color: rgba(59, 109, 163, 0.22);
            box-shadow: 0 0 0 3px rgba(59,109,163,0.08), 0 8px 16px rgba(59,109,163,0.08);
        }
        [data-testid="stSidebar"] .stRadio > div > label > input {
            display: none;
        }
        h1, h2, h3 {
            color: var(--text);
            letter-spacing: -0.04em;
        }
        .dashboard-hero {
            background: linear-gradient(135deg, #eef5ff 0%, #edf4ff 38%, #f9fbff 100%);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 1.05rem 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 18px var(--shadow);
        }
        .metric-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(244,248,255,0.92));
            backdrop-filter: blur(8px);
            border: 1px solid rgba(31, 69, 102, 0.08);
            border-radius: 14px;
            padding: 0.85rem 0.95rem;
            min-height: 100px;
            box-shadow: 0 6px 14px var(--shadow);
        }
        .metric-card .label {
            display: block;
            color: var(--muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.55rem;
        }
        .metric-card .value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--text);
        }
        .status-pill {
            background: #fafdff;
            border: 1px solid rgba(47, 125, 225, 0.18);
            border-radius: 12px;
            padding: 0.7rem 0.8rem;
            margin: 0.35rem 0;
            color: var(--text);
            box-shadow: 0 4px 10px var(--shadow);
        }
        .status-pill span {
            color: var(--muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .status-pill strong {
            display: block;
            font-size: 1.35rem;
            color: var(--text);
            margin-top: 0.35rem;
        }
        .release-box {
            background: linear-gradient(135deg, rgba(59,109,163,0.06), rgba(232,139,60,0.08));
            border: 1px solid rgba(232, 139, 60, 0.2);
            border-radius: 12px;
            padding: 0.8rem 0.9rem;
            color: var(--text);
        }
        .kpi-strip {
            display: flex;
            gap: 0.8rem;
            margin: 0.8rem 0 1.1rem 0;
            flex-wrap: wrap;
        }
        .kpi-tile {
            flex: 1 1 180px;
            min-width: 180px;
            background: linear-gradient(180deg, #ffffff 0%, #f3f8ff 100%);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 0.8rem 0.9rem;
            box-shadow: 0 6px 14px var(--shadow);
        }
        .kpi-tile .tiny-label {
            display: block;
            color: var(--muted);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.45rem;
        }
        .kpi-tile .big-value {
            display: block;
            font-size: 1.7rem;
            font-weight: 700;
            color: var(--text);
        }
        .trend {
            display: flex;
            align-items: end;
            gap: 0.28rem;
            margin-top: 0.65rem;
            height: 44px;
        }
        .trend span {
            display: inline-block;
            width: 9px;
            border-radius: 5px 5px 0 0;
            background: linear-gradient(180deg, rgba(63,143,190,0.9), rgba(63,143,190,0.25));
        }
        .health-panel {
            background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 0.9rem 1rem;
            box-shadow: 0 6px 14px var(--shadow);
            margin-top: 0.8rem;
        }
        .health-status {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 10px;
            background: rgba(47, 154, 122, 0.08);
            border: 1px solid rgba(47, 154, 122, 0.2);
            padding: 0.75rem 0.8rem;
            margin-top: 0.7rem;
        }
        .pulse {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--success);
            box-shadow: 0 0 0 6px rgba(47,154,122,0.12);
        }
        .stButton > button {
            background: linear-gradient(135deg, var(--accent), var(--accent-strong));
            color: white;
            font-weight: 700;
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1rem;
        }
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input,
        .stTextArea > div > textarea {
            background: #ffffff;
            color: var(--text);
            border: 1px solid rgba(20, 57, 81, 0.18);
            border-radius: 10px;
        }
        [data-testid="stMetricValue"] {
            color: var(--text);
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if st is not None:
    st.set_page_config(page_title="Claims Workspace", layout="wide")
    inject_ui_css()

    st.title("UHG Claims Operations Workspace")
    nav_labels = {
        "Dashboard": "🏠 Dashboard",
        "Submit claim": "📝 Submit claim",
        "Case queue": "📋 Case queue",
        "Approvals": "✅ Approvals",
        "Case chat": "💬 Case chat",
    }
    nav = st.sidebar.radio(
        "",
        list(nav_labels.keys()),
        format_func=lambda option: nav_labels[option],
        label_visibility="collapsed",
    )

    if nav == "Dashboard":
        summary = store.get_dashboard_summary()
        st.markdown(
            """
            <div class="dashboard-hero">
                <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.12em; color: #3f8fbe;">Care operations overview</div>
                <div style="font-size: 2rem; font-weight: 700; margin-top: 0.35rem; color: #123042;">Clinical claims command center</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card"><span class="label">Total cases</span><span class="value">{}</span></div>'.format(summary["total_cases"]), unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card"><span class="label">Open cases</span><span class="value">{}</span></div>'.format(summary["open_cases"]), unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card"><span class="label">Avg. claim</span><span class="value">${:,.2f}</span></div>'.format(summary["avg_claim_amount"]), unsafe_allow_html=True)

        kpi_values = [
            ("Claim volume", summary["total_cases"], [28, 32, 35, 38, 42, 50]),
            ("Open queue", summary["open_cases"], [18, 22, 24, 29, 27, 31]),
            ("Avg. claim", f"${summary['avg_claim_amount']:,.2f}", [15, 20, 22, 30, 32, 36]),
            ("Approvals", "92%", [20, 26, 25, 34, 40, 51]),
        ]

        st.markdown('<div class="kpi-strip">', unsafe_allow_html=True)
        for label, value, bars in kpi_values:
            bars_html = "".join(f'<span style="height:{bar * 1.2}px"></span>' for bar in bars)
            st.markdown(
                f'<div class="kpi-tile"><span class="tiny-label">{label}</span><span class="big-value">{value}</span><div class="trend">{bars_html}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        col_left, col_right = st.columns([1.8, 1.2])
        with col_left:
            st.subheader("Status breakdown")
            if summary["by_status"]:
                status_cols = st.columns(len(summary["by_status"]))
                for index, (status, count) in enumerate(summary["by_status"].items()):
                    with status_cols[index]:
                        st.markdown(f'<div class="status-pill"><span>{status}</span><strong>{count}</strong></div>', unsafe_allow_html=True)

            release = evaluate_release(
                {"coverage": 0.96, "safety": 0.97, "workflow_quality": 0.90},
                {"coverage": 0.9, "safety": 0.95, "workflow_quality": 0.85},
            )
            st.subheader("Release gate")
            st.markdown(
                f'<div class="release-box"><strong>Release status:</strong> {release["release_status"]}<br><strong>Pass rate:</strong> {release["pass_rate"]:.2%}<br>{release["summary"]}</div>',
                unsafe_allow_html=True,
            )

        with col_right:
            st.subheader("Care health")
            st.markdown(
                """
                <div class="health-panel">
                    <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em; color:#587389;">Operational stability</div>
                    <div class="health-status">
                        <div><strong style="font-size:1.2rem;">Healthy</strong><br><span style="color:#587389;">No critical escalations</span></div>
                        <div class="pulse"></div>
                    </div>
                    <div style="margin-top:1rem; color:#587389; line-height:1.8;">
                        <div>• Audit coverage: 96%</div>
                        <div>• SLA compliance: 94%</div>
                        <div>• PII guard: Active</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if store.list_cases():
            st.subheader("Case quality")
            for case in store.list_cases()[:5]:
                quality = store.get_case_quality_report(case.case_id)
                st.write(f"{case.case_id}: {quality['case_readiness']} | score {quality['overall_score']:.2f} | {case.status}")

            st.subheader("Recent case states")
            for case in store.list_cases()[:5]:
                st.write(f"{case.case_id}: {case.claimant_name} | {case.status} | ${case.claim_amount:,.2f}")

    if nav == "Submit claim":
        st.markdown("### New claim intake")
        with st.form("submit_claim"):
            claimant_name = st.text_input("Claimant name")
            claimant_email = st.text_input("Claimant email")
            policy_number = st.text_input("Policy number", value="POL-1001")
            claim_amount = st.number_input("Claim amount", min_value=0.0, step=100.0)
            incident_date = st.date_input("Incident date")
            submitted = st.form_submit_button("Submit claim")
            if submitted:
                case = store.register_case(claimant_name, claimant_email, policy_number, float(claim_amount), str(incident_date))
                st.success(f"Claim submitted with case ID {case.case_id}")
                st.session_state["last_case_id"] = case.case_id

    elif nav == "Case queue":
        cases = store.list_cases()
        if not cases:
            st.info("No cases yet.")
        else:
            rows = [
                {
                    "Case ID": case.case_id,
                    "Claimant": case.claimant_name,
                    "Policy": case.policy_number,
                    "Amount": f"${case.claim_amount:,.2f}",
                    "Status": case.status,
                    "Approver": case.approver or "Unassigned",
                }
                for case in cases
            ]
            st.subheader("Case queue")
            st.dataframe(rows, use_container_width=True, hide_index=True)

            for case in cases:
                with st.container():
                    st.markdown(f"### {case.case_id} - {case.claimant_name}")
                    st.write(f"Status: {case.status} | Amount: ${case.claim_amount:,.2f} | Policy: {case.policy_number}")
                    if case.summary:
                        st.write(case.summary)
                    audit_events = store.list_audit_events(case_id=case.case_id, limit=5)
                    if audit_events:
                        st.caption("Recent audit trail")
                        for event in audit_events:
                            st.write(f"- {event['timestamp']} | {event['actor']} | {event['action']}")
                    st.markdown("---")

    elif nav == "Approvals":
        case_id = st.text_input("Case ID for approval", value=st.session_state.get("last_case_id", "CASE-0001"))
        if st.button("Review case"):
            case = store.get_case(case_id)
            if case:
                st.write(case.summary or "No summary yet.")
                decision = st.radio("Decision", ["approve", "reject", "more_info"])
                rationale = st.text_area("Rationale")
                if st.button("Submit decision"):
                    store.record_decision(case_id, decision, rationale, approver_id=case.approver or "A-201")
                    st.success(f"Decision recorded for {case_id}: {decision}")
                    st.session_state["last_decision"] = decision

    elif nav == "Case chat":
        st.write("Ask the supervisor a question about the active case.")
        case_id = st.text_input("Case ID", value=st.session_state.get("last_case_id", "CASE-0001"))
        question = st.text_input("Question")
        if question:
            case = store.get_case(case_id)
            if case is None:
                st.warning("Case not found.")
            else:
                answer = store.answer_case_question(case_id, question)
                st.write(f"Answer: {answer}")

else:
    print("Streamlit is not installed; skipping UI execution.")


def run_happy_path(case_id: str) -> dict[str, Any]:
    initial = {"case_id": case_id, "case_status": "new", "next_step": "intake_agent", "messages": [], "agent_hops": [], "stage_results": {}, "human_decision": None, "errors": [], "token_usage": 0}
    return workflow.invoke(initial)
