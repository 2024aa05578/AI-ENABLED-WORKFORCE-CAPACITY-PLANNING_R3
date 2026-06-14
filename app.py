import streamlit as st
import pandas as pd
from backend_model import load_data, workforce_planning

st.set_page_config(page_title="AI Workforce Planning", layout="wide")

st.title("🚀 AI Enabled Workforce & Capacity Planning")

# Upload file (or GitHub load)
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df_main, df_projects = load_data(uploaded_file)

    st.success("✅ Data Loaded Successfully")

    if st.button("Run Forecast Model"):
        df_results = workforce_planning(df_main, df_projects)

        st.subheader("📊 Workforce Requirement Summary")
        st.dataframe(df_results)

        # Charts
        st.subheader("📈 Hiring Requirement by Product")
        st.bar_chart(df_results.set_index("Product")["To_Hire"])

        st.subheader("📉 SR Demand vs Supply")
        chart_df = df_results.set_index("Product")[["Total_SR", "Available_SR"]]
        st.line_chart(chart_df)
