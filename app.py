from datetime import date
import json

import pandas as pd
import streamlit as st

from risk_engine import CONDITION_WEIGHTS, assess_risk, recommendations

st.set_page_config(page_title="RiskContext AI", page_icon="🧬", layout="wide")

st.markdown("""
<style>
:root {--ink:#11231f;--muted:#61716c;--paper:#f5f7f3;--teal:#086b60;--line:#d8e4dd;}
.stApp{background:var(--paper)}
[data-testid="stSidebar"]{background:#eaf2ed;border-right:1px solid var(--line)}
h1,h2,h3{letter-spacing:-.035em}.hero{font-size:3.2rem;font-weight:750;line-height:1.04;color:var(--ink)}
.lede{color:var(--muted);font-size:1.05rem;max-width:760px;margin:.7rem 0 1.4rem}
.pill{display:inline-block;padding:.35rem .7rem;border:1px solid #a9d1c4;border-radius:999px;background:#edf8f3;color:#195d4c;font-size:.78rem}
.notice{background:#fff6dc;border-left:4px solid #d89a17;padding:1rem 1.15rem;border-radius:8px;margin:1rem 0}
div[data-testid="stMetric"]{background:white;border:1px solid var(--line);padding:1rem;border-radius:12px}
.stButton>button,.stDownloadButton>button{border-radius:9px;font-weight:650}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🧬 RiskContext AI")
    page = st.radio("Workspace", ["Risk assessment", "Method & safety"])
    st.divider()
    st.caption("Research prototype · v1.0")
    st.caption("Do not enter names, IDs, or other identifying health information.")

if page == "Method & safety":
    st.title("Transparent by design")
    st.write("This app is a deterministic decision-support demonstration—not a trained diagnostic model. It combines an existing PRS percentile with condition-specific context weights and widens uncertainty when evidence quality is weak.")
    st.subheader("What the output means")
    st.markdown("- **Adjusted percentile:** a bounded contextual estimate, not disease probability.\n- **Uncertainty interval:** a sensitivity range driven by cohort match and variant quality.\n- **Data quality:** evidence completeness, not model accuracy.\n- **Contributions:** the visible effect of every factor group.")
    st.subheader("Required before clinical use")
    st.write("External cohort validation, calibration curves, AUROC/sensitivity/specificity, subgroup fairness analysis, prospective evaluation, privacy controls, audit logging, clinical governance, and applicable regulatory approval.")
    st.info("100% accuracy is neither demonstrated nor promised. Real medical performance must be measured on representative, unseen data.")
    st.stop()

st.markdown('<span class="pill">Decision support · clinician review required</span>', unsafe_allow_html=True)
st.markdown('<div class="hero">Genetic risk, with the context<br>the raw score leaves out.</div>', unsafe_allow_html=True)
st.markdown('<div class="lede">Explore how evidence quality, family history, clinical factors, and environment affect interpretation of a polygenic-risk percentile. Every adjustment is visible and exportable.</div>', unsafe_allow_html=True)
st.markdown('<div class="notice"><b>Research use only.</b> This is not a diagnosis, medical device, or substitute for validated clinical guidelines.</div>', unsafe_allow_html=True)

with st.form("assessment"):
    st.subheader("1 · Genetic evidence")
    a, b, c = st.columns(3)
    with a:
        patient_ref = st.text_input("Anonymous case reference", "DEMO-001")
        condition = st.selectbox("Condition", list(CONDITION_WEIGHTS))
    with b:
        raw = st.slider("Source PRS percentile", 1, 99, 72)
        cohort_match = st.slider("Reference-cohort match", 0, 4, 2, help="0 = unknown/poor, 4 = strong documented match")
    with c:
        variant_quality = st.slider("Variant quality", 0, 4, 3, help="0 = unknown/poor, 4 = verified high quality")
        family = st.select_slider("Family history", options=[0, 1, 2], value=1, format_func=lambda x: ["None known", "One close relative", "Multiple/early onset"][x])

    st.subheader("2 · Ancestry context")
    st.caption("Technical global ancestry estimate only; it is not identity, race, or a basis for care decisions. Values must total 100%.")
    cols = st.columns(4)
    ancestry = {}
    for col, label, default in zip(cols, ["European", "African", "East Asian", "South Asian"], [25, 25, 25, 25]):
        with col:
            ancestry[label] = st.number_input(label, 0, 100, default, 1)
    st.caption(f"Current total: {sum(ancestry.values())}%")

    st.subheader("3 · Clinical and access context")
    clinical = {}
    environment = {}
    left, right = st.columns(2)
    with left:
        st.markdown("**Clinical burden** · 0 low, 4 high")
        for label in ["Blood pressure", "Metabolic markers", "Smoking exposure"]:
            clinical[label] = st.slider(label, 0, 4, 2 if label != "Smoking exposure" else 0)
    with right:
        st.markdown("**Environment / access barriers** · 0 low, 4 high")
        for label in ["Food access", "Activity barriers", "Air quality", "Care barriers"]:
            environment[label] = st.slider(label, 0, 4, 2)
    consent = st.checkbox("I understand this is a non-diagnostic research prototype.")
    submitted = st.form_submit_button("Run transparent assessment", type="primary", use_container_width=True)

if submitted:
    if not consent:
        st.error("Please confirm that you understand the research-only limitation.")
        st.stop()
    try:
        st.session_state.case = {"patient_ref": patient_ref.strip() or "DEMO", "condition": condition, "raw": raw, "ancestry": ancestry, "environment": environment, "clinical": clinical, "family": family, "cohort_match": cohort_match, "variant_quality": variant_quality}
    except Exception as exc:
        st.error(str(exc))

if "case" not in st.session_state:
    st.info("Complete the form and run the assessment to see results.")
    st.stop()

case = st.session_state.case
try:
    result = assess_risk(case["condition"], case["raw"], case["ancestry"], case["environment"], case["clinical"], case["family"], case["cohort_match"], case["variant_quality"])
except ValueError as exc:
    st.error(str(exc)); st.stop()

st.divider(); st.subheader("Assessment result")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Source PRS", f"{case['raw']:.0f}th", "percentile")
m2.metric("Context estimate", f"{result.adjusted_percentile:.1f}th", f"{result.adjusted_percentile-case['raw']:+.1f} points")
m3.metric("Uncertainty range", f"{result.lower_bound:.0f}–{result.upper_bound:.0f}", "sensitivity interval")
m4.metric("Evidence quality", f"{result.data_quality:.0f}/100", "not accuracy")

st.markdown(f"### Interpretation: {result.category} contextual band")
st.write("The interval matters more than the point estimate. A band crossing a category boundary means the classification is unstable and should not drive a decision.")
for warning in result.warnings:
    st.warning(warning)

tab1, tab2, tab3 = st.tabs(["Why this result", "Next steps", "Audit & export"])
with tab1:
    chart = pd.DataFrame({"Contribution (points)": result.contributions}).sort_values("Contribution (points)")
    st.bar_chart(chart, color="#086b60", horizontal=True)
    st.caption("Positive values raise and negative values lower the contextual estimate. Evidence-quality inputs primarily affect uncertainty.")
with tab2:
    for index, step in enumerate(recommendations(case["condition"], result), 1):
        st.write(f"**{index}.** {step}")
    st.error("Never use this output to diagnose disease, change medication, deny care, or avoid screening.")
with tab3:
    audit = {"generated": date.today().isoformat(), "model_version": "transparent-demo-1.0", "inputs": case, "result": result.to_dict(), "limitations": "Research prototype; not clinically validated."}
    st.json(audit)
    report = f"""# RiskContext AI brief\n\nGenerated: {audit['generated']}  \nCase: {case['patient_ref']}  \nCondition: {case['condition']}\n\n- Source PRS percentile: {case['raw']}\n- Context estimate: {result.adjusted_percentile}\n- Uncertainty range: {result.lower_bound}–{result.upper_bound}\n- Evidence quality: {result.data_quality}/100 (not accuracy)\n- Interpretation band: {result.category}\n\n## Warnings\n""" + "\n".join(f"- {w}" for w in result.warnings or ["No automatic warnings."]) + "\n\n## Limitation\nResearch-only demonstration. Not a diagnosis or clinical recommendation."
    d1, d2 = st.columns(2)
    d1.download_button("Download clinical brief", report.encode(), f"riskcontext_{case['patient_ref']}.md", "text/markdown", use_container_width=True)
    d2.download_button("Download audit JSON", json.dumps(audit, indent=2), f"riskcontext_{case['patient_ref']}.json", "application/json", use_container_width=True)
