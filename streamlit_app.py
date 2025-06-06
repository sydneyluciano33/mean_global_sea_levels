
import streamlit as st
import altair as alt
import pandas as pd
# pyright: ignore[reportMissingImports]
# Load data
data = pd.read_csv("sea_levels_with_years.csv")


# Sidebar
st.sidebar.header("Choose a Region To View")
#source = ["All"] + sorted(data["Indicator"].unique())
region = ["All"] + sorted(data["Measure"].unique())

st.sidebar.subheader("The first two charts are connected to the region selected and will display corresponding data.")
#selected_source = st.sidebar.selectbox("Data Source", source)
selected_region = st.sidebar.selectbox("Region", region)

# Apply filters for interactive views
data2 = data[data['Year'] <= 2024]

filtered = data2.copy()

#if selected_source != "All":
  #  filtered = filtered[filtered["Indicator"] == selected_source]
if selected_region != "All":
    filtered = filtered[filtered["Measure"] == selected_region]

st.header("All charts include tooltips that allow you to hover over data points for more information.")
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


# Always use the full dataset for volatility calculation
volatility_by_region = data2.groupby('Measure', as_index=False)['Value'].std()
volatility_by_region.columns = ['Measure', 'Volatility']

top_volatile = volatility_by_region.sort_values('Volatility', ascending=False).head(10)
# Step 3: Create Altair bar chart
min_height = 400
min_width = 600
chart_width = min_width  # pixels
bar_height = 40  # pixels per bar
num_bars = max(len(top_volatile), 1)
chart_height = max(bar_height * num_bars, min_height)

data2.loc[:, 'Measure'] = data2['Measure'].str.strip()
top_volatile.loc[:, 'Measure'] = top_volatile['Measure'].str.strip()

color_scale = alt.Scale(scheme='category10')  # color scheme for volatile and final charts
region_select = alt.selection_point(fields=['Measure'], empty='all')

volatile_chart = alt.Chart(top_volatile).mark_bar().encode(
    x=alt.X('Volatility:Q', title='Standard Deviation (mm)'),
    y=alt.Y('Measure:N', sort='-x', title='Region'),
    color=alt.Color('Measure:N', scale=color_scale, title='Region'),
    opacity=alt.condition(region_select, alt.value(1), alt.value(0)),
    tooltip=['Measure', 'Volatility']
).add_params(
    region_select 
).properties(
    title='Top 10 Most Volatile Sea Regions by Sea Level Change',
    width=chart_width,
    height=chart_height
)

#st.altair_chart(volatile_chart)

# Average per year chart
#average_per_year = filtered_dataset.groupby('Year', as_index=False)['Value'].mean()
average_per_year = data[data['Year'] <= 2024].groupby('Year', as_index=False)['Value'].mean()
top_10_measures = top_volatile['Measure'].tolist()
average_per_measure = data2.groupby(['Year', 'Measure'], as_index=False)['Value'].mean()
average_per_measure_top10 = average_per_measure[average_per_measure['Measure'].isin(top_10_measures)]


#average_per_measure.loc[:, 'Measure'] = average_per_measure['Measure'].str.strip()

#average_per_measure = filtered.groupby(['Year', 'Measure'], as_index=False)['Value'].mean()
# Bar or point chart for individual measures
points = alt.Chart(average_per_measure_top10).mark_circle(opacity=0.7).encode(
    x=alt.X('Year:O', title='Year'),
    y=alt.Y('Value:Q'),
     color=alt.Color('Measure:N', scale=color_scale, title='Region'),
    tooltip=['Year', 'Measure', 'Value']
).transform_filter(
    region_select
)

# Average line
average_line = alt.Chart(average_per_year).mark_line(
    color='black',
    strokeWidth=3
).encode(
    x=alt.X('Year:O', title='Year'),
    y=alt.Y('Value:Q', title='Average Sea Level Change (mm)'),
    tooltip=['Year', 'Value']
)

# Combine
final_chart = (points + average_line).properties(
    title='Yearly Sea Level Changes and Annual Average'
).interactive()
#st.altair_chart(final_chart, use_container_width=True)


st.subheader("Pick a region from the top 10 most volatile sea regions. Then, scroll down and examine how their volatility compares to the yearly average of all sea regions each year.")
st.altair_chart(volatile_chart & final_chart, use_container_width=True)