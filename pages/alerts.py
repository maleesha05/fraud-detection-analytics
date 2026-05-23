import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
from utils.data_generator import generate_transactions


def render(risk_filter):
    df = generate_transactions(500, "Last 7 Days")
    high_risk = df[df["risk_level"] == "High"].sort_values("risk_score", ascending=False)

    st.markdown("## ⚠️ Alert Center")
    st.caption("Active fraud alerts requiring investigation or action")

    # Alert summary bar
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""
    <div class="metric-card danger">
        <h3>Critical Alerts</h3>
        <div class="value">{high_risk[high_risk['risk_score']>=85].shape[0]}</div>
        <div class="delta up">Require immediate action</div>
    </div>""", unsafe_allow_html=True)

    c2.markdown(f"""
    <div class="metric-card warning">
        <h3>Under Investigation</h3>
        <div class="value">{df[df['status']=='Under Review'].shape[0]}</div>
        <div class="delta">Assigned to analysts</div>
    </div>""", unsafe_allow_html=True)

    c3.markdown(f"""
    <div class="metric-card success">
        <h3>Resolved Today</h3>
        <div class="value">47</div>
        <div class="delta down">▲ +12 vs yesterday</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Active alerts feed
    st.markdown('<div class="section-title">Active Alert Feed</div>', unsafe_allow_html=True)

    alerts = high_risk.head(15).copy()
    alerts["timestamp"] = pd.to_datetime(alerts["timestamp"])

    analysts = ["Sarah K.", "James W.", "Priya M.", "Tom R.", "Unassigned"]

    for _, row in alerts.iterrows():
        score = row["risk_score"]
        if score >= 85:
            badge = '<span class="badge-high">CRITICAL</span>'
            border = "#e02424"
            bg = "#fff8f8"
        elif score >= 70:
            badge = '<span class="badge-high">HIGH</span>'
            border = "#e02424"
            bg = "#fff8f8"
        else:
            badge = '<span class="badge-medium">MEDIUM</span>'
            border = "#e3a008"
            bg = "#fffdf0"

        flags = []
        if row["velocity_flag"]: flags.append("⚡ Velocity")
        if row["geo_mismatch"]: flags.append("🌍 Geo Mismatch")
        if row["amount"] > 2000: flags.append("💰 High Value")
        if row["country"] not in ["US", "CA", "GB"]: flags.append("🌐 Intl Origin")
        flag_str = " · ".join(flags) if flags else "Standard screening"

        analyst = random.choice(analysts)
        time_ago = int((datetime.now() - row["timestamp"].to_pydatetime()).total_seconds() // 60)
        time_str = f"{time_ago}m ago" if time_ago < 60 else f"{time_ago // 60}h ago"

        with st.container():
            st.markdown(f"""
            <div style="background:{bg};border:1px solid #e5e7eb;border-left:4px solid {border};
                        border-radius:8px;padding:14px 18px;margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        {badge}
                        <span style="font-family:'IBM Plex Mono',monospace;font-size:0.85rem;
                                     font-weight:600;color:#111827;margin-left:8px;">{row['transaction_id']}</span>
                        <span style="color:#9ca3af;font-size:0.78rem;margin-left:8px;">{time_str}</span>
                    </div>
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:1.1rem;font-weight:700;color:{border};">
                        ${row['amount']:,.2f}
                    </div>
                </div>
                <div style="margin-top:6px;font-size:0.82rem;color:#374151;">
                    <b>{row['merchant']}</b> · {row['transaction_type']} · {row['country']} · {row['card_type']}
                </div>
                <div style="margin-top:4px;font-size:0.78rem;color:#6b7280;">
                    Risk Score: <b style="color:{border};">{score}</b> · {flag_str}
                </div>
                <div style="margin-top:4px;font-size:0.75rem;color:#9ca3af;">
                    Account: {row['account_id']} · Assigned: {analyst}
                </div>
            </div>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            st.button("✅ Clear", key=f"clear_{row['transaction_id']}")
        with col2:
            st.button("🚫 Block", key=f"block_{row['transaction_id']}")

    # Rules engine
    st.markdown('<div class="section-title">Rule Engine Status</div>', unsafe_allow_html=True)
    rules = [
        ("Velocity Check", "Active", "Flag 5+ transactions within 10 minutes", 1243, "#057a55"),
        ("High-Value International", "Active", "Flag international transfers > $3,000", 87, "#057a55"),
        ("Night Hours Anomaly", "Active", "Flag transactions between 02:00–05:00 local", 334, "#057a55"),
        ("New Device + High Amount", "Active", "New device with transaction > $500", 156, "#057a55"),
        ("Country Blocklist", "Paused", "Block transactions from sanctioned countries", 0, "#e3a008"),
        ("Card Testing Pattern", "Active", "Flag micro-transactions followed by large charge", 612, "#057a55"),
    ]

    rule_df = pd.DataFrame(rules, columns=["Rule Name", "Status", "Condition", "Triggered (30d)", ""])
    rule_df = rule_df.drop(columns=[""])
    st.dataframe(rule_df, use_container_width=True, hide_index=True)
