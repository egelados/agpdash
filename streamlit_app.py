import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='AGP Dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)
# # -----------------------------------------------------------------------------



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Function to load and preprocess the data
def load_data(file_path):
    data = pd.ExcelFile(file_path)
    df = data.parse('Sheet1')
    df['Χρονική σήμανση συσκευής'] = pd.to_datetime(df['Χρονική σήμανση συσκευής'])
    df.rename(columns={
        'Χρονική σήμανση συσκευής': 'Timestamp',
        'Ιστορική γλυκόζη mg/dL': 'Glucose'
    }, inplace=True)
    return df

# Function to compute AGP summary
def compute_agp_summary(data):
    target_range = (70, 180)
    low_range = (54, 69)
    very_low_range = (0, 53)
    high_range = (181, 250)
    very_high_range = (251, float('inf'))

    total_readings = len(data)
    time_in_target = data['Glucose'].between(*target_range).mean() * 100
    time_low = data['Glucose'].between(*low_range).mean() * 100
    time_very_low = data['Glucose'].between(*very_low_range).mean() * 100
    time_high = data['Glucose'].between(*high_range).mean() * 100
    time_very_high = data['Glucose'].between(*very_high_range).mean() * 100
    mean_glucose = data['Glucose'].mean()
    cv_glucose = (data['Glucose'].std() / mean_glucose) * 100

    summary = {
        'Total Readings': total_readings,
        'Time in Target Range (70-180 mg/dL) (%)': time_in_target,
        'Time Below Range (54-69 mg/dL) (%)': time_low,
        'Time Very Low (<54 mg/dL) (%)': time_very_low,
        'Time Above Range (181-250 mg/dL) (%)': time_high,
        'Time Very High (>250 mg/dL) (%)': time_very_high,
        'Mean Glucose (mg/dL)': mean_glucose,
        'Coefficient of Variation (%CV)': cv_glucose
    }

    return summary

# Function to convert percentage to time
def percentage_to_time(percent):
    total_minutes = percent / 100 * 24 * 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    return f"{hours}ω {minutes}λεπτά"

# Function to plot Time in Range Stacked Bar Chart
def plot_time_in_range_stacked(summary):
    # Data preparation
    ranges = ['Very Low (<54 mg/dL)', 'Low (54-69 mg/dL)', 'Target (70-180 mg/dL)', 'High (181-250 mg/dL)', 'Very High (>250 mg/dL)']
    percentages = [
        summary['Time Very Low (<54 mg/dL) (%)'],
        summary['Time Below Range (54-69 mg/dL) (%)'],
        summary['Time in Target Range (70-180 mg/dL) (%)'],
        summary['Time Above Range (181-250 mg/dL) (%)'],
        summary['Time Very High (>250 mg/dL) (%)']
    ]
    times = [
        percentage_to_time(summary['Time Very Low (<54 mg/dL) (%)']),
        percentage_to_time(summary['Time Below Range (54-69 mg/dL) (%)']),
        percentage_to_time(summary['Time in Target Range (70-180 mg/dL) (%)']),
        percentage_to_time(summary['Time Above Range (181-250 mg/dL) (%)']),
        percentage_to_time(summary['Time Very High (>250 mg/dL) (%)'])
    ]
    
    # Colors for the chart
    colors = ['#ff6666', '#ffc000', '#8fd9b6', '#ffcc99', '#ff9999']
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    cumulative = 0
    for i, (range_name, pct, time, color) in enumerate(zip(ranges, percentages, times, colors)):
        bar = ax.barh([0], [pct], left=[cumulative], color=color, edgecolor='black')
        # Add text annotations
        ax.text(
            cumulative + pct / 2, 0, 
            f"{pct:.1f}%\n({time})", 
            ha='center', va='center', fontsize=10, color='white' if i == 2 else 'black'
        )
        cumulative += pct

    # Add gridlines and set limits
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 10))
    ax.set_xticklabels([f"{x}%" for x in range(0, 101, 10)], fontsize=10)
    ax.set_yticks([])
    ax.set_title('ΧΡΟΝΟΣ ΕΝΤΟΣ ΕΥΡΟΥΣ ΣΤΟΧΩΝ', fontsize=16, fontweight='bold')
    ax.set_xlabel('Percentage (%)', fontsize=12)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    # Position the legend
    ax.legend(
        [f"{range_name}" for range_name in ranges], 
        loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=10
    )

    return fig


def plot_time_in_range_stacked_vertical(summary):
    # Data preparation
    ranges = ['Very Low (<54 mg/dL)', 'Low (54-69 mg/dL)', 'Target (70-180 mg/dL)', 'High (181-250 mg/dL)', 'Very High (>250 mg/dL)']
    percentages = [
        summary['Time Very Low (<54 mg/dL) (%)'],
        summary['Time Below Range (54-69 mg/dL) (%)'],
        summary['Time in Target Range (70-180 mg/dL) (%)'],
        summary['Time Above Range (181-250 mg/dL) (%)'],
        summary['Time Very High (>250 mg/dL) (%)']
    ]
    times = [
        percentage_to_time(summary['Time Very Low (<54 mg/dL) (%)']),
        percentage_to_time(summary['Time Below Range (54-69 mg/dL) (%)']),
        percentage_to_time(summary['Time in Target Range (70-180 mg/dL) (%)']),
        percentage_to_time(summary['Time Above Range (181-250 mg/dL) (%)']),
        percentage_to_time(summary['Time Very High (>250 mg/dL) (%)'])
    ]
    
    # Colors for the chart
    colors = ['#ff6666', '#ffc000', '#8fd9b6', '#ffcc99', '#ff9999']
    
    # Plotting
    fig, ax = plt.subplots(figsize=(6, 8))
    cumulative = np.zeros(1)
    for i, (range_name, pct, time, color) in enumerate(zip(ranges, percentages, times, colors)):
        bar = ax.bar([0], [pct], bottom=cumulative, color=color, edgecolor='black', width=0.5, label=f"{range_name}: {pct:.1f}% ({time})")
        # Add text annotations
        ax.text(
            0, cumulative + pct / 2, 
            f"{pct:.1f}%\n({time})", 
            ha='center', va='center', fontsize=10, color='white' if i == 2 else 'black'
        )
        cumulative += pct

    # Set chart details
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 10))
    ax.set_yticklabels([f"{x}%" for x in range(0, 101, 10)], fontsize=10)
    ax.set_xticks([])
    ax.set_title('ΧΡΟΝΟΣ ΕΝΤΟΣ ΕΥΡΟΥΣ ΣΤΟΧΩΝ', fontsize=16, fontweight='bold')
    ax.set_ylabel('Percentage (%)', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    # Position the legend
    ax.legend(
        loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=1, fontsize=10, frameon=False
    )

    return fig


# Streamlit application
st.title("Ambulatory Glucose Profile (AGP) Report")

# File upload
uploaded_file = st.file_uploader("Upload your AGP dataset (Excel format)", type=["xlsx"])
if uploaded_file:
    data = load_data(uploaded_file)
    summary = compute_agp_summary(data)

    # Display summary
    st.header("AGP Summary")
    time_in_target_time = percentage_to_time(summary['Time in Target Range (70-180 mg/dL) (%)'])
    time_low_time = percentage_to_time(summary['Time Below Range (54-69 mg/dL) (%)'])
    time_very_low_time = percentage_to_time(summary['Time Very Low (<54 mg/dL) (%)'])
    time_high_time = percentage_to_time(summary['Time Above Range (181-250 mg/dL) (%)'])
    time_very_high_time = percentage_to_time(summary['Time Very High (>250 mg/dL) (%)'])

    st.write(f"**Mean Glucose:** {summary['Mean Glucose (mg/dL)']:.1f} mg/dL")
    gmi = 3.31 + 0.02392 * summary['Mean Glucose (mg/dL)']
    st.write(f"**Glucose Management Indicator (GMI):** {gmi:.1f}%")
    st.write(f"**Coefficient of Variation (%CV):** {summary['Coefficient of Variation (%CV)']:.1f}%")

    # Show stacked bar chart
    st.header("ΧΡΟΝΟΣ ΕΝΤΟΣ ΕΥΡΟΥΣ ΣΤΟΧΩΝ")
    stacked_chart = plot_time_in_range_stacked_vertical(summary)
    st.pyplot(stacked_chart)




# # -----------------------------------------------------------------------------


def compute_agp(data):
    # Extract time of day
    data['Time of Day'] = data['Timestamp'].dt.hour + data['Timestamp'].dt.minute / 60

    # Group data by time of day
    grouped = data.groupby('Time of Day')['Glucose']

    # Compute percentiles
    agp_stats = grouped.agg(
        Median='median',
        Percentile5=lambda x: np.percentile(x, 5),
        Percentile25=lambda x: np.percentile(x, 25),
        Percentile75=lambda x: np.percentile(x, 75),
        Percentile95=lambda x: np.percentile(x, 95)
    )

    return agp_stats.reset_index()

def plot_agp(agp_data):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot percentiles
    ax.fill_between(
        agp_data['Time of Day'], 
        agp_data['Percentile5'], 
        agp_data['Percentile95'], 
        color='lightblue', 
        alpha=0.5, 
        label='5th-95th Percentile'
    )
    ax.fill_between(
        agp_data['Time of Day'], 
        agp_data['Percentile25'], 
        agp_data['Percentile75'], 
        color='blue', 
        alpha=0.3, 
        label='25th-75th Percentile'
    )
    ax.plot(
        agp_data['Time of Day'], 
        agp_data['Median'], 
        color='darkblue', 
        linewidth=2, 
        label='Median (50th Percentile)'
    )

    # Add target range overlay
    ax.axhspan(70, 180, color='green', alpha=0.1, label='Target Range (70-180 mg/dL)')

    # Customize the chart
    ax.set_title('ΠΡΟΦΙΛ ΔΙΑΚΥΜΑΝΣΗΣ ΓΛΥΚΟΖΗΣ (AGP)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Time of Day (Hours)', fontsize=12)
    ax.set_ylabel('Glucose (mg/dL)', fontsize=12)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xticklabels([f"{int(x):02d}:00" for x in range(0, 25, 3)])
    ax.set_ylim(0, 350)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    return fig

# Streamlit Application
st.title("Ambulatory Glucose Profile (AGP) Report")

if uploaded_file:
    data = load_data(uploaded_file)
    agp_data = compute_agp(data)

    # Display AGP visualization
    st.header("ΠΡΟΦΙΛ ΔΙΑΚΥΜΑΝΣΗΣ ΓΛΥΚΟΖΗΣ (AGP)")
    agp_chart = plot_agp(agp_data)
    st.pyplot(agp_chart)




# # -----------------------------------------------------------------------------
# # Declare some useful functions.

# @st.cache_data
# def get_gdp_data():
#     """Grab GDP data from a CSV file.

#     This uses caching to avoid having to read the file every time. If we were
#     reading from an HTTP endpoint instead of a file, it's a good idea to set
#     a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
#     """

#     # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
#     DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
#     raw_gdp_df = pd.read_csv(DATA_FILENAME)

#     MIN_YEAR = 1960
#     MAX_YEAR = 2022

#     # The data above has columns like:
#     # - Country Name
#     # - Country Code
#     # - [Stuff I don't care about]
#     # - GDP for 1960
#     # - GDP for 1961
#     # - GDP for 1962
#     # - ...
#     # - GDP for 2022
#     #
#     # ...but I want this instead:
#     # - Country Name
#     # - Country Code
#     # - Year
#     # - GDP
#     #
#     # So let's pivot all those year-columns into two: Year and GDP
#     gdp_df = raw_gdp_df.melt(
#         ['Country Code'],
#         [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
#         'Year',
#         'GDP',
#     )

#     # Convert years from string to integers
#     gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

#     return gdp_df

# gdp_df = get_gdp_data()

# # -----------------------------------------------------------------------------
# # Draw the actual page

# # Set the title that appears at the top of the page.
# '''
# # :earth_americas: GDP dashboard

# Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
# notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
# But it's otherwise a great (and did I mention _free_?) source of data.
# '''

# # Add some spacing
# ''
# ''

# min_value = gdp_df['Year'].min()
# max_value = gdp_df['Year'].max()

# from_year, to_year = st.slider(
#     'Which years are you interested in?',
#     min_value=min_value,
#     max_value=max_value,
#     value=[min_value, max_value])

# countries = gdp_df['Country Code'].unique()

# if not len(countries):
#     st.warning("Select at least one country")

# selected_countries = st.multiselect(
#     'Which countries would you like to view?',
#     countries,
#     ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

# ''
# ''
# ''

# # Filter the data
# filtered_gdp_df = gdp_df[
#     (gdp_df['Country Code'].isin(selected_countries))
#     & (gdp_df['Year'] <= to_year)
#     & (from_year <= gdp_df['Year'])
# ]

# st.header('GDP over time', divider='gray')

# ''

# st.line_chart(
#     filtered_gdp_df,
#     x='Year',
#     y='GDP',
#     color='Country Code',
# )

# ''
# ''


# first_year = gdp_df[gdp_df['Year'] == from_year]
# last_year = gdp_df[gdp_df['Year'] == to_year]

# st.header(f'GDP in {to_year}', divider='gray')

# ''

# cols = st.columns(4)

# for i, country in enumerate(selected_countries):
#     col = cols[i % len(cols)]

#     with col:
#         first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
#         last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

#         if math.isnan(first_gdp):
#             growth = 'n/a'
#             delta_color = 'off'
#         else:
#             growth = f'{last_gdp / first_gdp:,.2f}x'
#             delta_color = 'normal'

#         st.metric(
#             label=f'{country} GDP',
#             value=f'{last_gdp:,.0f}B',
#             delta=growth,
#             delta_color=delta_color
#         )
