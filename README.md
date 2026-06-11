# Kosicodie Macro Dashboard

A real-time U.S. macroeconomic dashboard built with **Streamlit** and live data from the
**FRED API** (Federal Reserve Bank of St. Louis). It tracks the key indicators, scores the
state of the economy, classifies the current regime, and estimates recession risk using a
published Federal Reserve model — all in a flat, monospace "terminal" interface.

> Built by Kosi · Data from [FRED](https://fred.stlouisfed.org/)

---

## Features

- **Live indicators** — GDP, Unemployment, CPI inflation (YoY), Fed Funds Rate, 10Y Treasury,
  Personal Consumption Expenditures, Real GDP, and the 10Y–3M yield spread.
- **Recession probability** — 12-month-ahead estimate from the New York Fed
  **Estrella–Mishkin probit** model on the 10Y–3M Treasury spread.
- **Economic Health Score** — a transparent 0–100 composite of unemployment, inflation, and
  the yield curve.
- **Economic Regime classification** — Expansion / Overheating / Slowdown / Recovery /
  Stagflation, based on the indicator mix.
- **Yield-curve risk signal** — inversion-aware recession-risk banner.
- **Interactive analytics** — adjustable history window, indicator selection, summary
  statistics, a growth-rate correlation matrix, and an ARIMA forecast of Real GDP.
- **CSV export** of the full dataset.

---

## Methodology

The dashboard is built to be **economically and statistically defensible**, not just pretty.

### Recession probability — NY Fed probit
Probability of a U.S. recession within the next 12 months:

```
P(recession) = Φ(-0.5333 - 0.6629 × spread)
```

where `Φ` is the standard normal CDF and `spread` is the **10Y minus 3M Treasury** yield
(FRED series `T10Y3M`) in percentage points, averaged monthly — the input the model was
estimated on. Coefficients are the published Estrella & Mishkin (1996) values.

### Yield spread
Uses the **10Y–3M** spread (`T10Y3M`), the academically validated recession predictor, rather
than an ad-hoc 10Y–Fed-Funds difference.

### Economic Health Score (0–100)
| Component | Max | Target |
|-----------|----:|--------|
| Unemployment | 35 | 3.5% |
| Inflation (CPI YoY) | 35 | 2.0% |
| Yield Spread | 30 | positive / steep |

### Mixed-frequency handling
Series arrive at different frequencies (GDP quarterly, CPI/Unemployment monthly, Treasuries
daily). The app keeps **two frames**:

- **Display frame** — resampled to a common monthly grid and forward-filled, so cards and
  charts always show a latest value.
- **Analysis frame** — native monthly observations **without** forward-fill, used for summary
  statistics and correlations. Correlations are computed on **quarterly growth rates**
  (stationary) to avoid the serial-correlation artifacts of correlating forward-filled levels.

> ⚠️ This is an educational/portfolio project. The models are simplified and **not investment
> advice**.

---

## Getting started

### Prerequisites
- Python 3.13 (3.10+ should work)
- A free **FRED API key** — get one at
  [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html)

### Installation

```bash
# clone
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root with your FRED API key:

```env
FRED_API_KEY=your_fred_api_key_here
```

> `.env` is git-ignored — your key is never committed.

### Run

```bash
streamlit run app.py
```

The dashboard opens at [http://localhost:8501](http://localhost:8501).

---

## Project structure

```
.
├── app.py                 # the entire dashboard (data, models, UI)
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Matte Terminal theme (dark base, amber accent, mono)
├── .env                   # FRED_API_KEY (not committed)
└── README.md
```

---

## Tech stack

| Tool | Role |
|------|------|
| [Streamlit](https://streamlit.io/) | UI / app framework |
| [fredapi](https://github.com/mortada/fredapi) | FRED data access |
| [pandas](https://pandas.pydata.org/) / [numpy](https://numpy.org/) | data wrangling |
| [Plotly](https://plotly.com/python/) | charts |
| [SciPy](https://scipy.org/) | normal CDF for the probit model |
| [statsmodels](https://www.statsmodels.org/) | ARIMA forecast |

---

## Data sources

All data from the **Federal Reserve Bank of St. Louis (FRED)**:

| Series | FRED ID |
|--------|---------|
| Nominal GDP | `GDP` |
| Real GDP | `GDPC1` |
| Unemployment Rate | `UNRATE` |
| CPI | `CPIAUCSL` |
| Fed Funds Rate | `FEDFUNDS` |
| 10Y Treasury | `DGS10` |
| 10Y–3M Spread | `T10Y3M` |
| Personal Consumption Expenditures | `PCE` |

---

## License

MIT — see [`LICENSE`](LICENSE) if included. Educational use; not financial advice.
