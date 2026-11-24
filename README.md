# Employee Attrition Intelligence Dashboard

A Streamlit EDA dashboard built from the supplied employee attrition CSV.

## Project contents
- `app.py` — interactive dashboard with department, job role, tenure, overtime and travel filters.
- `analysis.py` — reusable data validation and KPI helpers.
- `data/employee_attrition.csv` — input dataset supplied for this project.
- `reports/` — research paper and executive summary.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `streamlit run app.py`
6. Open the local URL shown in the terminal (usually http://localhost:8501).

## Dataset interpretation
The supplied CSV has 1,470 rows and 31 columns. `Attrition` is numeric:
- `0` = retained
- `1` = exited

The supplied file is named for Palo Alto Networks, but the file itself does not contain a verifiable source/provenance field. Therefore, findings in the reports are attributed to the **provided dataset**, not independently verified company HR records.

## KPI definition
Attrition rate = exited employees / all employees in the selected population × 100.

## Notes
- Dashboard comparisons are descriptive, not causal.
- Small groups can produce unstable rates; always consider employee counts alongside percentages.
- Demographic differences should be used for fair workforce analysis, not individual-level employment decisions.
