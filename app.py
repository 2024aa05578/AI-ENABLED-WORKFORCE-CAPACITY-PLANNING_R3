import os
import pandas as pd
import streamlit as st

from forecasting import build_monthly_forecast, summarize_latest_month, validate_inputs, PRODUCT_LINES, REGIONS
from github_backend import GithubRepoBackend

st.set_page_config(page_title="AI Enabled Workforce & Capacity Planning", layout="wide")

DEFAULT_ASSUMPTIONS = {
    "planning_horizon_months": 12,
    "target_utilization_pct": 85,
    "shrinkage_pct": 12,
    "skill_buffer_pct": 10,
    "default_monthly_capacity_per_engineer": 35,
}


def init_state():
    if "engineers_df" not in st.session_state:
        st.session_state["engineers_df"] = pd.DataFrame(
            [
                {
                    "region": r,
                    "product_line": p,
                    "current_engineers": 0,
                    "avg_monthly_capacity_per_engineer": DEFAULT_ASSUMPTIONS["default_monthly_capacity_per_engineer"],
                    "productivity_factor": 1.0,
                }
                for r in REGIONS
                for p in PRODUCT_LINES
            ]
        )

    if "wo_df" not in st.session_state:
        st.session_state["wo_df"] = pd.DataFrame(
            [
                {
                    "region": r,
                    "product_line": p,
                    "baseline_monthly_wo": 0,
                    "bau_annual_growth_pct": 8,
                    "dc_annual_growth_pct": 0,
                }
                for r in REGIONS
                for p in PRODUCT_LINES
            ]
        )

    if "assumptions" not in st.session_state:
        st.session_state["assumptions"] = DEFAULT_ASSUMPTIONS.copy()


def sidebar_backend():
    st.sidebar.header("GitHub Backend")

    owner = st.sidebar.text_input("GitHub Owner", value=os.getenv("GITHUB_OWNER", ""))
    repo = st.sidebar.text_input("GitHub Repo", value=os.getenv("GITHUB_REPO", ""))
    branch = st.sidebar.text_input("GitHub Branch", value=os.getenv("GITHUB_BRANCH", "main"))
    data_path = st.sidebar.text_input("Data Folder in Repo", value=os.getenv("GITHUB_DATA_PATH", "data"))
    token = st.sidebar.text_input("GitHub Token", type="password", value=os.getenv("GITHUB_TOKEN", ""))

    backend = None
    if owner and repo and token:
        backend = GithubRepoBackend(
            owner=owner,
            repo=repo,
            branch=branch,
            token=token,
            data_path=data_path
        )

    col1, col2 = st.sidebar.columns(2)

    if col1.button("Load from GitHub", use_container_width=True, disabled=backend is None):
        try:
            engineers = backend.read_csv("baseline_engineers.csv")
            wo = backend.read_csv("work_orders.csv")
            assumptions = backend.read_json("assumptions.json")

            st.session_state["engineers_df"] = engineers
            st.session_state["wo_df"] = wo
            st.session_state["assumptions"] = assumptions

            st.sidebar.success("Loaded data from GitHub successfully.")
        except Exception as e:
            st.sidebar.error(f"Load failed: {e}")

    if col2.button("Save to GitHub", use_container_width=True, disabled=backend is None):
        try:
            backend.write_csv(st.session_state["engineers_df"], "baseline_engineers.csv", "Update baseline engineers")
            backend.write_csv(st.session_state["wo_df"], "work_orders.csv", "Update work orders")
            backend.write_json(st.session_state["assumptions"], "assumptions.json", "Update assumptions")

            st.sidebar.success("Saved current inputs to GitHub successfully.")
        except Exception as e:
            st.sidebar.error(f"Save failed: {e}")


def data_input_section():
    st.subheader("1) Baseline Inputs")
    st.caption(
        "Provide baseline service engineer count, engineer capacity, work order volume, BAU growth, and additional Data Center growth."
    )

    tab1, tab2, tab3 = st.tabs(["Engineer Baseline", "Work Orders / Growth", "Assumptions"])

    with tab1:
        st.markdown("### Engineer Baseline Input")
        engineers_df = st.data_editor(
            st.session_state["engineers_df"],
            use_container_width=True,
            num_rows="dynamic",
            key="engineers_editor",
            column_config={
                "region": st.column_config.SelectboxColumn("Region", options=REGIONS),
                "product_line": st.column_config.SelectboxColumn("Product Line", options=PRODUCT_LINES),
                "current_engineers": st.column_config.NumberColumn("Current Engineers", min_value=0, step=1),
                "avg_monthly_capacity_per_engineer": st.column_config.NumberColumn(
                    "Avg Monthly Capacity per Engineer", min_value=1, step=1
                ),
                "productivity_factor": st.column_config.NumberColumn(
                    "Productivity Factor", min_value=0.1, max_value=3.0, step=0.05
                ),
            },
        )
        st.session_state["engineers_df"] = engineers_df

    with tab2:
        st.markdown("### Work Orders / Growth Input")
        wo_df = st.data_editor(
            st.session_state["wo_df"],
            use_container_width=True,
            num_rows="dynamic",
            key="wo_editor",
            column_config={
                "region": st.column_config.SelectboxColumn("Region", options=REGIONS),
                "product_line": st.column_config.SelectboxColumn("Product Line", options=PRODUCT_LINES),
                "baseline_monthly_wo": st.column_config.NumberColumn("Baseline Monthly WO", min_value=0, step=1),
                "bau_annual_growth_pct": st.column_config.NumberColumn(
                    "BAU Annual Growth %", min_value=-100.0, max_value=500.0, step=0.5
                ),
                "dc_annual_growth_pct": st.column_config.NumberColumn(
                    "DC Annual Growth %", min_value=-100.0, max_value=500.0, step=0.5
                ),
            },
        )
        st.session_state["wo_df"] = wo_df

    with tab3:
        st.markdown("### Planning Assumptions")
        assumptions = st.session_state["assumptions"]

        c1, c2, c3 = st.columns(3)
        assumptions["planning_horizon_months"] = c1.number_input(
            "Planning Horizon (Months)", min_value=1, max_value=60, value=int(assumptions.get("planning_horizon_months", 12))
        )
        assumptions["target_utilization_pct"] = c2.number_input(
            "Target Utilization %", min_value=10.0, max_value=100.0, value=float(assumptions.get("target_utilization_pct", 85.0)), step=1.0
        )
        assumptions["shrinkage_pct"] = c3.number_input(
            "Shrinkage %", min_value=0.0, max_value=80.0, value=float(assumptions.get("shrinkage_pct", 12.0)), step=0.5
        )

        c4, c5 = st.columns(2)
        assumptions["skill_buffer_pct"] = c4.number_input(
            "Skill / Training Buffer %", min_value=0.0, max_value=80.0, value=float(assumptions.get("skill_buffer_pct", 10.0)), step=0.5
        )
        assumptions["default_monthly_capacity_per_engineer"] = c5.number_input(
            "Default Monthly WO Capacity per Engineer", min_value=1, max_value=1000, value=int(assumptions.get("default_monthly_capacity_per_engineer", 35))
        )

        st.session_state["assumptions"] = assumptions


def results_section():
    st.subheader("2) Forecast Results")

    engineers_df = st.session_state["engineers_df"].copy()
    wo_df = st.session_state["wo_df"].copy()
    assumptions = st.session_state["assumptions"].copy()

    errors = validate_inputs(engineers_df, wo_df)
    if errors:
        for err in errors:
            st.error(err)
        st.stop()

    monthly_forecast = build_monthly_forecast(engineers_df, wo_df, assumptions)
    summary = summarize_latest_month(monthly_forecast)

    total_current = int(summary["current_engineers"].sum())
    total_required = int(summary["required_engineers"].sum())
    total_gap = int(summary["gap_engineers"].sum())

    k1, k2, k3 = st.columns(3)
    k1.metric("Current Engineers", total_current)
    k2.metric("Required Engineers (Latest Month)", total_required)
    k3.metric("Gap / Surplus", total_gap)

    st.markdown("### Latest Month Summary")
    st.dataframe(summary, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Required Engineers by Product Line")
        by_product = summary.groupby("product_line", as_index=False)["required_engineers"].sum().set_index("product_line")
        st.bar_chart(by_product)

    with c2:
        st.markdown("### Required Engineers by Region")
        by_region = summary.groupby("region", as_index=False)["required_engineers"].sum().set_index("region")
        st.bar_chart(by_region)

    st.markdown("### Monthly Forecast Detail")
    st.dataframe(monthly_forecast, use_container_width=True)


def main():
    init_state()

    st.title("AI Enabled Workforce & Capacity Planning")
    st.write(
        "This application forecasts service engineer requirements across product lines and regions. "
        "It combines BAU forecast with additional Data Center business growth."
    )

    sidebar_backend()
    data_input_section()
    results_section()


if __name__ == "__main__":
    main()
