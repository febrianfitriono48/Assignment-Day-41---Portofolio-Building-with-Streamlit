import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(layout="wide")

# =====================================================
# SIDEBAR — BIODATA
# =====================================================
st.sidebar.title("About Me")
st.sidebar.write("**Name:** Febrian Fitriono")
st.sidebar.write("**Role:** Supervisor")
st.sidebar.write("**Age:** 31")
st.sidebar.write("**Scope:** Nickel Mining")

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_csv("production-of-nickel-mine.csv", sep=";")
    df = df.drop(columns=["Sub-commodity"])
    return df

df = load_data()

# =====================================================
# CONTINENT MAPPING
# =====================================================
continent_map = {
    "Indonesia":"Asia","China":"Asia","Philippines":"Asia","Japan":"Asia",
    "Russia":"Europe","Finland":"Europe","Greece":"Europe",
    "Australia":"Oceania","New Caledonia":"Oceania",
    "USA":"North America","Canada":"North America","Cuba":"North America",
    "Brazil":"South America","Colombia":"South America",
    "South Africa":"Africa","Morocco":"Africa","Botswana":"Africa",
}

df["Continent"] = df["Country"].map(continent_map).fillna("Other")

# =====================================================
# SIDEBAR FILTER
# =====================================================
st.sidebar.title("Filters")

countries = st.sidebar.multiselect(
    "Select Country",
    df["Country"].unique(),
    default=df["Country"].unique()
)

year_range = st.sidebar.slider(
    "Select Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (int(df["Year"].min()), int(df["Year"].max()))
)

period = st.sidebar.selectbox(
    "Aggregation Period",
    ["Yearly","5-Year Period"]
)

filtered = df[
    (df["Country"].isin(countries)) &
    (df["Year"].between(year_range[0], year_range[1]))
]

# =====================================================
# AGGREGATION
# =====================================================
if period == "5-Year Period":
    filtered["Period"] = (filtered["Year"]//5)*5
    group_time = filtered.groupby("Period")["Production"].sum().reset_index()
    x_axis = "Period"
else:
    group_time = filtered.groupby("Year")["Production"].sum().reset_index()
    x_axis = "Year"

# =====================================================
# TITLE
# =====================================================
st.title("Nickel Production Intelligence Dashboard")

# =====================================================
# KPI METRICS
# =====================================================
total_prod = int(filtered["Production"].sum())
top_country = filtered.groupby("Country")["Production"].sum().idxmax()
peak_year = filtered.groupby("Year")["Production"].sum().idxmax()

year_start = group_time.iloc[0]["Production"]
year_end = group_time.iloc[-1]["Production"]
years = len(group_time)-1
cagr = ((year_end/year_start)**(1/years)-1)*100 if years>0 else 0

last10 = group_time.tail(10)["Production"]
growth10 = ((last10.iloc[-1]-last10.iloc[0])/last10.iloc[0])*100 if len(last10)>1 else 0

col1,col2,col3,col4,col5 = st.columns(5)
col1.metric("Total Production", f"{total_prod:,.0f}")
col2.metric("Top Producer", top_country)
col3.metric("Peak Year", int(peak_year))
col4.metric("CAGR %", f"{cagr:.2f}%")
col5.metric("10Y Growth %", f"{growth10:.2f}%")

# Download Button
st.download_button(
    "Download Filtered Data",
    filtered.to_csv(index=False),
    file_name="nickel_filtered.csv"
)

# =====================================================
# TREND CHART
# =====================================================
fig1 = px.line(group_time, x=x_axis, y="Production",
               title="Production Trend")
st.plotly_chart(fig1, use_container_width=True)

st.markdown(
f"""
**Insight:**  
Production peaks around **{peak_year}**, driven mainly by **{top_country}**.  
Growth momentum across the selected range reflects structural demand changes
in global nickel markets.
"""
)

# =====================================================
# INDONESIA VS GLOBAL
# =====================================================
indo = filtered[filtered["Country"]=="Indonesia"]\
    .groupby("Year")["Production"].sum().reset_index()

global_trend = filtered.groupby("Year")["Production"].sum().reset_index()

fig_compare = px.line(title="Indonesia vs Global Trend")

fig_compare.add_scatter(
    x=global_trend["Year"],
    y=global_trend["Production"],
    mode="lines",
    name="Global"
)

fig_compare.add_scatter(
    x=indo["Year"],
    y=indo["Production"],
    mode="lines",
    name="Indonesia"
)

st.plotly_chart(fig_compare, use_container_width=True)

# =====================================================
# CONTINENT ANALYSIS
# =====================================================
cont = filtered.groupby("Continent")["Production"].sum().reset_index()

fig2 = px.bar(cont, x="Continent", y="Production",
              title="Production Contribution by Continent")
st.plotly_chart(fig2, use_container_width=True)

fig_pie = px.pie(
    cont,
    names="Continent",
    values="Production",
    title="Share by Continent"
)
st.plotly_chart(fig_pie, use_container_width=True)

top_cont = cont.sort_values("Production", ascending=False).iloc[0]
share = (top_cont["Production"] / cont["Production"].sum()) * 100

st.markdown(
f"""
**Insight:**  
The largest regional contribution comes from **{top_cont['Continent']}**
with **{share:.1f}%** share of total production.
This highlights geographic supply concentration.
"""
)

# =====================================================
# TOP COUNTRIES
# =====================================================
top = filtered.groupby("Country")["Production"].sum()\
        .nlargest(10).reset_index()

fig3 = px.bar(top, x="Country", y="Production",
              title="Top Producing Countries")
st.plotly_chart(fig3, use_container_width=True)

st.markdown(
"""
**Insight:**  
Top producers dominate global supply structure.  
Monitoring these countries is essential for forecasting price shifts,
investment risk, and supply security.
"""
)
