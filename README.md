# 🛡️ FraudShield — Fraud Detection Dashboard

A professional Streamlit dashboard for fraud detection, monitoring, and ML-powered risk scoring.

## Features

- **📊 Overview** — KPIs, fraud trends, geographic heatmap, top risk merchants
- **🔍 Transaction Monitor** — Searchable, filterable transaction log with risk scatter plots
- **🤖 ML Detection** — ROC curve, confusion matrix, feature importance, and live transaction scoring
- **⚠️ Alert Center** — Active alert feed with analyst assignment and rule engine status
- **📈 Analytics** — Hour/day heatmaps, fraud by transaction type, amount distributions, automated insights

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

## Project Structure

```
fraud_detection/
├── app.py                  # Main entry point & navigation
├── requirements.txt
├── pages/
│   ├── overview.py         # Overview dashboard
│   ├── transactions.py     # Transaction monitor
│   ├── ml_detection.py     # ML model performance & prediction
│   ├── alerts.py           # Alert center
│   └── analytics.py        # Deep-dive analytics
└── utils/
    └── data_generator.py   # Synthetic data generation
```

## Notes

- All data is **synthetically generated** for demonstration purposes.
- The ML model metrics are illustrative (simulated Random Forest classifier).
- Swap `data_generator.py` with your real data source to use in production.
