# dashboard.py: Streamlit app to visualize urban inequality metrics in Mexico using WRI's dataset

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Streamlit page setup
st.set_page_config(page_title="Urban Inequality in Mexico", layout="wide")
st.title("🏙️ Urban Inequality Dashboard - Mexico")
st.markdown("""
This dashboard presents a visualization of selected urban inequality indicators 
from the [World Resources Institute](https://datasets.wri.org/) dataset.
""")

# Step 1: Retrieve metadata to access dataset resources
api_url = "https://datasets.wri.org/api/3/action/package_show"
dataset_id = "index-urban-inequality-mexico"
response = requests.get(api_url, params={"id": dataset_id})
resources = response.json()["result"]["resources"]

# Step 2: Find first CSV resource and load it
csv_url = next((r["url"] for r in resources if r["format"].lower() == "csv"), None)

if csv_url:
    try:
        df = pd.read_csv(csv_url)
        st.success("Dataset loaded successfully.")

        # Show preview
        st.subheader("📊 Data Preview")
        st.dataframe(df.head())

        # Select variables for plotting
        st.subheader("📈 Interactive Plot")
        x_col = st.selectbox("Select X-axis variable", df.columns, index=0)
        y_col = st.selectbox("Select Y-axis variable", df.columns, index=1)
        color_col = st.selectbox("Select color grouping", df.columns, index=2)

        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            hover_name=color_col,
            title=f"{y_col} vs {x_col} grouped by {color_col}",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading dataset: {e}")
else:
    st.warning("No CSV file found in the WRI dataset resource list.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io/) and WRI Open Data.")
