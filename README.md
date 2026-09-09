# DataGuardian AI

AI-assisted data quality monitoring and validation tool built with Python, Pandas, Streamlit, and Gemini.

## Live Demo

🔗 [Open DataGuardian AI](https://dataguardian-ai-mvp-033.streamlit.app/)

## What It Does

DataGuardian AI analyzes uploaded CSV datasets and detects common data-quality issues before they reach downstream analytics or ML workflows.

### Architecture

**CSV Dataset**
↓
**Data Quality Engine**
- Missing values
- Duplicate records
- Numerical outliers
- Schema and data-type validation
↓
**Quality Score + Validation**
↓
**PASS / WARNING / BLOCK**
↓
**Gemini AI**
↓
**Business Impact + Remediation**

The core validation is deterministic and handled by Python. Gemini is used only to explain detected issues and recommend actions.

### Features

- Missing value detection
- Duplicate record detection
- Numerical outlier detection using IQR
- Schema and data-type validation
- Data quality score
- PASS / WARNING / BLOCK quality gate
- Gemini-powered business impact analysis
- Recommended remediation actions
- Downloadable quality report

## Tech Stack

- Python
- Pandas
- NumPy
- Streamlit
- Google Gemini API

## Run Locally
pip install -r requirements.txt
streamlit run app.py
