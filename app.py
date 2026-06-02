import streamlit as st
from fredapi import Fred
import pandas as pd
import plotly.express as px

# ================== CONFIG ==================
st.set_page_config(page_title="Kosicodie Macro Dashboard", layout="wide")
st.title("📈 Kosicodie Macro Dashboard")
st.subheader("US Macro Economic Trends • Built by a 19yo Econ Freshman")

# ←←← PUT YOUR FRED API KEY HERE ←←←
API_KEY = "22ff88e163768c8805a0589a9c4bf692"

fred = Fred(api_key=API_KEY)

# ================== DATA PULL ==================
@st.cache_data
def load_data():
    series = {
        'GDP': 'GDP',
        'Unemployment': 'UNRATE',
        'Inflation (CPI)': 'CPIAUCSL',
        'Fed Funds Rate': 'FEDFUNDS',
        '10Y Treasury': 'DGS10'
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

st.subheader("Recent Data")
st.dataframe(df.tail(10), use_container_width=True)

st.caption("Kosicodie Macro Dashboard • Data from FRED (St. Louis Fed) • Built by Kosi")
