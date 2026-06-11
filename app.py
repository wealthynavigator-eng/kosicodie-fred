from dotenv import load_dotenv
load_dotenv()          # Load variables from .env file
import os
import streamlit as st
from fredapi import Fred
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm
from statsmodels.tsa.arima.model import ARIMA

# ============================================================================
# DESIGN SYSTEM — "Matte Terminal" (sodium-amber accent)
# Flat near-black panels, hairline borders, monospace numerics, zero glow.
# Color is reserved for economic signals only.
# ============================================================================
BG0, BG1, BG2 = "#0a0b0c", "#101214", "#16191c"
LINE, LINE2 = "#23272c", "#2d3238"
TXT, DIM, FAINT = "#e7e9eb", "#818991", "#565d64"
AMBER, AMBERD = "#ffb000", "#c9881a"
GOOD, WARN, BAD, INFO = "#5fae8c", "#e0a23c", "#cf6a5e", "#6f9bd1"

st.set_page_config(page_title="KOSICODIE // MACRO", layout="wide", page_icon="▦")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap');
:root{
  --bg0:#0a0b0c; --bg1:#101214; --bg2:#16191c; --line:#23272c; --line2:#2d3238;
  --txt:#e7e9eb; --dim:#818991; --faint:#565d64; --amber:#ffb000; --amberd:#c9881a;
  --good:#5fae8c; --warn:#e0a23c; --bad:#cf6a5e; --info:#6f9bd1;
}
.stApp{ background:var(--bg0); }
html, body, [class*="css"], .stApp, [data-testid="stMarkdownContainer"]{
  font-family:'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace; color:var(--txt);}
[data-testid="stHeader"]{ background:transparent; }
.block-container{ padding-top:2.4rem; padding-bottom:3rem; max-width:1520px; }
[data-testid="stSidebar"]{ background:var(--bg1); border-right:1px solid var(--line); }
[data-testid="stSidebar"] *{ font-family:'IBM Plex Mono', monospace; }

.term-head{ display:flex; align-items:baseline; gap:14px; border-bottom:1px solid var(--line);
  padding-bottom:12px; }
.term-title{ font-size:20px; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:var(--txt); }
.term-dot{ color:var(--amber); }
.term-sub{ font-size:11px; color:var(--faint); letter-spacing:1.5px; margin-left:auto; text-transform:uppercase; }

.statusbar{ display:grid; grid-template-columns:2fr 1fr 1fr; border:1px solid var(--line);
  border-radius:3px; margin:16px 0 6px; background:var(--bg1); }
.scell{ padding:13px 18px; border-right:1px solid var(--line); }
.scell:last-child{ border-right:none; }
.slabel{ font-size:10px; letter-spacing:1.5px; color:var(--dim); text-transform:uppercase; margin-bottom:7px; }
.sval{ font-size:18px; font-weight:600; letter-spacing:1px; }
.sdim{ color:var(--faint); font-weight:400; font-size:13px; }
.smark{ display:inline-block; width:7px; height:15px; margin-right:9px; vertical-align:-2px; }

.tcard{ border:1px solid var(--line); border-radius:3px; background:var(--bg1);
  padding:14px 16px 12px; height:100%; }
.tcard.accent{ border-color:var(--amberd); }
.tcard-top{ display:flex; justify-content:space-between; align-items:center; margin-bottom:11px; }
.tlabel{ font-size:10px; letter-spacing:1.5px; color:var(--dim); text-transform:uppercase; }
.ttag{ font-size:9px; color:var(--faint); border:1px solid var(--line2); border-radius:2px;
  padding:2px 6px; letter-spacing:1px; text-transform:uppercase; }
.tval{ font-size:30px; font-weight:600; line-height:1; color:var(--txt); letter-spacing:0.5px; }
.tcard.accent .tval{ color:var(--amber); }
.tsub{ display:flex; justify-content:space-between; align-items:center; margin-top:11px; }
.tunit{ font-size:10px; color:var(--faint); letter-spacing:1px; text-transform:uppercase; }
.tdelta{ font-size:11px; color:var(--dim); letter-spacing:0.5px; }

.hbar{ font-size:17px; letter-spacing:3px; line-height:1; margin:4px 0 2px; }
.hseg-off{ color:var(--line2); }

.statline{ font-size:11.5px; letter-spacing:0.8px; padding:9px 14px; border-left:2px solid var(--dim);
  background:var(--bg1); border-radius:0 3px 3px 0; margin:5px 0; text-transform:uppercase; color:var(--dim); }
.statline.good{ border-left-color:var(--good); color:var(--good); }
.statline.warn{ border-left-color:var(--warn); color:var(--warn); }
.statline.bad{ border-left-color:var(--bad); color:var(--bad); }
.statline.info{ border-left-color:var(--info); color:var(--info); }

.sechead{ font-size:11px; letter-spacing:2.5px; text-transform:uppercase; color:var(--dim);
  border-bottom:1px solid var(--line); padding-bottom:7px; margin:30px 0 16px; display:flex; justify-content:space-between; }
.sechead .idx{ color:var(--faint); }

.brk{ display:flex; justify-content:space-between; border-bottom:1px dotted var(--line);
  padding:8px 2px; font-size:13px; }
.brk .k{ color:var(--dim); text-transform:uppercase; letter-spacing:1px; font-size:11px; }
.brk .v{ color:var(--txt); }
.brk .pts{ color:var(--amber); font-size:11px; }

.stTabs [data-baseweb="tab-list"]{ gap:4px; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"]{ font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:1.5px;
  text-transform:uppercase; color:var(--dim); background:transparent; border-radius:0; }
.stTabs [aria-selected="true"]{ color:var(--amber); }

[data-testid="stMetricValue"]{ font-family:'IBM Plex Mono',monospace; color:var(--amber); }
[data-testid="stMetricLabel"]{ color:var(--dim); text-transform:uppercase; letter-spacing:1px; }

[data-testid="stTable"] table, .stDataFrame{ font-family:'IBM Plex Mono',monospace; font-size:12px; }
thead tr th{ background:var(--bg2) !important; color:var(--dim) !important; text-transform:uppercase;
  letter-spacing:1px; font-size:10px; border-color:var(--line) !important; }
tbody tr td{ background:var(--bg1) !important; color:var(--txt) !important; border-color:var(--line) !important; }

::-webkit-scrollbar{ width:10px; height:10px; }
::-webkit-scrollbar-track{ background:var(--bg0); }
::-webkit-scrollbar-thumb{ background:var(--line2); }
::-webkit-scrollbar-thumb:hover{ background:var(--amberd); }

.stDownloadButton button{ font-family:'IBM Plex Mono',monospace; background:var(--bg1); color:var(--amber);
  border:1px solid var(--amberd); border-radius:3px; text-transform:uppercase; letter-spacing:1.5px; font-size:11px; }
.stDownloadButton button:hover{ background:var(--amber); color:var(--bg0); border-color:var(--amber); }
.streamlit-expanderHeader{ font-size:11px; letter-spacing:1.5px; text-transform:uppercase; color:var(--dim); }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPERS
# ============================================================================
def style_fig(fig, height=320, spark=False, heatmap=False):
    fig.update_layout(
        paper_bgcolor=BG0, plot_bgcolor=BG1, height=height,
        font=dict(family="IBM Plex Mono, monospace", color=DIM, size=11),
        margin=dict(l=8, r=8, t=(36 if not spark else 2), b=(2 if spark else 8)),
        hovermode="x unified", showlegend=not spark,
        legend=dict(font=dict(size=10, color=DIM), bgcolor="rgba(0,0,0,0)",
                    orientation="h", y=1.06, x=0),
        title=dict(font=dict(family="IBM Plex Mono, monospace", color=TXT, size=13)),
    )
    ax = dict(gridcolor=LINE, linecolor=LINE, color=DIM, zeroline=False,
              tickfont=dict(size=10), showgrid=not spark)
    fig.update_xaxes(**ax)
    fig.update_yaxes(**ax)
    if spark:
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
    if heatmap:
        fig.update_xaxes(showgrid=False, showticklabels=True, visible=True)
        fig.update_yaxes(showgrid=False, showticklabels=True, visible=True)
    return fig

def sechead(title, idx):
    st.markdown(f'<div class="sechead"><span>{title}</span><span class="idx">{idx}</span></div>',
                unsafe_allow_html=True)

def delta_of(series, pct=False):
    """Return (text, direction) for the last period-over-period change, or (None, 'flat')."""
    s = series.dropna()
    if len(s) < 2:
        return None, "flat"
    cur, prev = s.iloc[-1], s.iloc[-2]
    if pct:
        if prev == 0:
            return None, "flat"
        d = (cur / prev - 1) * 100
        txt = f"{d:+.1f}%"
    else:
        d = cur - prev
        txt = f"{d:+.2f}pp"
    return txt, ("up" if d > 0 else ("down" if d < 0 else "flat"))

def metric_card(label, value, unit="", tag="", delta=None, direction="flat", accent=False):
    acc = " accent" if accent else ""
    tag_h = f'<span class="ttag">{tag}</span>' if tag else ""
    arrow = {"up": "▲", "down": "▼", "flat": "■"}.get(direction, "■")
    delta_h = f'<span class="tdelta">{arrow} {delta}</span>' if delta else '<span class="tdelta"></span>'
    return (f'<div class="tcard{acc}"><div class="tcard-top">'
            f'<span class="tlabel">{label}</span>{tag_h}</div>'
            f'<div class="tval">{value}</div>'
            f'<div class="tsub"><span class="tunit">{unit}</span>{delta_h}</div></div>')

def spark(series, height=72, color=AMBER, zero=False):
    s = series.dropna().tail(48)
    f = px.line(x=s.index, y=s.values)
    f.update_traces(line=dict(color=color, width=1.4), fill="tozeroy",
                    fillcolor="rgba(255,176,0,0.07)")
    f = style_fig(f, height=height, spark=True)
    if zero:
        f.add_hline(y=0, line=dict(color=LINE2, width=1, dash="dot"))
    return f

def health_color(score):
    if score >= 80: return GOOD
    if score >= 60: return GOOD
    if score >= 40: return WARN
    return BAD

def regime_severity(regime):
    if "Overheating" in regime: return "warn"
    if regime.startswith("Expansion"): return "good"
    if "Stagflation" in regime or "Slowdown" in regime: return "bad"
    if "Recovery" in regime: return "info"
    return "info"

SEV_COLOR = {"good": GOOD, "warn": WARN, "bad": BAD, "info": INFO}

def classify_regime(u, infl, spread):
    is_u_low, is_u_mod, is_u_high = u < 4.5, 4.5 <= u < 6.0, u >= 6.0
    is_i_low, is_i_mod, is_i_high = infl < 2.0, 2.0 <= infl < 4.0, infl >= 4.0
    is_y_norm, is_y_inv = spread > 0.5, spread < 0.0
    if is_u_low and is_i_mod and is_y_norm:   return "Expansion"
    if is_u_low and is_i_high and is_y_norm:  return "Expansion (Overheating Risk)"
    if is_u_mod and is_i_low and is_y_inv:    return "Slowdown"
    if is_u_high and is_i_low:                return "Recovery"
    if is_u_high and is_i_high:               return "Stagflation"
    if is_y_inv:                              return "Slowdown (Yield Curve Inverted)"
    return "Neutral/Mixed Signals"

def calculate_recession_probability(yield_spread):
    """
    Probability of a US recession within the NEXT 12 MONTHS.

    New York Fed (Estrella & Mishkin, 1996) probit on the 10Y-3M Treasury spread:
        P = Phi(alpha + beta * spread), alpha=-0.5333, beta=-0.6629, spread in pp.
    Source: FRBNY, "The Yield Curve as a Predictor of U.S. Recessions".
    """
    ALPHA, BETA = -0.5333, -0.6629
    return float(norm.cdf(ALPHA + BETA * yield_spread))

# ============================================================================
# DATA
# ============================================================================
API_KEY = os.getenv("FRED_API_KEY")
if not API_KEY:
    st.error("FRED_API_KEY not found in .env file")
    st.stop()
fred = Fred(api_key=API_KEY)

@st.cache_data
def load_data():
    series = {
        'GDP': 'GDP',
        'Unemployment': 'UNRATE',
        'Inflation (CPI)': 'CPIAUCSL',
        'Fed Funds Rate': 'FEDFUNDS',
        '10Y Treasury': 'DGS10',
        'Personal Consumption Expenditures': 'PCE',
        'Real GDP': 'GDPC1',
        # 10Y minus 3M Treasury spread — the NY Fed / Estrella-Mishkin standard
        # recession predictor, pulled directly so it is computed consistently.
        'Yield Spread': 'T10Y3M'
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

    raw = pd.DataFrame(df_dict)
    # Native monthly grid WITHOUT forward-fill: quarterly series keep NaN in their
    # off-quarter months, so .describe()/.corr() see real observations rather than
    # duplicated values. This is the ANALYSIS frame.
    df_raw = raw.resample('MS').last()
    # DISPLAY frame: forward-filled so cards, charts, score and regime always have a
    # latest value on the common monthly grid.
    df = df_raw.ffill()

    # Monthly-AVERAGE 10Y-3M spread for the recession probit. Estrella-Mishkin was
    # estimated on monthly averages of the daily spread, not a single month-end print.
    spread_monthly_avg = None
    if 'Yield Spread' in df_dict:
        spread_monthly_avg = df_dict['Yield Spread'].resample('MS').mean()

    print(f"Dataframe shape: {df.shape}")
    return df, df_raw, spread_monthly_avg

df, df_raw, spread_monthly_avg = load_data()

# ============================================================================
# COMPUTE  (all scalars derived first, then rendered)
# ============================================================================
def last_val(col):
    if col in df.columns and not df[col].dropna().empty:
        return df[col].dropna().iloc[-1]
    return np.nan

latest_gdp = last_val('GDP')
gdp_delta, gdp_dir = delta_of(df['GDP'], pct=True) if 'GDP' in df else (None, "flat")

unemployment_rate = last_val('Unemployment')
unemp_delta, unemp_dir = delta_of(df['Unemployment']) if 'Unemployment' in df else (None, "flat")

inflation_series = df["Inflation (CPI)"].dropna().pct_change(12) if "Inflation (CPI)" in df else pd.Series(dtype=float)
latest_inflation_rate = inflation_series.dropna().iloc[-1] * 100 if not inflation_series.dropna().empty else np.nan
infl_delta, infl_dir = delta_of(inflation_series * 100)

latest_spread = last_val('Yield Spread')
spread_delta, spread_dir = delta_of(df['Yield Spread']) if 'Yield Spread' in df else (None, "flat")

# Recession probit — monthly-average spread, fall back to latest displayed spread.
probit_spread = np.nan
if spread_monthly_avg is not None and not spread_monthly_avg.dropna().empty:
    probit_spread = spread_monthly_avg.dropna().iloc[-1]
elif not np.isnan(latest_spread):
    probit_spread = latest_spread
recession_probability = calculate_recession_probability(probit_spread) if not np.isnan(probit_spread) else np.nan

# Economic Health Score
have_score = not (np.isnan(unemployment_rate) or np.isnan(latest_inflation_rate) or np.isnan(latest_spread))
unemployment_score = inflation_score = yield_spread_score = total_score = np.nan
status_label = status_sev = None
if have_score:
    unemployment_score = max(0, 35 - (unemployment_rate - 3.5) * 10)
    inflation_score = max(0, 35 - abs(latest_inflation_rate - 2.0) * 15)
    yield_spread_score = max(0, min(30, (latest_spread + 1.0) * 10))
    total_score = unemployment_score + inflation_score + yield_spread_score
    if total_score >= 80:   status_label, status_sev = "Excellent", "good"
    elif total_score >= 60: status_label, status_sev = "Good", "info"
    elif total_score >= 40: status_label, status_sev = "Fair", "warn"
    else:                   status_label, status_sev = "Weak", "bad"

# Economic Regime
regime = regime_sev = regime_col = None
if have_score:
    regime = classify_regime(unemployment_rate, latest_inflation_rate, latest_spread)
    regime_sev = regime_severity(regime)
    regime_col = SEV_COLOR[regime_sev]

last_updated = df.index[-1].strftime('%Y-%m-%d') if not df.empty else "N/A"

# quarter / month tags
def qtag(col):
    s = df[col].dropna()
    if s.empty: return ""
    d = s.index[-1]
    return f"Q{((d.month - 1)//3)+1} {d.year}"
def mtag(col):
    s = df[col].dropna()
    return s.index[-1].strftime('%b %Y').upper() if not s.empty else ""

# ============================================================================
# SIDEBAR
# ============================================================================
st.sidebar.markdown('<div class="slabel" style="margin-bottom:10px;">▦ CONTROL</div>',
                    unsafe_allow_html=True)
WINDOWS = {"ALL": None, "10Y": 120, "5Y": 60, "2Y": 24}
window_key = st.sidebar.radio("HISTORY WINDOW", list(WINDOWS.keys()), index=0)
window_months = WINDOWS[window_key]

available_indicators = [c for c in df.columns if c not in ["Yield Spread", "Real GDP"]]
selected_indicators = st.sidebar.multiselect("SELECT INDICATORS", options=available_indicators,
                                              default=available_indicators)

# ============================================================================
# HEADER + STATUS STRIP
# ============================================================================
st.markdown(
    '<div class="term-head"><span class="term-dot">●</span>'
    '<span class="term-title">Kosicodie · Macro</span>'
    '<span class="term-sub">FRED // St. Louis Fed · Monthly · Live</span></div>',
    unsafe_allow_html=True)

regime_txt = regime.upper() if regime else "—"
regime_mark = regime_col if regime_col else FAINT
score_txt = f"{total_score:.0f}<span class='sdim'>/100</span>" if have_score else "—"
score_col = health_color(total_score) if have_score else FAINT
st.markdown(f"""
<div class="statusbar">
  <div class="scell"><div class="slabel">Economic Regime</div>
    <div class="sval"><span class="smark" style="background:{regime_mark};"></span>
    <span style="color:{regime_mark};">{regime_txt}</span></div></div>
  <div class="scell"><div class="slabel">Health Score</div>
    <div class="sval" style="color:{score_col};">{score_txt}</div></div>
  <div class="scell"><div class="slabel">Last Updated</div>
    <div class="sval">{last_updated}</div></div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 01 / SIGNALS
# ============================================================================
sechead("Signals", "01")

c1, c2, c3, c4 = st.columns(4)
with c1:
    v = f"${latest_gdp:,.0f}B" if not np.isnan(latest_gdp) else "—"
    st.markdown(metric_card("GDP", v, "Billions · SAAR", qtag('GDP'), gdp_delta, gdp_dir),
                unsafe_allow_html=True)
with c2:
    v = f"{unemployment_rate:.1f}%" if not np.isnan(unemployment_rate) else "—"
    st.markdown(metric_card("Unemployment", v, "Rate", mtag('Unemployment'), unemp_delta, unemp_dir),
                unsafe_allow_html=True)
with c3:
    v = f"{latest_inflation_rate:.1f}%" if not np.isnan(latest_inflation_rate) else "—"
    st.markdown(metric_card("Inflation", v, "CPI · YoY", "YOY", infl_delta, infl_dir),
                unsafe_allow_html=True)
with c4:
    v = f"{latest_spread:.2f}%" if not np.isnan(latest_spread) else "—"
    st.markdown(metric_card("Yield Spread", v, "10Y − 3M", "T10Y3M", spread_delta, spread_dir),
                unsafe_allow_html=True)

s1, s2 = st.columns([1, 1])
with s1:
    rv = f"{recession_probability:.1%}" if not np.isnan(recession_probability) else "—"
    st.markdown(metric_card("Recession · 12M", rv, "Estrella–Mishkin Probit", "PROBIT", accent=True),
                unsafe_allow_html=True)
    if 'Yield Spread' in df and not df['Yield Spread'].dropna().empty:
        st.markdown('<div class="tunit" style="margin:8px 2px 0;">10Y−3M SPREAD · 48M</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(spark(df['Yield Spread'], zero=True), use_container_width=True,
                        config={"displayModeBar": False})
with s2:
    if have_score:
        segs = int(round(total_score / 10))
        bar = "".join(f'<span style="color:{health_color(total_score)};">▌</span>' for _ in range(segs))
        bar += "".join('<span class="hseg-off">▌</span>' for _ in range(10 - segs))
        st.markdown(
            f'<div class="tcard"><div class="tcard-top"><span class="tlabel">Economic Health</span>'
            f'<span class="ttag">{status_label}</span></div>'
            f'<div class="tval" style="color:{health_color(total_score)};">{total_score:.0f}'
            f'<span class="sdim" style="font-size:16px;">/100</span></div>'
            f'<div class="hbar">{bar}</div>'
            f'<div class="tsub"><span class="tunit">Unemployment · Inflation · Curve</span></div></div>',
            unsafe_allow_html=True)
    else:
        st.markdown(metric_card("Economic Health", "—", "Insufficient data"), unsafe_allow_html=True)

# Slim status lines: recession risk (curve) + regime
if not np.isnan(latest_spread):
    if latest_spread < 0:
        st.markdown(f'<div class="statline bad">● High Recession Risk — Yield Curve Inverted ({latest_spread:.2f}%)</div>', unsafe_allow_html=True)
    elif latest_spread < 0.5:
        st.markdown(f'<div class="statline warn">● Moderate Risk — Narrow Yield Spread ({latest_spread:.2f}%)</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="statline good">● Low Recession Risk — Normal Yield Spread ({latest_spread:.2f}%)</div>', unsafe_allow_html=True)
if regime:
    st.markdown(f'<div class="statline {regime_sev}">▌ Current Regime — {regime}</div>', unsafe_allow_html=True)

# Score composition (tucked into an expander to keep the surface clean)
if have_score:
    with st.expander("SCORE COMPOSITION"):
        rows = [
            ("Unemployment Rate", f"{unemployment_rate:.1f}%", f"{unemployment_score:.0f} / 35"),
            ("Inflation (YoY)", f"{latest_inflation_rate:.1f}%", f"{inflation_score:.0f} / 35"),
            ("Yield Spread", f"{latest_spread:.2f}%", f"{yield_spread_score:.0f} / 30"),
        ]
        for k, val, pts in rows:
            st.markdown(f'<div class="brk"><span class="k">{k}</span>'
                        f'<span><span class="v">{val}</span> &nbsp; '
                        f'<span class="pts">{pts}</span></span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="brk"><span class="k">Total</span>'
                    f'<span class="pts">{total_score:.0f} / 100 · {status_label}</span></div>',
                    unsafe_allow_html=True)

# ============================================================================
# 02 / INDICATORS
# ============================================================================
sechead(f"Indicators · {window_key}", "02")
for column in selected_indicators:
    if column in df.columns:
        s = df[column].dropna()
        if window_months:
            s = s.tail(window_months)
        fig = px.line(x=s.index, y=s.values, title=column.upper())
        fig.update_traces(line=dict(color=AMBER, width=1.6))
        st.plotly_chart(style_fig(fig, height=300), use_container_width=True,
                        config={"displayModeBar": False})

# ============================================================================
# 03 / ANALYTICS
# ============================================================================
sechead("Analytics", "03")
tab_stats, tab_corr, tab_fc = st.tabs(["SUMMARY", "CORRELATION", "FORECAST"])

with tab_stats:
    st.caption("Computed on raw (non-forward-filled) monthly observations.")
    st.dataframe(df_raw.describe(), use_container_width=True)

with tab_corr:
    st.caption("Quarterly growth-rate correlations (stationary) — not forward-filled levels.")
    analysis_cols = [c for c in df_raw.columns if c != "Yield Spread"]
    growth = df_raw[analysis_cols].resample('QS').last().pct_change()
    corr_matrix = growth.corr()
    fig_corr = px.imshow(corr_matrix, text_auto=".2f", aspect="auto",
                         color_continuous_scale=[[0, BAD], [0.5, BG1], [1, GOOD]],
                         zmin=-1, zmax=1)
    fig_corr.update_traces(textfont=dict(family="IBM Plex Mono, monospace", size=10))
    st.plotly_chart(style_fig(fig_corr, height=520, heatmap=True), use_container_width=True,
                    config={"displayModeBar": False})

with tab_fc:
    real_gdp_data = df['Real GDP'].dropna() if 'Real GDP' in df else pd.Series(dtype=float)
    if not real_gdp_data.empty:
        try:
            model_fit = ARIMA(real_gdp_data, order=(1, 1, 1)).fit()
            steps = 8
            fr = model_fit.get_forecast(steps=steps)
            fvals, fci = fr.predicted_mean, fr.conf_int()
            fidx = pd.date_range(start=real_gdp_data.index[-1], periods=steps + 1, freq='QS-OCT')[1:]
            plot_df = pd.DataFrame({
                'Historical Real GDP': real_gdp_data,
                'Forecasted Real GDP': pd.Series(fvals.values, index=fidx),
            })
            fig_fc = px.line(plot_df, title="REAL GDP · ARIMA(1,1,1) · NEXT 8 QUARTERS")
            fig_fc.for_each_trace(lambda t: t.update(line=dict(color=AMBER, width=1.8))
                                  if "Historical" in t.name
                                  else t.update(line=dict(color=AMBERD, width=1.8, dash="dash")))
            fig_fc.add_traces([
                go.Scatter(x=fidx, y=fci.iloc[:, 0], line=dict(color="rgba(0,0,0,0)"),
                           showlegend=False, mode="lines"),
                go.Scatter(x=fidx, y=fci.iloc[:, 1], line=dict(color="rgba(0,0,0,0)"),
                           fill="tonexty", fillcolor="rgba(255,176,0,0.10)",
                           name="95% CI", mode="lines"),
            ])
            st.plotly_chart(style_fig(fig_fc, height=380), use_container_width=True,
                            config={"displayModeBar": False})
        except Exception as e:
            st.markdown(f'<div class="statline warn">ARIMA forecast unavailable — {e}</div>',
                        unsafe_allow_html=True)
            fig = px.line(x=real_gdp_data.index, y=real_gdp_data.values, title="REAL GDP · HISTORICAL")
            fig.update_traces(line=dict(color=AMBER, width=1.6))
            st.plotly_chart(style_fig(fig, height=380), use_container_width=True,
                            config={"displayModeBar": False})
    else:
        st.markdown('<div class="statline warn">Real GDP data not available for forecasting.</div>',
                    unsafe_allow_html=True)

# ============================================================================
# 04 / DATA
# ============================================================================
sechead("Data", "04")
d1, d2 = st.columns([2, 1])
with d1:
    sel = df.columns[0] if 'GDP' in df.columns else (selected_indicators[0] if selected_indicators else df.columns[0])
    recent = df[sel].dropna().tail(10).to_frame('Value').reset_index()
    recent['index'] = recent['index'].dt.strftime('%Y-%m-%d')
    recent = recent.rename(columns={'index': 'Date'})
    st.markdown(f'<div class="tunit" style="margin-bottom:8px;">RECENT · {sel.upper()}</div>',
                unsafe_allow_html=True)
    st.table(recent[['Date', 'Value']])
with d2:
    st.markdown('<div class="tunit" style="margin-bottom:8px;">EXPORT</div>', unsafe_allow_html=True)
    st.download_button("↓ Download CSV", data=df.to_csv(index=True).encode('utf-8'),
                       file_name='economic_indicators.csv', mime='text/csv')

st.markdown(
    '<div class="term-sub" style="margin-top:34px; border-top:1px solid #23272c; padding-top:14px;">'
    'Kosicodie Macro Dashboard · Data from FRED (St. Louis Fed) · Recession model: NY Fed Estrella–Mishkin probit'
    '</div>', unsafe_allow_html=True)
