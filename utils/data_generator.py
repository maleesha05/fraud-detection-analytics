import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

MERCHANTS = [
    "Amazon", "Walmart", "Target", "Best Buy", "Apple Store",
    "Shell Gas", "Marriott Hotels", "Delta Airlines", "Netflix", "Uber",
    "Unknown Merchant XZ", "CryptoExchange Pro", "QuickCash ATM", "IntlTransfer Ltd"
]

COUNTRIES = ["US", "US", "US", "US", "CA", "GB", "FR", "NG", "RU", "CN", "BR", "MX"]
CARD_TYPES = ["Visa", "Mastercard", "Amex", "Discover"]
TRANSACTION_TYPES = ["Purchase", "ATM Withdrawal", "Wire Transfer", "Online Payment", "International Transfer"]


def generate_transactions(n=500, period="Last 7 Days"):
    period_map = {
        "Last 24 Hours": 1,
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last Quarter": 90,
    }
    days = period_map.get(period, 7)
    end = datetime.now()
    start = end - timedelta(days=days)

    timestamps = [start + (end - start) * random.random() for _ in range(n)]
    timestamps.sort(reverse=True)

    amounts = np.concatenate([
        np.random.exponential(80, int(n * 0.75)),
        np.random.exponential(1200, int(n * 0.20)),
        np.random.exponential(5000, int(n * 0.05)),
    ])
    np.random.shuffle(amounts)
    amounts = np.clip(amounts, 1, 50000).round(2)

    fraud_prob = []
    for amt in amounts:
        if amt > 3000:
            fraud_prob.append(random.random() < 0.45)
        elif amt > 500:
            fraud_prob.append(random.random() < 0.12)
        else:
            fraud_prob.append(random.random() < 0.03)

    risk_scores = []
    for is_fraud, amt in zip(fraud_prob, amounts):
        base = 70 + random.gauss(0, 12) if is_fraud else 25 + random.gauss(0, 18)
        risk_scores.append(int(np.clip(base, 1, 100)))

    def risk_label(score):
        if score >= 70: return "High"
        elif score >= 40: return "Medium"
        return "Low"

    merchants = random.choices(MERCHANTS, k=n)
    countries = random.choices(COUNTRIES, k=n)

    df = pd.DataFrame({
        "transaction_id": [f"TXN{random.randint(100000,999999)}" for _ in range(n)],
        "timestamp": timestamps,
        "merchant": merchants,
        "amount": amounts[:n],
        "card_type": random.choices(CARD_TYPES, k=n),
        "transaction_type": random.choices(TRANSACTION_TYPES, k=n),
        "country": countries,
        "is_fraud": fraud_prob,
        "risk_score": risk_scores,
        "account_id": [f"ACC{random.randint(10000,99999)}" for _ in range(n)],
        "velocity_flag": [random.random() < 0.15 for _ in range(n)],
        "geo_mismatch": [random.random() < 0.1 for _ in range(n)],
    })
    df["risk_level"] = df["risk_score"].apply(risk_label)
    df["status"] = df.apply(
        lambda r: "Blocked" if r["is_fraud"] and r["risk_score"] > 80
        else "Under Review" if r["risk_score"] >= 40
        else "Cleared", axis=1
    )
    return df


def get_summary_stats(df):
    total = len(df)
    flagged = df[df["is_fraud"]].shape[0]
    high_risk = df[df["risk_level"] == "High"].shape[0]
    total_amount = df["amount"].sum()
    fraud_amount = df[df["is_fraud"]]["amount"].sum()

    return {
        "total_transactions": total,
        "flagged_transactions": flagged,
        "high_risk_count": high_risk,
        "fraud_rate": round(flagged / total * 100, 2),
        "total_amount": total_amount,
        "fraud_amount": fraud_amount,
        "fraud_amount_pct": round(fraud_amount / total_amount * 100, 2),
        "avg_risk_score": round(df["risk_score"].mean(), 1),
    }
