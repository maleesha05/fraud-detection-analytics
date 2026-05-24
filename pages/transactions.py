import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_generator import generate_transactions
from utils.chart_theme import apply_theme


def render(date_range, risk_filter):
    df = generate_transactions(500, date_range)
    if risk_filter:
        df = df[df["risk_level"].isin(risk_filter)]

    st.markdown("## 🔍 Transaction Monitor")
    st.caption("Real-time transaction screening and investigation")

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search = st.text_input("Search by Transaction ID or Account", placeholder="TXN... or ACC...")
    with col2:
        status_filter = st.selectbox("Status", ["All", "Blocked", "Under Review", "Cleared"])
    with col3:
        txn_type = st.selectbox("Type", ["All"] + list(df["transaction_type"].unique()))
    with col4:
        min_amt, max_amt = st.slider("Amount Range ($)", 0, 50000, (0, 50000), step=100)

    filtered = df.copy()
    if search:
        filtered = filtered[
            filtered["transaction_id"].str.contains(search, case=False) |
            filtered["account_id"].str.contains(search, case=False)
        ]
    if status_filter != "All":
        filtered = filtered[filtered["status"] == status_filter]
    if txn_type != "All":
        filtered = filtered[filtered["transaction_type"] == txn_type]
    filtered = filtered[(filtered["amount"] >= min_amt) & (filtered["amount"] <= max_amt)]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Showing", f"{len(filtered):,} transactions")
    c2.metric("Blocked", filtered[filtered["status"] == "Blocked"].shape[0], delta_color="inverse")
    c3.metric("Under Review", filtered[filtered["status"] == "Under Review"].shape[0])
    c4.metric("Total Volume", f"${filtered['amount'].sum():,.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Risk Score vs. Transaction Amount</div>', unsafe_allow_html=True)
    color_map = {"High": "#f87171", "Medium": "#fbbf24", "Low": "#34d399"}
    sample = filtered.sample(min(300, len(filtered)))
    fig = go.Figure()
    for level, color in color_map.items():
        sub = sample[sample["risk_level"] == level]
        fig.add_trace(go.Scatter(
            x=sub["amount"], y=sub["risk_score"],
            mode="markers",
            name=level,
            marker=dict(color=color, size=6, opacity=0.8),
            text=sub["transaction_id"],
            hovertemplate="<b>%{text}</b><br>Amount: $%{x:,.2f}<br>Risk: %{y}<extra></extra>"
        ))
    apply_theme(fig, height=300,
                xaxis=dict(gridcolor="#2d3f55", title="Amount ($)", title_font=dict(color="#cbd5e1"), tickfont=dict(color="#94a3b8")),
                yaxis=dict(gridcolor="#2d3f55", title="Risk Score", title_font=dict(color="#cbd5e1"), tickfont=dict(color="#94a3b8")),
                legend=dict(orientation="h", y=1.1, font=dict(color="#e2e8f0")))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Transaction Log</div>', unsafe_allow_html=True)

    display = filtered[[
        "transaction_id", "timestamp", "account_id", "merchant",
        "transaction_type", "amount", "country", "card_type",
        "risk_score", "risk_level", "velocity_flag", "geo_mismatch", "status"
    ]].copy()

    display["timestamp"] = pd.to_datetime(display["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
    display["amount"] = display["amount"].apply(lambda x: f"${x:,.2f}")
    display["velocity_flag"] = display["velocity_flag"].map({True: "⚠️ Yes", False: "No"})
    display["geo_mismatch"] = display["geo_mismatch"].map({True: "⚠️ Yes", False: "No"})
    display.columns = [
        "Txn ID", "Time", "Account", "Merchant", "Type",
        "Amount", "Country", "Card", "Risk Score", "Risk Level",
        "Velocity Flag", "Geo Mismatch", "Status"
    ]

    st.dataframe(
        display.head(100),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Risk Score": st.column_config.ProgressColumn(
                "Risk Score", min_value=0, max_value=100, format="%d"
            )
        }
    )

    if len(filtered) > 100:
        st.caption(f"Showing first 100 of {len(filtered):,} results.")

    csv = filtered.to_csv(index=False)
    st.download_button("⬇️ Export to CSV", csv, "transactions.csv", "text/csv")