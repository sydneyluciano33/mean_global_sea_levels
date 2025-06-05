import streamlit as st # pyright: ignore[reportMissingImports]
import altair as alt # pyright: ignore[reportMissingImports]
import pandas as pd  # pyright: ignore[reportMissingImports]

# Load the dataset
dataset = pd.read_csv('sea_levels_with_years.csv')

st.set_page_config(layout="wide")
with st.sidebar:
    st.title("Sea Level Change Analysis")
    st.markdown("Explore sea level changes across different regions and years.")
    measure_options = ['All'] + dataset['Measure'].unique().tolist()
    selection = st.selectbox(
        'Select a sea region to view sea level changes:',
        options = measure_options
)

# Filter the dataset based on the selection
if selection == 'All':
    filtered_dataset = dataset[dataset['Year'] <= 2024]
else:
    filtered_dataset = dataset[(dataset['Year'] <= 2024) & (dataset['Measure'] == selection)]

#  Create a heatmap chart
chart = alt.Chart(filtered_dataset).mark_bar().encode(
    x = alt.X('Year:O', title = 'Year'),
    y = alt.Y('Measure:N', title = 'Geographic Location'),
    color = alt.Color('Value:Q', scale=alt.Scale(scheme='lightgreyred'), title = 'Change in Mean Sea Level')
    #size = alt.Size('Value:Q', bin = alt.Bin(maxbins=10))
    #scale = alt.Scale(domain =(1993,2000))
).properties(
    title = 'Mean Sea Level Change by Year Across All Measured Regions'
).interactive()


# Average per year chart
#average_per_year = filtered_dataset.groupby('Year', as_index=False)['Value'].mean()
average_per_year = dataset[dataset['Year'] <= 2024].groupby('Year', as_index=False)['Value'].mean()
average_per_measure = filtered_dataset.groupby(['Year', 'Measure'], as_index=False)['Value'].mean()
# Bar or point chart for individual measures
points = alt.Chart(average_per_measure).mark_circle(opacity=0.7).encode(
    x=alt.X('Year:O', title='Year'),
    y=alt.Y('Value:Q'),
    color=alt.Color('Measure:N'),
    tooltip=['Year', 'Measure', 'Value']
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

# display heat map and yearly sea level changes side by side
columns = st.columns(2)
with columns[0]:
    st.subheader("Mean Sea Level Change by Year Across All Measured Regions")
    st.altair_chart(chart)

with columns[1]:
    st.subheader("Yearly Sea Level Changes and Annual Average")
    st.altair_chart(final_chart)

# change year to year bar chart

# Average sea level change per year
filtered_dataset = dataset[dataset['Year'] <= 2024]
yearly_avg = filtered_dataset.groupby('Year', as_index=False)['Value'].mean()
yearly_avg['Change'] = yearly_avg['Value'].diff()

# Line chart: average value per year
filtered_dataset = dataset[dataset['Year'] <= 2024]
line = alt.Chart(yearly_avg).mark_line(point=True).encode(
    x=alt.X('Year:O', title='Year'),
    y=alt.Y('Value:Q', title='Average Sea Level Change (mm)'),
    tooltip=['Year', 'Value']
).properties(
    title='Average Sea Level Change by Year',
    width=600,
    height=300
)


# Bar chart: year-to-year change
filtered_dataset = dataset[dataset['Year'] <= 2024]
bars = alt.Chart(yearly_avg).mark_bar(color='orange', opacity=0.6).encode(
    x=alt.X('Year:O'),
    y=alt.Y('Change:Q', title='Year-to-Year Change (mm)'),
    tooltip=['Year', 'Change']
).properties(
    title='Year-to-Year Change in Mean Sea Level',
    width=600,
    height=200
)
st.altair_chart(line & bars)

#Top 10 most volatile sea regions by sea level change
filtered_dataset = dataset[dataset['Year'] <= 2024]
volatility_by_region = filtered_dataset.groupby('Measure', as_index=False)['Value'].std()
volatility_by_region.columns = ['Measure', 'Volatility']

# Step 2: Get top 10 most volatile regions
top_volatile = volatility_by_region.sort_values('Volatility', ascending=False).head(10)

# Step 3: Create Altair bar chart
volatile_chart = alt.Chart(top_volatile).mark_bar().encode(
    x=alt.X('Volatility:Q', title='Standard Deviation (mm)'),
    y=alt.Y('Measure:N', sort='-x', title='Region'),
    color=alt.Color('Measure:N', legend=None),
    tooltip=['Measure', 'Volatility']
).properties(
    title='Top 10 Most Volatile Sea Regions by Sea Level Change',
    width=600,
    height=400
)
st.altair_chart(volatile_chart)


