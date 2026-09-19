from datetime import date
import json
import pandas as pd
import streamlit as st
from pgs_engine import MODEL, build_audit_record, interpret_score, validate_genotype_upload

st.set_page_config(page_title="RiskContext T2D",page_icon="🧬",layout="wide")
st.markdown("""<style>:root{--ink:#10231f;--muted:#60716b;--paper:#f5f8f5;--teal:#087064;--line:#d5e3dc}.stApp{background:var(--paper)}[data-testid="stSidebar"]{background:#e8f1ec;border-right:1px solid var(--line)}h1,h2,h3{letter-spacing:-.035em}.hero{font-size:3.1rem;font-weight:760;line-height:1.04;color:var(--ink)}.lede{color:var(--muted);font-size:1.05rem;max-width:780px;margin:.7rem 0 1.4rem}.pill{display:inline-block;padding:.35rem .7rem;border:1px solid #a8d4c5;border-radius:999px;background:#ecf9f4;color:#185d4d;font-size:.78rem}.notice{background:#fff6dc;border-left:4px solid #d89a17;padding:1rem 1.15rem;border-radius:8px;margin:1rem 0}div[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);padding:1rem;border-radius:12px}</style>""",unsafe_allow_html=True)

with st.sidebar:
    st.title("🧬 RiskContext T2D"); page=st.radio("Workspace",["Assessment","Genotype pipeline","Evidence & safety"]); st.divider(); st.caption(f"Model: {MODEL['id']} · {MODEL['name']}"); st.caption("South Asian–optimized research workflow")

if page=="Evidence & safety":
    st.title("Published model, visible limitations")
    st.markdown(f"""This version references **[{MODEL['id']}]({MODEL['catalog_url']})**, a published Type 2 diabetes polygenic score optimized and evaluated for South Asian ancestry.

- Method: {MODEL['method']}
- Genome build: {MODEL['genome_build']}
- Variants: {MODEL['variant_count']:,}
- Reported South Asian AUROC: {MODEL['auroc_low']:.3f}–{MODEL['auroc_high']:.3f}
- Reported odds ratio per SD: {MODEL['or_per_sd']:.2f}

The app reports relative genetic odds, not absolute disease probability. Published performance does not prove accuracy in Pakistani patients.""")
    st.warning("Research use only. Do not use this output to diagnose diabetes or change medication."); st.stop()

if page=="Genotype pipeline":
    st.title("Genotype input readiness")
    st.write("The official score contains about 1.3 million variants. Upload validation checks readiness; reproducible scoring should run through the official PGS Catalog pipeline in a controlled environment.")
    uploaded=st.file_uploader("Upload genotype file for format validation",type=["vcf","gz","pgen","bed"]); build=st.selectbox("Declared genome build",["GRCh37","GRCh38","Unknown"])
    if uploaded:
        report=validate_genotype_upload(uploaded.name,uploaded.size,build); (st.success if report.ready else st.error)(report.message); st.json(report.to_dict())
    st.code("pgscatalog-download --pgs PGS005336\nnextflow run pgscatalog/pgsc_calc -profile docker --input samplesheet.csv --pgs_id PGS005336 --target_build GRCh37",language="bash")
    st.caption("Uploaded files are not scored or saved by this prototype."); st.stop()

st.markdown('<span class="pill">PGS Catalog evidence · clinician review required</span>',unsafe_allow_html=True)
st.markdown('<div class="hero">Type 2 diabetes genetic risk,<br>grounded in published evidence.</div>',unsafe_allow_html=True)
st.markdown('<div class="lede">Interpret a standardized PGS005336 result using performance reported in South Asian evaluation cohorts. Clinical measurements remain separate so the app does not invent an unvalidated combined probability.</div>',unsafe_allow_html=True)
st.markdown('<div class="notice"><b>Research use only.</b> Diabetes diagnosis requires validated laboratory testing and clinical evaluation.</div>',unsafe_allow_html=True)

with st.form("assessment"):
    st.subheader("1 · PGS005336 result"); c1,c2,c3=st.columns(3)
    with c1: case_ref=st.text_input("Anonymous case reference","DEMO-001"); z=st.number_input("Standardized PGS (z-score)",-5.0,5.0,0.0,.1)
    with c2: source=st.selectbox("Score source",["PGS Catalog pipeline","Clinical genetics laboratory","Research pipeline","Unknown"]); build=st.selectbox("Genome build",["GRCh37","GRCh38","Unknown"])
    with c3: coverage=st.slider("Variant coverage",0,100,90); ancestry=st.selectbox("Reference match",["South Asian","Mixed/other","Unknown"])
    st.subheader("2 · Clinical context (shown separately)"); left,right=st.columns(2)
    with left: age=st.number_input("Age",18,100,40); bmi=st.number_input("BMI",10.0,60.0,25.0,.1); family=st.checkbox("Parent or sibling with Type 2 diabetes")
    with right: hba1c=st.number_input("HbA1c % (0 if unavailable)",0.0,20.0,0.0,.1); glucose=st.number_input("Fasting glucose mg/dL (0 if unavailable)",0.0,600.0,0.0,1.0); symptoms=st.checkbox("Possible hyperglycaemia symptoms")
    consent=st.checkbox("I understand this is research interpretation, not diagnosis."); submitted=st.form_submit_button("Interpret published score",type="primary",use_container_width=True)

if submitted:
    if not consent: st.error("Confirm the research-only limitation."); st.stop()
    result=interpret_score(z,coverage,ancestry,build,source); clinical={"age":age,"bmi":bmi,"family_history":family,"hba1c":hba1c,"fasting_glucose":glucose,"symptoms":symptoms}; st.session_state.analysis={"case_ref":case_ref.strip() or "DEMO","z_score":z,"coverage":coverage,"ancestry":ancestry,"build":build,"source":source,"clinical":clinical,"result":result}
if "analysis" not in st.session_state: st.info("Enter a quality-controlled PGS005336 z-score to see its interpretation."); st.stop()

a=st.session_state.analysis; r=a["result"]; clinical=a["clinical"]; st.divider(); st.subheader("Genetic interpretation")
m1,m2,m3,m4=st.columns(4); m1.metric("PGS percentile",f"{r.percentile:.1f}th"); m2.metric("Relative genetic odds",f"{r.relative_odds:.2f}×","vs population mean"); m3.metric("Evidence quality",f"{r.quality_score}/100","not accuracy"); m4.metric("Genetic band",r.band)
for warning in r.warnings: st.warning(warning)
t1,t2,t3=st.tabs(["Evidence","Clinical checks","Audit & export"])
with t1:
    st.dataframe(pd.DataFrame({"South Asian cohort":["UK Biobank","All of Us","MGBB"],"N":[6605,3217,607],"Reported AUROC":[.720,.839,.834]}),hide_index=True,use_container_width=True); st.write("Odds are not the same as probability; performance varies by cohort.")
with t2:
    if clinical["hba1c"]>=6.5 or clinical["fasting_glucose"]>=126: st.error("Entered laboratory value is in a commonly used diabetes diagnostic range. Seek clinical confirmation.")
    elif clinical["hba1c"]>=5.7 or 100<=clinical["fasting_glucose"]<126: st.warning("Entered value may fall in a prediabetes range. Discuss confirmatory testing with a clinician.")
    else: st.info("No diagnostic-range value was entered. Genetic risk does not replace glucose or HbA1c testing.")
with t3:
    audit=build_audit_record(a["case_ref"],a["z_score"],a["coverage"],a["ancestry"],a["build"],a["source"],r,clinical); st.json(audit); st.download_button("Download audit JSON",json.dumps(audit,indent=2),f"riskcontext_{a['case_ref']}.json","application/json",use_container_width=True)
st.error("Do not use this result alone for diagnosis, treatment, insurance, employment, or denial of care.")
