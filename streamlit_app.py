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
