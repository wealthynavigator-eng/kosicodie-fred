# Kosicodie Macro Dashboard

## Current Status

Functional v1 dashboard built with:
- Streamlit
- FRED API
- Plotly
- ARIMA forecasting
- Economic health scoring
- Recession analysis

---

## Immediate Priorities

### 1. Fix Recession Probability

Issue:
Positive yield spread shows low risk status but 99.86% recession probability.

Goal:
Positive spread = lower recession probability.
Negative spread = higher recession probability.

Status:
Diagnosed.

---

### 2. Fix ARIMA Forecast Plot

Issue:
Plotly Express crashes due to unsupported line_color argument.

Location:
app.py lines ~355-356.

Status:
Diagnosed.

---

### 3. Restore Recent Data Table

Display latest observations in dashboard.

Status:
Pending.

---

## Technical Debt

### Mixed Frequency Data

Current Data:

- GDP = quarterly
- CPI = monthly
- Treasury = daily

Current implementation:

df = pd.DataFrame(df_dict)

Future:
Store series independently and resample intentionally.

Priority:
Medium.

---

## Future Features

- NBER recession shading (USREC)
- Improved forecasting
- Export data
- Documentation
- Unit tests
- Deployment

---

## Development Rules

- One bug per prompt
- One feature per commit
- Use Groq when Gemini quota is exhausted
- Prefer manual edits for tiny fixes
