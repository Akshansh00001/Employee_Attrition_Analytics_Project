"""Reusable validation and KPI calculations for the Employee Attrition project."""
from pathlib import Path
import pandas as pd

REQUIRED = ["Age","Attrition","BusinessTravel","Department","Gender","JobRole","MaritalStatus",
            "OverTime","TotalWorkingYears","YearsAtCompany","YearsSinceLastPromotion"]

def load_and_validate(csv_path):
    df = pd.read_csv(csv_path)
    missing_columns = sorted(set(REQUIRED)-set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    if df["Attrition"].isna().any() or not set(df["Attrition"].dropna().unique()).issubset({0,1}):
        raise ValueError("Attrition must contain only 0 (retained) and 1 (exited), with no missing values.")
    return df

def attrition_table(df, column):
    out = df.groupby(column, dropna=False)["Attrition"].agg(Employees="size", Exits="sum").reset_index()
    out["AttritionRatePct"] = out["Exits"] / out["Employees"] * 100
    return out.sort_values("AttritionRatePct", ascending=False)

def overall_kpis(df):
    total = len(df)
    exits = int(df["Attrition"].sum())
    return {"employees": total, "exits": exits, "retained": total-exits,
            "attrition_rate_pct": (exits/total*100 if total else 0)}
