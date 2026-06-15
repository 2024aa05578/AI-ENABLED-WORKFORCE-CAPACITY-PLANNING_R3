import math
import pandas as pd

PRODUCT_LINES = [
    "UPS",
    "Cooling",
    "Power Products",
    "Power System",
    "Industrial Automation"
]

REGIONS = [
    "North",
    "South",
    "East",
    "West"
]


def validate_inputs(engineers_df: pd.DataFrame, wo_df: pd.DataFrame):
    errors = []

    required_eng_cols = {
        "region",
        "product_line",
        "current_engineers",
        "avg_monthly_capacity_per_engineer",
        "productivity_factor"
    }

    required_wo_cols = {
        "region",
        "product_line",
        "baseline_monthly_wo",
        "bau_annual_growth_pct",
        "dc_annual_growth_pct"
    }

    if not required_eng_cols.issubset(engineers_df.columns):
        missing = sorted(required_eng_cols - set(engineers_df.columns))
        errors.append(f"Engineer baseline file missing columns: {missing}")

    if not required_wo_cols.issubset(wo_df.columns):
        missing = sorted(required_wo_cols - set(wo_df.columns))
        errors.append(f"Work order file missing columns: {missing}")

    duplicate_eng = engineers_df.duplicated(subset=["region", "product_line"]).sum()
    duplicate_wo = wo_df.duplicated(subset=["region", "product_line"]).sum()

    if duplicate_eng > 0:
        errors.append("Engineer baseline contains duplicate rows for region + product_line.")

    if duplicate_wo > 0:
        errors.append("Work order baseline contains duplicate rows for region + product_line.")

    return errors


def build_monthly_forecast(engineers_df: pd.DataFrame, wo_df: pd.DataFrame, assumptions: dict) -> pd.DataFrame:
    merged = pd.merge(engineers_df, wo_df, on=["region", "product_line"], how="outer").fillna(0)

    target_util = assumptions.get("target_utilization_pct", 85) / 100.0
    shrinkage = assumptions.get("shrinkage_pct", 12) / 100.0
    skill_buffer = assumptions.get("skill_buffer_pct", 10) / 100.0
    horizon = int(assumptions.get("planning_horizon_months", 12))

    rows = []

    for _, row in merged.iterrows():
        base_wo = float(row["baseline_monthly_wo"])
        current_engineers = int(round(float(row["current_engineers"])))
        avg_capacity = max(float(row["avg_monthly_capacity_per_engineer"]), 1.0)
        productivity_factor = max(float(row.get("productivity_factor", 1.0)), 0.1)

        bau_monthly_growth = float(row["bau_annual_growth_pct"]) / 100.0 / 12.0
        dc_monthly_growth = float(row["dc_annual_growth_pct"]) / 100.0 / 12.0

        effective_capacity = avg_capacity * productivity_factor * target_util * (1 - shrinkage)
        effective_capacity = max(effective_capacity, 0.01)

        for month in range(1, horizon + 1):
            projected_wo = (
                base_wo
                * ((1 + bau_monthly_growth) ** month)
                * ((1 + dc_monthly_growth) ** month)
            )

            required_engineers = math.ceil((projected_wo / effective_capacity) * (1 + skill_buffer))
            gap_engineers = required_engineers - current_engineers

            rows.append(
                {
                    "month_index": month,
                    "region": row["region"],
                    "product_line": row["product_line"],
                    "current_engineers": current_engineers,
                    "baseline_monthly_wo": round(base_wo, 2),
                    "projected_wo": round(projected_wo, 2),
                    "effective_capacity_per_engineer": round(effective_capacity, 2),
                    "required_engineers": required_engineers,
                    "gap_engineers": gap_engineers,
                    "bau_annual_growth_pct": row["bau_annual_growth_pct"],
                    "dc_annual_growth_pct": row["dc_annual_growth_pct"],
                }
            )

    forecast_df = pd.DataFrame(rows).sort_values(
        by=["month_index", "region", "product_line"]
    ).reset_index(drop=True)

    return forecast_df


def summarize_latest_month(monthly_forecast: pd.DataFrame) -> pd.DataFrame:
    latest_month = int(monthly_forecast["month_index"].max())

    cols = [
        "region",
        "product_line",
        "current_engineers",
        "baseline_monthly_wo",
        "projected_wo",
        "effective_capacity_per_engineer",
        "required_engineers",
        "gap_engineers",
        "bau_annual_growth_pct",
        "dc_annual_growth_pct",
    ]

    summary = monthly_forecast.loc[
        monthly_forecast["month_index"] == latest_month,
        cols
    ].sort_values(by=["region", "product_line"]).reset_index(drop=True)

    return summary
``
