# Dashboard.py: Streamlit app to visualize urban inequality metrics in Mexico using WRI's dataset

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

# Sidebar description
st.sidebar.header("🔎 Filter Data")
st.sidebar.markdown("Use these filters to explore urban inequality dimensions across Mexico.")

# Step 1: Retrieve metadata to access dataset resources
api_url = "https://datasets.wri.org/api/3/action/package_show"
dataset_id = "index-urban-inequality-mexico"
response = requests.get(api_url, params={"id": dataset_id})
resources = response.json()["result"]["resources"]

# Step 2: Find and load CSV data
csv_url = next((r["url"] for r in resources if r["format"].lower() == "csv"), None)

if csv_url:
    try:
        df = pd.read_csv(csv_url)

        # Step 3: Basic cleaning
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
        df.dropna(how="all", inplace=True)

        # Check for equity-related columns
        possible_income = [col for col in df.columns if "income" in col]
        possible_gender = [col for col in df.columns if "gender" in col]
        possible_neigh = [col for col in df.columns if "neigh" in col or "municipality" in col]
        possible_time = [col for col in df.columns if "year" in col or "month" in col or "date" in col]

        # Sidebar filters
        if possible_income:
            income_col = possible_income[0]
            income_options = df[income_col].dropna().unique().tolist()
            selected_income = st.sidebar.multiselect("Filter by Income Group", income_options, default=income_options)
            df = df[df[income_col].isin(selected_income)]

        if possible_gender:
            gender_col = possible_gender[0]
            gender_options = df[gender_col].dropna().unique().tolist()
            selected_gender = st.sidebar.multiselect("Filter by Gender", gender_options, default=gender_options)
            df = df[df[gender_col].isin(selected_gender)]

        if possible_neigh:
            neigh_col = possible_neigh[0]
            neigh_options = df[neigh_col].dropna().unique().tolist()
            selected_neigh = st.sidebar.multiselect("Filter by Neighborhood/Municipality", neigh_options, default=neigh_options)
            df = df[df[neigh_col].isin(selected_neigh)]

        if possible_time:
            time_col = possible_time[0]
            if df[time_col].dtype == "object":
                df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
            df = df.dropna(subset=[time_col])
            min_date = df[time_col].min()
            max_date = df[time_col].max()
            selected_range = st.sidebar.slider("Select Time Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))
            df = df[(df[time_col] >= selected_range[0]) & (df[time_col] <= selected_range[1])]

        # Equity principles text block
        st.markdown("""
        > ⚖️ *This dashboard uses income-quartile, gender, and municipality filters in line with WRI’s equity-by-design approach 
        to show which communities bear the greatest burden of urban inequality.*  
        """)

        # Interactive scatter plot
        st.subheader("📈 Explore Inequality Metrics")
        x_axis = st.selectbox("X-axis variable", df.select_dtypes(include=['float64', 'int64']).columns)
        y_axis = st.selectbox("Y-axis variable", df.select_dtypes(include=['float64', 'int64']).columns, index=1)
        color_by = st.selectbox("Color by", [income_col if possible_income else "none", gender_col if possible_gender else "none", neigh_col if possible_neigh else "none"])

        fig = px.scatter(
            df,
            x=x_axis,
            y=y_axis,
            color=df[color_by] if color_by != "none" else None,
            hover_data=df.columns,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Optional: Geographic map
        lat_cols = [col for col in df.columns if "lat" in col.lower()]
        lon_cols = [col for col in df.columns if "lon" in col.lower() or "lng" in col.lower()]
        if lat_cols and lon_cols:
            st.subheader("🗺️ Geographic Visualization")
            st.map(df[[lat_cols[0], lon_cols[0]]].rename(columns={lat_cols[0]: "lat", lon_cols[0]: "lon"}))

        # Data preview
        st.subheader("🔍 Filtered Data")
        st.dataframe(df.head(20))

    except Exception as e:
        st.error(f"Error processing dataset: {e}")

else:
    st.warning("No CSV file found in the WRI dataset resource list.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io/) and WRI Open Data.")
