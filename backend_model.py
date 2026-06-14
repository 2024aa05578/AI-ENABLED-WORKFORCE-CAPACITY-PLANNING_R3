import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# CONSTANTS
HOURS_PER_DAY = 7
DAYS_PER_MONTH = 20
MONTHS = 12
ANNUAL_HOURS_PER_SR = HOURS_PER_DAY * DAYS_PER_MONTH * MONTHS  # 1680

ATTRITION_RATE = 0.08

# ========== LOAD DATA ==========
def load_data(file_path):
    xls = pd.ExcelFile(file_path)

    df_main = xls.parse("Work File")
    df_projects = xls.parse("C&SP Projects")

    return df_main, df_projects


# ========== BAU FORECAST ==========
def forecast_bau(series):
    """
    Simple ML model (linear regression)
    """
    years = np.array([0, 1, 2]).reshape(-1, 1)  
    values = np.array(series).reshape(-1, 1)

    model = LinearRegression()
    model.fit(years, values)

    forecast_2026 = model.predict([[3]])[0][0]

    return max(forecast_2026, 0)


# ========== PROJECT LOAD ==========
def calculate_project_sr(df_projects):
    """
    Convert project workload into SR requirement
    """
    total_assets = df_projects["Total Assest projected "].sum()
    
    # assume 1 asset needs X hours (configurable)
    HOURS_PER_ASSET = 10  

    total_hours = total_assets * HOURS_PER_ASSET
    sr_required = total_hours / ANNUAL_HOURS_PER_SR

    return sr_required


# ========== SR CALCULATION ==========
def calculate_sr_required(total_hours):
    return total_hours / ANNUAL_HOURS_PER_SR


# ========== ATTRITION ==========
def apply_attrition(sr_available):
    return sr_available * (1 - ATTRITION_RATE)


# ========== MAIN MODEL ==========
def workforce_planning(df_main, df_projects):

    results = []

    product_lines = ["SP UPS", "SP Cooling", "Power Products", "Power System", "Industiral Automation"]

    for product in product_lines:
        try:
            # Mock extraction (can refine based on actual column mapping)
            hours_2023 = np.random.randint(10000, 50000)
            hours_2024 = np.random.randint(10000, 50000)
            hours_2025 = np.random.randint(10000, 50000)

            forecast_hours = forecast_bau([hours_2023, hours_2024, hours_2025])

            bau_sr = calculate_sr_required(forecast_hours)

            project_sr = calculate_project_sr(df_projects)

            total_sr_required = bau_sr + project_sr

            available_sr = np.random.randint(20, 100)
            available_after_attrition = apply_attrition(available_sr)

            sr_to_hire = total_sr_required - available_after_attrition

            results.append({
                "Product": product,
                "BAU_SR": round(bau_sr, 2),
                "Project_SR": round(project_sr, 2),
                "Total_SR": round(total_sr_required, 2),
                "Available_SR": available_after_attrition,
                "To_Hire": round(sr_to_hire, 2)
            })

        except:
            continue

    return pd.DataFrame(results)
