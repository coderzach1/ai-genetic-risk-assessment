# RiskContext T2D

An evidence-linked Streamlit research app for interpreting the South Asian–optimized **PGS005336 (D_MetPRS_SAS)** Type 2 diabetes polygenic score.

## What changed

- Replaced the hand-written contextual risk formula with a published PGS Catalog model reference
- Reports percentile and relative genetic odds from a standardized PGS z-score
- Shows published South Asian evaluation cohorts and AUROC values
- Validates genotype upload format/build readiness without retaining or pretending to score incomplete files
- Keeps clinical measurements separate from the genetic association
- Flags low variant coverage, ancestry mismatch, genome-build mismatch, and unverified score sources
- Produces an auditable JSON record

## Model evidence

- PGS Catalog: [PGS005336](https://www.pgscatalog.org/score/PGS005336/)
- Trait: Type 2 diabetes
- Method: LDpred2
- Genome build: GRCh37
- Variants: 1,297,046
- Reported South Asian AUROC: 0.720–0.839 across listed cohorts

Published performance is cohort-specific and does not establish accuracy for Pakistani clinical deployment.

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
```

## Genotype scoring

Full PGS005336 scoring requires harmonized genomic data and roughly 1.3 million variants. Run the official `pgsc_calc` workflow in a consented, secure research environment; then provide the standardized score and quality metrics to this app. The Streamlit interface does not retain or calculate uploaded genomic files.

> **Research use only:** not a diagnostic device and not a substitute for glucose/HbA1c testing, professional judgment, local validation, or regulatory approval.
