from dotenv import load_dotenv
load_dotenv()          # Load variables from .env file
import streamlit as st
from fredapi import Fred
import pandas as pd
import plotly.express as px
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

# ================== CONFIG ==================
st.set_page_config(page_title="Kosicodie Macro Dashboard", layout="wide")
st.title("📈 Kosicodie Macro Dashboard")
st.subheader("US Macro Economic Trends • Built by a 19yo Econ Freshman")

import os
API_KEY = os.getenv("FRED_API_KEY")
if not API_KEY:
    st.error("FRED_API_KEY not found in .env file")
    st.stop()
fred = Fred(api_key=API_KEY)

# ================== DATA PULL ==================
@st.cache_data
def load_data():
    series = {
        'GDP': 'GDP',
        'Unemployment': 'UNRATE',
        'Inflation (CPI)': 'CPIAUCSL',
        'Fed Funds Rate': 'FEDFUNDS',
        '10Y Treasury': 'DGS10',
        'Personal Consumption Expenditures': 'PCE',
        'Real GDP': 'GDPC1'
    }
    
    df_dict = {}
    for name, sid in series.items():
        print(f"Loading {name}: {sid}")
        try:
            data = fred.get_series(sid, observation_start='2010-01-01')
            df_dict[name] = data
        except Exception as e:
            print(f"Failed to load {name} ({sid}): {e}")
            continue
    
    df = pd.DataFrame(df_dict)
    print(f"Dataframe shape: {df.shape}")
    print(f"Dataframe index type: {type(df.index)}")
    print("Non-null counts by column:")
    print(df.count())
    
    return df

df = load_data()

# ================== SIDEBAR ==================
available_indicators = [col for col in df.columns if col not in ["Yield Spread", "Real GDP"]] # Exclude derived/redundant indicators from main selection
selected_indicators = st.sidebar.multiselect(
    "Select Indicators",
    options=available_indicators,
    default=available_indicators
)

# ================== DASHBOARD ==================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Latest GDP", f"${df['GDP'].dropna().iloc[-1]:,.0f}B")

with col2:
    st.metric("Unemployment Rate", f"{df['Unemployment'].dropna().iloc[-1]:.1f}%")

with col3:
    cpi = df["Inflation (CPI)"].dropna()
    inflation_series = cpi.pct_change(12)
    if inflation_series.empty or inflation_series.dropna().empty:
        st.metric("Inflation Rate (YoY)", "N/A")
    else:
        latest_inflation = inflation_series.dropna().iloc[-1] * 100
        st.metric("Inflation Rate (YoY)", f"{latest_inflation:.1f}%")

st.subheader("Economic Trends Over Time")
st.subheader("Time Series Plots")

for column in selected_indicators:
    if column in df.columns: # Ensure the column exists in the DataFrame
        series_data = df[column].dropna() # Use only non-null observations for the specific series
        fig = px.line(
            x=series_data.index,
            y=series_data.values,
            title=column,
            template="plotly_dark"
        )
        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

# Yield spread calculation (always displayed, not part of multiselect)
if "10Y Treasury" in df.columns and "Fed Funds Rate" in df.columns:
    df["Yield Spread"] = df["10Y Treasury"] - df["Fed Funds Rate"]
    
    # Only display Yield Spread chart if the necessary columns were loaded
    # and if it's not explicitly excluded from display logic.
    # For now, it's always displayed as per original request to not change other functionality.

fig = px.line(
    df,
    x=df.index,
    y="Yield Spread",
    title="Yield Spread & Recession Signals",
    template="plotly_dark"
)

fig.update_layout(
    template="plotly_dark",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

latest_spread = df["Yield Spread"].dropna().iloc[-1]

st.subheader("Recession Risk Indicator")
if latest_spread < 0:
    st.error(f"🔴 High Recession Risk: Yield Curve Inverted ({latest_spread:.2f}%)")
elif 0 <= latest_spread < 0.5:
    st.warning(f"🟠 Moderate Recession Risk: Narrow Yield Spread ({latest_spread:.2f}%)")
else:
    st.success(f"🟢 Low Recession Risk: Normal Yield Spread ({latest_spread:.2f}%)")

def calculate_recession_probability(yield_spread):
    # This is a placeholder model. A more robust model would be trained on historical data.
    # For now, it provides a probability based on the given formula which correlates with inversion.
    probability = 1 / (1 + np.exp(-1 * (yield_spread * 10 - 1))) # Adjusted for more intuitive output with typical spreads
    return probability

recession_probability = calculate_recession_probability(latest_spread)
st.metric("Recession Probability", f"{recession_probability:.2%}")

st.subheader("Economic Health Score")

# --- Get latest indicator values for score calculation ---
# Ensure values are available before proceeding.
unemployment_rate = df['Unemployment'].dropna().iloc[-1] if not df['Unemployment'].dropna().empty else np.nan

cpi_data_for_inflation = df["Inflation (CPI)"].dropna()
inflation_yoy_calc_series = cpi_data_for_inflation.pct_change(12)
latest_inflation_rate = inflation_yoy_calc_series.dropna().iloc[-1] * 100 if not inflation_yoy_calc_series.dropna().empty else np.nan

# latest_spread is already calculated and available from the Recession Risk Indicator section.

# Check if any required value is NaN, if so, display a warning and skip score calculation
if np.isnan(unemployment_rate) or np.isnan(latest_inflation_rate) or np.isnan(latest_spread):
    st.warning("Could not calculate Economic Health Score due to missing data for key indicators (Unemployment, Inflation, Yield Spread).")
else:
    # ================== Score Calculation Methodology ==================
    # Each component contributes to a total score out of 100.
    # The calculations are transparent and aim to give a higher score for healthier economic conditions.

    # 1. Unemployment Rate Component (Max 35 points)
    # Target: 3.5% unemployment rate. Penalize for each % point above target.
    # Formula: max(0, 35 - (actual_rate - 3.5) * 10)
    # Example: 3.5% -> 35 pts, 4.5% -> 25 pts, 5.5% -> 15 pts, 6.5% -> 5 pts
    unemployment_score = max(0, 35 - (unemployment_rate - 3.5) * 10)
    st.markdown(f"**Unemployment Rate:** {unemployment_rate:.1f}% ({unemployment_score:.0f} points)")

    # 2. Inflation Rate Component (Max 35 points)
    # Target: 2.0% YoY inflation. Penalize for deviations from target.
    # Formula: max(0, 35 - abs(actual_rate - 2.0) * 15)
    # Example: 2.0% -> 35 pts, 3.0% (or 1.0%) -> 20 pts, 4.0% (or 0.0%) -> 5 pts
    inflation_score = max(0, 35 - abs(latest_inflation_rate - 2.0) * 15)
    st.markdown(f"**Inflation Rate (YoY):** {latest_inflation_rate:.1f}% ({inflation_score:.0f} points)")

    # 3. Yield Spread Component (Max 30 points)
    # Positive yield spread indicates healthier conditions. Inverted (negative) spread is worse.
    # Formula: max(0, min(30, (actual_spread + 1.0) * 10))
    # Example: -1.0% -> 0 pts, 0.0% -> 10 pts, 1.0% -> 20 pts, 2.0% -> 30 pts (score capped at 30)
    yield_spread_score = max(0, min(30, (latest_spread + 1.0) * 10))
    st.markdown(f"**Yield Spread:** {latest_spread:.2f}% ({yield_spread_score:.0f} points)")

    # Total Economic Health Score
    total_score = unemployment_score + inflation_score + yield_spread_score
    st.markdown(f"---")
    st.metric("Overall Economic Health Score", f"{total_score:.0f}/100")

    # Determine status label based on total score
    if total_score >= 80:
        status_label = "Excellent"
        st.success(f"Status: {status_label} 💪")
    elif total_score >= 60:
        status_label = "Good"
        st.info(f"Status: {status_label} 👍")
    elif total_score >= 40:
        status_label = "Fair"
        st.warning(f"Status: {status_label} ⚠️")
    else:
        status_label = "Weak"
        st.error(f"Status: {status_label} 👎")

st.markdown("---") # Add a separator after the section

# Removed forecast functions and plots

st.subheader("Recent Data")
# This is not the correct location for this change, the previous change already replaced this line
# st.dataframe(df.tail(10), use_container_width=True)
st.subheader("Summary Statistics")

summary_stats = df.describe()
st.dataframe(summary_stats, use_container_width=True)
st.subheader("Correlation Matrix")

corr_matrix = df.corr()
fig_corr = px.imshow(
    corr_matrix,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="RdBu_r", # Red-Blue diverging color scale
    title="Indicator Correlation Heatmap"
)
fig_corr.update_layout(
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    xaxis_zeroline=False,
    yaxis_zeroline=False,
    template="plotly_dark",
    height=600 # Adjust height for better visibility
)
st.plotly_chart(fig_corr, use_container_width=True)
st.subheader("Forecast")

window_size = 12
forecast = df['GDP'].rolling(window=window_size).mean()
st.plotly_chart(px.line(x=df.index, y=forecast), use_container_width=True)

st.caption("Kosicodie Macro Dashboard • Data from FRED (St. Louis Fed) • Built by Kosi")
