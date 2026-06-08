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
    probability = 1 / (1 + np.exp(yield_spread * 5)) # Adjusted for more intuitive output with typical spreads
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

st.subheader("Economic Regime")

# --- Economic Regime Classification Methodology ---
# This classification is based on general macroeconomic characteristics.
# The thresholds are simplified for illustrative purposes and can be fine-tuned.
#
# Indicators used:
# - Unemployment Rate: Low (<4.5%), Moderate (4.5-6%), High (>6%)
# - Inflation Rate (YoY): Low (<2%), Moderate (2-4%), High (>4%)
# - Yield Spread: Inverted (<0%), Narrow (0-0.5%), Normal (>0.5%)

# Ensure values are available before proceeding.
# unemployment_rate, latest_inflation_rate, and latest_spread are already calculated above.
if np.isnan(unemployment_rate) or np.isnan(latest_inflation_rate) or np.isnan(latest_spread):
    st.warning("Could not determine Economic Regime due to missing data for key indicators.")
else:
    regime = "Unknown"
    status_emoji = "❓"
    status_func = st.info # Default to info

    # Define thresholds
    unemployment_low = 4.5
    unemployment_high = 6.0
    inflation_low = 2.0
    inflation_moderate_high = 4.0
    yield_spread_inverted = 0.0
    yield_spread_narrow = 0.5

    # Determine conditions
    is_unemployment_low = unemployment_rate < unemployment_low
    is_unemployment_moderate = unemployment_rate >= unemployment_low and unemployment_rate < unemployment_high
    is_unemployment_high = unemployment_rate >= unemployment_high

    is_inflation_low = latest_inflation_rate < inflation_low
    is_inflation_moderate = latest_inflation_rate >= inflation_low and latest_inflation_rate < inflation_moderate_high
    is_inflation_high = latest_inflation_rate >= inflation_moderate_high

    is_yield_spread_normal = latest_spread > yield_spread_narrow
    is_yield_spread_narrow_positive = latest_spread >= yield_spread_inverted and latest_spread <= yield_spread_narrow
    is_yield_spread_inverted = latest_spread < yield_spread_inverted

    # Classification Logic
    if is_unemployment_low and is_inflation_moderate and is_yield_spread_normal:
        regime = "Expansion"
        status_emoji = "🟢"
        status_func = st.success
    elif is_unemployment_low and is_inflation_high and is_yield_spread_normal: # Potentially overheating
        regime = "Expansion (Overheating Risk)"
        status_emoji = "🟡"
        status_func = st.warning
    elif is_unemployment_moderate and is_inflation_low and is_yield_spread_inverted:
        regime = "Slowdown"
        status_emoji = "🟠"
        status_func = st.warning
    elif is_unemployment_high and is_inflation_low: # Coming out of recession
        regime = "Recovery"
        status_emoji = "🔵"
        status_func = st.info
    elif is_unemployment_high and is_inflation_high:
        regime = "Stagflation"
        status_emoji = "🔴"
        status_func = st.error
    elif is_yield_spread_inverted: # Strong signal for upcoming slowdown/recession
        regime = "Slowdown (Yield Curve Inverted)"
        status_emoji = "⚠️"
        status_func = st.error
    else:
        regime = "Neutral/Mixed Signals"
        status_emoji = "⚪"
        status_func = st.info

    status_func(f"{status_emoji} Current Economic Regime: **{regime}**")

st.markdown("---") # Add a separator after the section

# Removed forecast functions and plots

st.subheader("Recent Data")
# This is not the correct location for this change, the previous change already replaced this line
# st.dataframe(df.tail(10), use_container_width=True)

st.subheader("Download Data")
csv_data = df.to_csv(index=True).encode('utf-8')
st.download_button(
    label="Download data as CSV",
    data=csv_data,
    file_name='economic_indicators.csv',
    mime='text/csv',
)

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

# --- ARIMA Forecast for Real GDP ---
# Ensure Real GDP data is available and clean
real_gdp_data = df['Real GDP'].dropna()

if not real_gdp_data.empty:
    # A simple ARIMA(1,1,1) model is chosen for demonstration.
    # Model order (p,d,q) can be optimized for better performance.
    try:
        model = ARIMA(real_gdp_data, order=(1,1,1))
        model_fit = model.fit()

        # Forecast for the next 8 quarters (2 years)
        # Note: ARIMA forecasts typically do not extend far into the future without increasing uncertainty.
        forecast_steps = 8
        forecast_result = model_fit.get_forecast(steps=forecast_steps)
        forecast_values = forecast_result.predicted_mean
        forecast_ci = forecast_result.conf_int()

        # Create a date range for the forecast period
        last_date = real_gdp_data.index[-1]
        forecast_index = pd.date_range(start=last_date, periods=forecast_steps + 1, freq='QS-OCT')[1:] # Quarterly start in Oct (FRED's GDPC1)

        # Combine historical and forecast data for plotting
        plot_df = pd.DataFrame({
            'Historical Real GDP': real_gdp_data,
            'Forecasted Real GDP': pd.Series(forecast_values, index=forecast_index)
        })

        # Plotting with Plotly
        fig_forecast = px.line(
            plot_df,
            title="Real GDP Historical and ARIMA Forecast (Next 8 Quarters)",
            template="plotly_dark",
            labels={'value': 'Real GDP (Billions of Chained 2017 Dollars)', 'index': 'Date'}
        )
        import plotly.graph_objects as go
        # Add confidence intervals
        fig_forecast.add_traces([
            go.Scatter(x=forecast_index, y=forecast_ci.iloc[:, 0], line_color='rgba(0,0,0,0)', showlegend=False, mode='lines'),
            go.Scatter(x=forecast_index, y=forecast_ci.iloc[:, 1], line_color='rgba(0,0,0,0)', fill='tonexty', fillcolor='rgba(0,100,80,0.2)', name='95% Confidence Interval', mode='lines')
        ])
        fig_forecast.update_layout(hovermode="x unified")
        st.plotly_chart(fig_forecast, use_container_width=True)

    except Exception as e:
        st.warning(f"Could not generate ARIMA forecast for Real GDP: {e}")
        st.write("Displaying simple historical Real GDP plot instead.")
        fig = px.line(
            x=real_gdp_data.index,
            y=real_gdp_data.values,
            title="Real GDP Historical Data",
            template="plotly_dark"
        )
        fig.update_layout(template="plotly_dark", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Real GDP data not available for forecasting.")

st.caption("Kosicodie Macro Dashboard • Data from FRED (St. Louis Fed) • Built by Kosi")
