import streamlit as st
import altair as alt
import pandas as pd

# Load data
data = pd.read_excel("sea_levels_with_years (1).xlsx")
mapping = {
    "Change in mean sea level: Sea level: TOPEX.Poseidon" : "Poseidon",
    "Change in mean sea level: Sea level: Jason.1" : "Jason.1",
    "Change in mean sea level: Sea level: Jason.2" : "Jason.2",
    "Change in mean sea level: Sea level: Jason.3" : "Jason:3",
    "Change in mean sea level: Sea level: Sentinel-6MF" : "Sentinel-6MF",
    "Change in mean sea level: Sea level: Trend" : "Trend"
}
data["Indicator"] = data["Indicator"].replace(mapping)

# Sidebar
st.sidebar.header("Filter Source")
source = ["All"] + sorted(data["Indicator"].unique())
region = ["All"] + sorted(data["Measure"].unique())

selected_source = st.sidebar.selectbox("Data Source", source)
selected_region = st.sidebar.selectbox("Region", region)

# Apply filters for interactive views
data2 = data[data['Year'] <= 2024]

filtered = data2.copy()

if selected_source != "All":
    filtered = filtered[filtered["Indicator"] == selected_source]
if selected_region != "All":
    filtered = filtered[filtered["Measure"] == selected_region]


box = alt.Chart(filtered).mark_bar().encode(
    x=alt.X("Year:O"),
    y=alt.Y("Measure:N", title="Region"),
    color=alt.Color("Value:Q", scale=alt.Scale(scheme="lightgreyred"), title="Change in Mean Sea Level")
).properties(
    title="Mean Sea Level Change by Year Across All Measured Regions"
).interactive()

st.altair_chart(box, use_container_width=True)


overall = alt.Chart(filtered).mark_line().encode(
    x=alt.X("Date:T"),
    y=alt.Y("Value:Q"),
    tooltip=["Year", "Value"]
).properties(
    title="Sea Level Changes Over Time"
).interactive()

st.altair_chart(overall, use_container_width=True)

year_average = filtered.groupby("Year", as_index=False)["Value"].mean()
year_average["Change"] = year_average["Value"].diff()

average = alt.Chart(year_average).mark_line(point=True).encode(
    x=alt.X("Year:O"),
    y=alt.Y("Value:Q", title="Average Sea Level Change (mm)"),
    tooltip=["Year", "Value"]
).properties(
    title="Average Sea Level Change by Year",
)

st.altair_chart(average, use_container_width=True)

volatility_by_region = data.groupby("Measure", as_index=False)["Value"].std()
volatility_by_region.columns = ["Measure", "Volatility"]

top_volatile = volatility_by_region.sort_values("Volatility", ascending=False).head(10)

volatility = alt.Chart(top_volatile).mark_bar().encode(
    x=alt.X("Volatility:Q", title="Standard Deviation (mm)"),
    y=alt.Y("Measure:N", sort='-x', title="Region"),
    color=alt.Color("Measure:N", legend=None),
    tooltip=["Measure", "Volatility"]
).properties(
    title="Top 10 Most Volatile Sea Regions by Sea Level Change"
)

st.altair_chart(volatility, use_container_width=True)
