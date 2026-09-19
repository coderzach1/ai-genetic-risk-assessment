# RiskContext AI

A transparent Streamlit research prototype that combines an imported polygenic-risk percentile with family history, clinical context, environment/access, cohort match, and variant quality.

## Features

- Condition-specific, bounded risk-context calculation
- Explicit uncertainty interval instead of a misleading “accuracy” claim
- Data-quality score and validation warnings
- Explainable factor contributions
- Dynamic next-step recommendations
- Downloadable JSON audit record and Markdown clinical brief
- Deterministic unit tests

> **Research use only:** this repository does not contain a clinically validated model and must not be used to diagnose, treat, deny care, or replace professional judgment. No medical AI can honestly guarantee 100% accuracy.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

## Validation path

Before real clinical use, replace the demonstration engine with a locked, versioned model; validate discrimination and calibration on external cohorts; publish subgroup metrics and confidence intervals; test prospectively; add consent, privacy, retention, access-control, and clinical-governance workflows; and obtain the required regulatory review.
