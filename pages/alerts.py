import streamlit as st
import pandas as pd
from datetime import datetime
import random
from utils.data_generator import generate_transactions

def render(risk_filter):
    df = generate_transactions(500, "Last 7 Days")
    high_risk = df[df["risk_level"]=="High"].sort_values("risk_score", ascending=False)

    st.markdown("""
    <div class="page-header">
        <h2>⚠️ Alert Center</h2>
        <p>Active fraud alerts requiring investigation or immediate action</p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, label, value, color, sub in [
        (c1, "Critical Alerts",     str(high_risk[high_risk["risk_score"]>=85].shape[0]), "#ef4444", "Require immediate action"),
        (c2, "Under Investigation", str(df[df["status"]=="Under Review"].shape[0]),        "#f59e0b", "Assigned to analysts"),
        (c3, "Resolved Today",      "47",                                                   "#10b981", "▲ +12 vs yesterday"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-top:3px solid {color};padding:18px 22px;">
                <div class="kpi-label">{label}</div>
                <div style="font-size:2rem;font-weight:800;font-family:'JetBrains Mono',monospace;color:#f1f5f9;">{value}</div>
                <div style="font-size:0.75rem;color:{color};margin-top:4px;">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Active Alert Feed</div>', unsafe_allow_html=True)

    analysts = ["Sarah K.","James W.","Priya M.","Tom R.","Unassigned"]

    for _, row in high_risk.head(12).iterrows():
        score = row["risk_score"]
        color = "#ef4444" if score>=70 else "#f59e0b"
        badge = f'<span class="badge badge-red">{"CRITICAL" if score>=85 else "HIGH"}</span>'

        flags = []
        if row["velocity_flag"]: flags.append("⚡ Velocity")
        if row["geo_mismatch"]:  flags.append("🌍 Geo Mismatch")
        if row["amount"]>2000:   flags.append("💰 High Value")
        if row["country"] not in ["US","CA","GB"]: flags.append("🌐 International")
        flag_str = " · ".join(flags) if flags else "Standard screening"

        analyst = random.choice(analysts)
        ts = pd.to_datetime(row["timestamp"])
        mins = int((datetime.now()-ts.to_pydatetime()).total_seconds()//60)
        time_str = f"{mins}m ago" if mins<60 else f"{mins//60}h ago"

        st.markdown(f"""
        <div class="alert-card high">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    {badge}
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.82rem;font-weight:600;color:#e2e8f0;">{row['transaction_id']}</span>
                    <span style="font-size:0.72rem;color:#334155;">{time_str}</span>
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;font-weight:800;color:{color};">${row['amount']:,.2f}</div>
            </div>
            <div style="font-size:0.82rem;color:#94a3b8;margin-bottom:4px;">
                <b style="color:#cbd5e1;">{row['merchant']}</b> &nbsp;·&nbsp; {row['transaction_type']} &nbsp;·&nbsp; {row['country']} &nbsp;·&nbsp; {row['card_type']}
            </div>
            <div style="font-size:0.75rem;color:#475569;">
                Risk: <b style="color:{color};">{score}</b> &nbsp;·&nbsp; {flag_str} &nbsp;·&nbsp; Analyst: {analyst}
            </div>
        </div>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1,1,5])
        with col1:
            st.button("✅ Clear", key=f"c_{row['transaction_id']}")
        with col2:
            st.button("🚫 Block", key=f"b_{row['transaction_id']}")

    st.markdown('<div class="section-title">Rule Engine</div>', unsafe_allow_html=True)
    rules = [
        ("Velocity Check",           "🟢 Active", "5+ transactions within 10 minutes",         1243),
        ("High-Value International", "🟢 Active", "International transfers > $3,000",           87),
        ("Night Hours Anomaly",      "🟢 Active", "Transactions between 02:00–05:00 local",     334),
        ("New Device + High Amount", "🟢 Active", "New device with transaction > $500",          156),
        ("Country Blocklist",        "🟡 Paused", "Block transactions from sanctioned regions",   0),
        ("Card Testing Pattern",     "🟢 Active", "Micro-transactions followed by large charge", 612),
    ]
    rdf = pd.DataFrame(rules, columns=["Rule Name","Status","Condition","Triggered (30d)"])
    st.dataframe(rdf, use_container_width=True, hide_index=True)