# RiskContext AI

An ancestry- and environment-aware Streamlit prototype for interrogating polygenic risk scores. It is designed as a clinical decision-support interface, not a diagnostic device.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The prototype uses a deliberately transparent, bounded calibration formula. Replace it with externally validated, condition-specific models before any clinical use.