import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# CONSTANTS
HOURS_PER_DAY = 7
DAYS_PER_MONTH = 20
MONTHS = 12
ANNUAL_HOURS_PER_SR = HOURS_PER_DAY * DAYS_PER_MONTH * MONTHS

ATTRITION_RATE = 0.08


# ========== LOAD DATA ==========
def load_data(file):
    xls = pd.ExcelFile(file)

    df_main = xls.parse("Work File")
    df_projects = xls.parse("C&SP Projects")

    return df_main, df_projects


# ========== FORECAST ==========
def forecast_bau(values):
    X = np.array([0, 1, 2]).reshape(-1, 1)
    y = np.array(values).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, y)

    return model.predict([[3]])[0][0]


# ========== PROJECT LOAD REGION-WISE ==========
def get_project_load_by_region(df_projects):

    # If region column exists, use it
    if "Region" in df_projects.columns:
        grouped = df_projects.groupby(["Projects", "Region"])["Total Assest projected "].sum()
    else:
        # fallback: assume all in West (your file mostly West heavy)
        df_projects["Region"] = "West"
        grouped = df_projects.groupby(["Projects", "Region"])["Total Assest projected "].sum()

    return grouped.reset_index()


# ========== MAIN MODEL ==========
def workforce_planning(df_main, df_projects):

