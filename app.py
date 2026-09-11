from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="RiskContext AI",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');
        :root { --ink:#17221f; --muted:#63726d; --paper:#f5f7f2; --mint:#dcefe6; --teal:#0b6b63; --coral:#ef795f; --line:#d8e2dc; }
        html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; color: var(--ink); }
        .stApp { background: var(--paper); }
        [data-testid="stSidebar"] { background: #eaf1eb; border-right: 1px solid var(--line); }
        [data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
        h1, h2, h3 { letter-spacing: -0.04em; }
        h1 { font-size: 3.2rem !important; line-height: 1.02 !important; margin-bottom: .35rem !important; }
        h2 { font-size: 1.55rem !important; }
        .brand { font-size: 1.15rem; font-weight: 700; letter-spacing: -.03em; margin-bottom: 2.6rem; }
        .brand-mark { display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:9px; margin-right:9px; background:var(--teal); color:#fff; font-family:'DM Mono'; font-size:.8rem; }
        .eyebrow { color:var(--teal); text-transform:uppercase; letter-spacing:.16em; font:500 .72rem 'DM Mono'; margin-bottom:.65rem; }
        .lede { color:var(--muted); max-width:660px; font-size:1.05rem; line-height:1.55; margin-bottom:2rem; }
        .status { display:inline-flex; align-items:center; gap:8px; border:1px solid #b9d7c7; background:#edf8f1; color:#27634d; border-radius:999px; padding:6px 10px; font:500 .72rem 'DM Mono'; }
        .status-dot { width:7px; height:7px; background:#3ca36c; border-radius:50%; }
        .section-label { color:var(--muted); text-transform:uppercase; letter-spacing:.12em; font:500 .68rem 'DM Mono'; margin:1.4rem 0 .7rem; }
        .metric-card { background:#fff; border:1px solid var(--line); border-radius:12px; padding:1.15rem 1.3rem; min-height:125px; }
        .metric-kicker { color:var(--muted); font:500 .68rem 'DM Mono'; text-transform:uppercase; letter-spacing:.1em; }
        .metric-value { font-size:2.35rem; font-weight:600; letter-spacing:-.06em; margin:.35rem 0 .2rem; }
        .metric-note { color:var(--muted); font-size:.78rem; }
        .callout { background:var(--ink); color:#f8fcf7; border-radius:14px; padding:1.35rem 1.5rem; margin:1.3rem 0; }
        .callout strong { color:#9fe0c1; }
        .callout p { color:#d5e2db; line-height:1.55; margin:.4rem 0 0; }
        .report-head { border-bottom:1px solid var(--line); padding-bottom:1rem; margin-bottom:1.2rem; }
        .small-mono { font: .72rem 'DM Mono'; color:var(--muted); }
        div[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); padding:1rem; border-radius:12px; }
        div[data-testid="stMetric"] label { font-family:'DM Mono'; text-transform:uppercase; font-size:.65rem; letter-spacing:.1em; }
        .stButton > button, .stDownloadButton > button { border-radius:8px; font-weight:600; border:1px solid var(--teal); }
        .stButton > button[kind="primary"] { background:var(--teal); }
        .stTabs [data-baseweb="tab-list"] { gap:1.5rem; }
        .stTabs [data-baseweb="tab"] { font-family:'DM Mono'; font-size:.72rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def adjusted_risk(raw_score: float, ancestry: dict[str, int], environment: dict[str, int]) -> tuple[float, float, float]:
    """A transparent demo calibration, intentionally bounded for decision support."""
    european_share = ancestry["European"] / 100
    diversity_gap = 1 - european_share
    ancestry_adjustment = diversity_gap * 0.22
    environmental_load = sum(environment.values()) / (len(environment) * 4)
    context_adjustment = ancestry_adjustment + (environmental_load - 0.5) * 0.12
    corrected = max(1, min(99, raw_score * (1 - context_adjustment)))
    confidence = max(55, min(96, 92 - diversity_gap * 24 - environmental_load * 7))
    return corrected, context_adjustment * 100, confidence


def build_report(patient_id: str, condition: str, raw: float, corrected: float, ancestry: dict[str, int], environment: dict[str, int], confidence: float) -> bytes:
    ancestry_lines = "\n".join(f"- {key}: {value}%" for key, value in ancestry.items())
    environment_lines = "\n".join(f"- {key}: {value}/4" for key, value in environment.items())
    report = f"""# RiskContext AI | Contextualized Risk Brief
Generated: {date.today().isoformat()}
Patient reference: {patient_id}
Condition: {condition}

## Risk summary
- Uncorrected PRS percentile: {raw:.0f}
- Context-adjusted percentile: {corrected:.0f}
- Model confidence: {confidence:.0f}%

## Ancestry context
{ancestry_lines}

## Environment context (0 = low, 4 = high)
{environment_lines}

## Interpretation
This report is a research prototype for clinician review. The adjusted score is a transparent contextual estimate, not a diagnosis or a replacement for validated clinical guidelines. Consider family history, clinical measurements, variant quality, and patient preferences before acting.

## Suggested next step
Use the adjusted score as one input to a shared decision conversation. Avoid ancestry-based assumptions and document the evidence considered.
"""
    return report.encode("utf-8")


inject_styles()

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">R</span>RiskContext AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Workspace</div>', unsafe_allow_html=True)
    mode = st.radio("View", ["Risk interrogator", "Method notes"], label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Pipeline</div>', unsafe_allow_html=True)
    st.markdown("**01**  Patient context\n\n**02**  Risk calibration\n\n**03**  Clinical brief")
    st.divider()
    st.markdown('<span class="small-mono">DEMO MODE  /  v0.4</span>', unsafe_allow_html=True)

if mode == "Method notes":
    st.markdown('<div class="eyebrow">Model transparency</div>', unsafe_allow_html=True)
    st.title("A score should explain itself.")
    st.markdown("The prototype uses a bounded, inspectable adjustment so clinicians can see what changes the output. It is deliberately not presented as a validated medical model.")
    st.markdown("### Calibration logic")
    st.code("context_adjustment = ancestry_gap * 0.22 + (environmental_load - 0.5) * 0.12\nadjusted_percentile = raw_percentile * (1 - context_adjustment)", language="python")
    st.markdown("### What to validate before clinical use")
    st.write("External calibration by condition and population, variant quality controls, confidence intervals, prospective clinical utility, subgroup performance, and governance for patient consent and data retention.")
    st.stop()

st.markdown('<div class="status"><span class="status-dot"></span>Decision support prototype · clinician review required</div>', unsafe_allow_html=True)
st.markdown('<div class="eyebrow" style="margin-top:1.5rem">Precision medicine / context layer</div>', unsafe_allow_html=True)
st.title("Make genetic risk\ncontextual, not absolute.")
st.markdown("<div class=\"lede\">Interrogate a polygenic risk score against ancestry composition and lived environment. Surface where a raw percentile may overstate certainty, so the clinical conversation starts with context.</div>", unsafe_allow_html=True)

with st.form("risk_form"):
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown("### Patient context")
        patient_id = st.text_input("Patient reference", value="RC-2048", help="Use a non-identifying reference for this prototype.")
        condition = st.selectbox("Risk domain", ["Coronary artery disease", "Type 2 diabetes", "Breast cancer", "Alzheimer's disease"])
        raw_score = st.slider("Raw PRS percentile", 1, 99, 78, help="Percentile from the source PRS pipeline.")
    with right:
        st.markdown("### Global ancestry estimate")
        st.caption("Sum to 100%. Use a global estimate, not a proxy for identity.")
        ancestry_cols = st.columns(4)
        ancestry = {}
        for column, label, value in zip(ancestry_cols, ["European", "African", "East Asian", "South Asian"], [42, 24, 18, 16]):
            with column:
                ancestry[label] = st.number_input(label, 0, 100, value, 1, key=f"ancestry_{label}")
    st.markdown("### Environment and access")
    env_cols = st.columns(4)
    env_labels = ["Food access", "Activity", "Air quality", "Care access"]
    env_help = ["Low access to fresh, affordable food", "Low opportunity for regular movement", "Exposure to particulate pollution", "Barriers to screening or continuity"]
    environment = {}
    for column, label, help_text in zip(env_cols, env_labels, env_help):
        with column:
            environment[label] = st.slider(label, 0, 4, 2, key=f"env_{label}", help=help_text)
    submitted = st.form_submit_button("Interrogate risk", type="primary", use_container_width=True)

if "result" not in st.session_state:
    st.session_state.result = True

if submitted:
    if sum(ancestry.values()) != 100:
        st.error(f"Ancestry estimates currently sum to {sum(ancestry.values())}%. Adjust them to exactly 100%.")
        st.stop()
    st.session_state.analysis = (patient_id, condition, raw_score, ancestry, environment)

patient_id, condition, raw_score, ancestry, environment = st.session_state.get("analysis", ("RC-2048", "Coronary artery disease", 78, {"European": 42, "African": 24, "East Asian": 18, "South Asian": 16}, {"Food access": 2, "Activity": 2, "Air quality": 2, "Care access": 2}))
corrected, delta, confidence = adjusted_risk(raw_score, ancestry, environment)

st.markdown('<div class="section-label">Analysis output</div>', unsafe_allow_html=True)
metric_a, metric_b, metric_c, metric_d = st.columns(4)
with metric_a:
    st.metric("Raw percentile", f"{raw_score:.0f}", "source PRS")
with metric_b:
    st.metric("Context-adjusted", f"{corrected:.0f}", f"{corrected - raw_score:+.0f} points")
with metric_c:
    st.metric("Context shift", f"{delta:+.1f}%", "bounded adjustment")
with metric_d:
    st.metric("Confidence", f"{confidence:.0f}%", "context completeness")

st.markdown('<div class="callout"><strong>Clinical readout</strong><p>The raw score places this profile in the high-risk band. After accounting for ancestry representation and environmental context, the estimate moves to a more cautious level. Treat the shift as a prompt to investigate, not as permission to dismiss risk.</p></div>', unsafe_allow_html=True)

tab_risk, tab_context, tab_actions = st.tabs(["Risk comparison", "Context signals", "Clinical brief"])
with tab_risk:
    chart_data = pd.DataFrame({"Score": [raw_score, corrected]}, index=["Uncorrected PRS", "Context-adjusted"])
    st.bar_chart(chart_data, color="#0b6b63", height=270)
    st.caption("Percentile scale: 0 = lower observed risk relative to reference cohort, 100 = higher observed risk. This visualization is not a diagnostic threshold.")
with tab_context:
    context_col, table_col = st.columns([1, 1.15], gap="large")
    with context_col:
        ancestry_data = pd.DataFrame({"Share": list(ancestry.values())}, index=list(ancestry.keys()))
        st.bar_chart(ancestry_data, color="#ef795f", height=260)
    with table_col:
        st.markdown("**Signals contributing to interpretation**")
        signals = pd.DataFrame({"Signal": list(environment.keys()), "Intensity": [f"{value}/4" for value in environment.values()], "Read": ["Higher context load" if value >= 3 else "Moderate context load" if value == 2 else "Lower context load" for value in environment.values()]})
        st.dataframe(signals, hide_index=True, use_container_width=True)
with tab_actions:
    st.markdown("### Suggested conversation")
    st.write(f"For {condition.lower()}, confirm the underlying PRS cohort and variant quality, review family history and clinical measurements, and discuss whether additional screening is appropriate. The ancestry adjustment should trigger calibration review, not a change in care by itself.")
    st.markdown("### Guardrails")
    st.write("Do not use the output as a diagnosis, as a basis for denying care, or as a substitute for a validated guideline. Document uncertainty and invite the patient to correct the context data.")

st.divider()
report = build_report(patient_id, condition, raw_score, corrected, ancestry, environment, confidence)
download_col, note_col = st.columns([1, 2])
with download_col:
    st.download_button("Download clinical brief", data=report, file_name=f"riskcontext_{patient_id}.md", mime="text/markdown", use_container_width=True)
with note_col:
    st.markdown('<span class="small-mono">REPORT READY  /  includes inputs, calibration output, and review guardrails</span>', unsafe_allow_html=True)