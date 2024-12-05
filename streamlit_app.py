import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set Streamlit page configuration
st.set_page_config(
    page_title='AGP Dashboard',
    page_icon=':bar_chart:',
)

# --------------------------------------------------------------------
# Data Processing Functions
# --------------------------------------------------------------------

# Function to load and preprocess the data
def load_data(file_path):
    df = pd.ExcelFile(file_path).parse('Sheet1')
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

    summary = {
        'Total Readings': len(data),
        'Time in Target Range (70-180 mg/dL) (%)': data['Glucose'].between(*target_range).mean() * 100,
        'Time Below Range (54-69 mg/dL) (%)': data['Glucose'].between(*low_range).mean() * 100,
        'Time Very Low (<54 mg/dL) (%)': data['Glucose'].between(*very_low_range).mean() * 100,
        'Time Above Range (181-250 mg/dL) (%)': data['Glucose'].between(*high_range).mean() * 100,
        'Time Very High (>250 mg/dL) (%)': data['Glucose'].between(*very_high_range).mean() * 100,
        'Mean Glucose (mg/dL)': data['Glucose'].mean(),
        'Coefficient of Variation (%CV)': (data['Glucose'].std() / data['Glucose'].mean()) * 100,
    }

    return summary

# Function to convert percentage to time
def percentage_to_time(percent):
    total_minutes = percent / 100 * 24 * 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    return f"{hours}ω {minutes}λεπτά"

# --------------------------------------------------------------------
# Visualization Functions
# --------------------------------------------------------------------

# Function to plot vertical stacked bar chart
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
    times = [percentage_to_time(p) for p in percentages]
    colors = ['#ff6666', '#ffc000', '#8fd9b6', '#ffcc99', '#ff9999']

    # Plotting
    fig, ax = plt.subplots(figsize=(6, 8))
    cumulative = np.zeros(1)
    for range_name, pct, time, color in zip(ranges, percentages, times, colors):
        bar = ax.bar([0], [pct], bottom=cumulative, color=color, edgecolor='black', width=0.5)
        ax.text(0, cumulative + pct / 2, f"{pct:.1f}%\n({time})", ha='center', va='center', fontsize=10, color='black')
        cumulative += pct

    # Chart details
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 10))
    ax.set_yticklabels([f"{x}%" for x in range(0, 101, 10)], fontsize=10)
    ax.set_xticks([])
    ax.set_title('ΧΡΟΝΟΣ ΕΝΤΟΣ ΕΥΡΟΥΣ ΣΤΟΧΩΝ', fontsize=16, fontweight='bold')
    ax.set_ylabel('Percentage (%)', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.legend(ranges, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=1, fontsize=10, frameon=False)

    return fig

# --------------------------------------------------------------------
# Streamlit App
# --------------------------------------------------------------------

st.title("Ambulatory Glucose Profile (AGP) Report")

# File Upload
uploaded_file = st.file_uploader("Upload your AGP dataset (Excel format)", type=["xlsx"])

if uploaded_file:
    data = load_data(uploaded_file)
    summary = compute_agp_summary(data)

    # Display Summary
    st.header("AGP Summary")
    st.write(f"**Mean Glucose:** {summary['Mean Glucose (mg/dL)']:.1f} mg/dL")
    gmi = 3.31 + 0.02392 * summary['Mean Glucose (mg/dL)']
    st.write(f"**Glucose Management Indicator (GMI):** {gmi:.1f}%")
    st.write(f"**Coefficient of Variation (%CV):** {summary['Coefficient of Variation (%CV)']:.1f}%")

    # Show Vertical Stacked Bar Chart
    st.header("ΧΡΟΝΟΣ ΕΝΤΟΣ ΕΥΡΟΥΣ ΣΤΟΧΩΝ")
    stacked_chart = plot_time_in_range_stacked_vertical(summary)
    st.pyplot(stacked_chart)


##########################################################


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

