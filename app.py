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

# ←←← PUT YOUR FRED API KEY HERE ←←←
# Replace with your actual FRED API key
API_KEY = "YOUR_ACTUAL_FRED_API_KEY"

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
        'Consumer Price Index': 'CPI',
        'Personal Consumption Expenditures': 'PCE',
        'GDP Growth Rate': 'GDPC1'
    }
    
    df_dict = {}
    for name, sid in series.items():
        data = fred.get_series(sid, observation_start='2010-01-01')
        df_dict[name] = data
    
    df = pd.DataFrame(df_dict)
    return df

df = load_data()

# ================== DASHBOARD ==================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Latest GDP", f"${df['GDP'].dropna().iloc[-1]:,.0f}B")

with col2:
    st.metric("Unemployment Rate", f"{df['Unemployment'].dropna().iloc[-1]:.1f}%")

with col3:
    # Fixed Indentation & Added Metric Label
    inflation_series = (
        df["Inflation (CPI)"]
        .pct_change(12)
        .dropna()
    )

    if not inflation_series.empty:
        latest_inflation = inflation_series.iloc[-1] * 100
        st.metric("Inflation Rate (YoY)", f"{latest_inflation:.1f}%")
    else:
        st.metric("Inflation Rate (YoY)", "N/A")

st.subheader("Economic Trends Over Time")
st.subheader("Time Series Plots")

for column in df.columns:
    if column != "Yield Spread":
        fig = px.line(
            df,
            x=df.index,
            y=column,
            title=column,
            template="plotly_dark"
        )
        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

# Yield spread calculation
df["Yield Spread"] = df["10Y Treasury"] - df["Fed Funds Rate"]

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
