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
        fig = px.line(
            x=df.index,
            y=df[column],
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

if latest_spread < 0:
    st.error(f"⚠️ Yield Curve Inverted ({latest_spread:.2f}%)")
else:
    st.success(f"✅ Yield Curve Normal ({latest_spread:.2f}%)")

def calculate_recession_probability(yield_spread):
    probability = 1 / (1 + np.exp(-yield_spread))
    return probability

recession_probability = calculate_recession_probability(latest_spread)
st.metric("Recession Probability", f"{recession_probability:.2%}")

# Removed forecast functions and plots

st.subheader("Recent Data")
# This is not the correct location for this change, the previous change already replaced this line
# st.dataframe(df.tail(10), use_container_width=True)
st.subheader("Summary Statistics")

summary_stats = df.describe()
st.dataframe(summary_stats, use_container_width=True)
st.subheader("Correlation Matrix")

corr_matrix = df.corr()
st.dataframe(corr_matrix, use_container_width=True)
st.subheader("Forecast")

window_size = 12
forecast = df['GDP'].rolling(window=window_size).mean()
st.plotly_chart(px.line(x=df.index, y=forecast), use_container_width=True)

st.caption("Kosicodie Macro Dashboard • Data from FRED (St. Louis Fed) • Built by Kosi")
