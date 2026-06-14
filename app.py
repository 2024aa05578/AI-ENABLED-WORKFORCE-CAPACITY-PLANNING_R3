import streamlit as st
from backend_model import load_data, workforce_planning

st.set_page_config(layout="wide")

st.title("🚀 AI Enabled Workforce & Capacity Planning")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    df_main, df_projects = load_data(uploaded_file)

    st.success("✅ Data Loaded")

    if st.button("Run AI Model"):

        df = workforce_planning(df_main, df_projects)

        st.subheader("📊 Region + Product Workforce Plan")
        st.dataframe(df)

        st.subheader("📈 Pivot View: Hiring Need")
        pivot = df.pivot_table(
            values="To_Hire",
            index="Product",
            columns="Region",
            aggfunc="sum"
        )
        st.dataframe(pivot)

        st.subheader("📊 Hiring Demand by Product")
        st.bar_chart(df.groupby("Product")["To_Hire"].sum())
        st.subheader("🌍 Hiring Demand by Region")
        st.bar_chart(df.groupby("Region")["To_Hire"].sum())
``
