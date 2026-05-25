import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_generator import generate_transactions

CARD = "#111827"
GRID = "#1e2d3d"

def chart_layout(fig, height=300, **kw):
    fig.update_layout(
        height=height, plot_bgcolor=CARD, paper_bgcolor=CARD,
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(family="Inter", color="#94a3b8", size=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
        **kw
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=GRID, tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8"), zeroline=False)
    fig.update_yaxes(gridcolor=GRID, linecolor=GRID, tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8"), zeroline=False)
    return fig

def render(date_range, risk_filter):
    df = generate_transactions(500, date_range)
    if risk_filter:
        df = df[df["risk_level"].isin(risk_filter)]

    st.markdown("""
    <div class="page-header">
        <h2>🔍 Transaction Monitor</h2>
        <p>Real-time transaction screening, search and investigation tools</p>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([2,1,1,1])
    with col1:
        search = st.text_input("🔎 Search Transaction ID or Account", placeholder="TXN... or ACC...")
    with col2:
        status_filter = st.selectbox("Status", ["All","Blocked","Under Review","Cleared"])
    with col3:
        txn_type = st.selectbox("Type", ["All"]+list(df["transaction_type"].unique()))
    with col4:
        min_amt, max_amt = st.slider("Amount ($)", 0, 50000, (0, 50000), step=100)

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["transaction_id"].str.contains(search, case=False)|
                            filtered["account_id"].str.contains(search, case=False)]
    if status_filter != "All":
        filtered = filtered[filtered["status"]==status_filter]
    if txn_type != "All":
        filtered = filtered[filtered["transaction_type"]==txn_type]
    filtered = filtered[(filtered["amount"]>=min_amt)&(filtered["amount"]<=max_amt)]

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, color in [
        (c1, "Showing",      f"{len(filtered):,} txns",                               "#6366f1"),
        (c2, "Blocked",      str(filtered[filtered["status"]=="Blocked"].shape[0]),    "#ef4444"),
        (c3, "Under Review", str(filtered[filtered["status"]=="Under Review"].shape[0]),"#f59e0b"),
        (c4, "Total Volume", f"${filtered['amount'].sum():,.0f}",                      "#10b981"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-top:3px solid {color};padding:14px 18px;">
                <div class="kpi-label">{label}</div>
                <div style="font-size:1.4rem;font-weight:800;font-family:'JetBrains Mono',monospace;color:#f1f5f9;">{value}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Risk Score vs Transaction Amount</div>', unsafe_allow_html=True)
    color_map = {"High":"#ef4444","Medium":"#f59e0b","Low":"#10b981"}
    sample = filtered.sample(min(300, len(filtered)))
    fig = go.Figure()
    for level, color in color_map.items():
        sub = sample[sample["risk_level"]==level]
        fig.add_trace(go.Scatter(
            x=sub["amount"], y=sub["risk_score"], mode="markers", name=level,
            marker=dict(color=color, size=7, opacity=0.75,
                        line=dict(color="rgba(0,0,0,0.3)", width=1)),
            text=sub["transaction_id"],
            hovertemplate="<b>%{text}</b><br>Amount: $%{x:,.2f}<br>Risk Score: %{y}<extra></extra>"
        ))
    chart_layout(fig, height=300,
                 xaxis=dict(gridcolor=GRID, title="Amount ($)", title_font=dict(color="#94a3b8"), tickfont=dict(color="#64748b")),
                 yaxis=dict(gridcolor=GRID, title="Risk Score", title_font=dict(color="#94a3b8"), tickfont=dict(color="#64748b")),
                 legend=dict(orientation="h", y=1.12, font=dict(color="#94a3b8")))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Transaction Log</div>', unsafe_allow_html=True)
    display = filtered[["transaction_id","timestamp","account_id","merchant",
                         "transaction_type","amount","country","card_type",
                         "risk_score","risk_level","velocity_flag","geo_mismatch","status"]].copy()
    display["timestamp"] = pd.to_datetime(display["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
    display["amount"] = display["amount"].apply(lambda x: f"${x:,.2f}")
    display["velocity_flag"] = display["velocity_flag"].map({True:"⚠️ Yes", False:"—"})
    display["geo_mismatch"]  = display["geo_mismatch"].map({True:"⚠️ Yes", False:"—"})
    display.columns = ["Txn ID","Time","Account","Merchant","Type","Amount",
                        "Country","Card","Risk Score","Risk Level","Velocity","Geo Mismatch","Status"]
    st.dataframe(display.head(100), use_container_width=True, hide_index=True,
                 column_config={"Risk Score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100, format="%d")})
    if len(filtered) > 100:
        st.caption(f"Showing first 100 of {len(filtered):,} results.")
    st.download_button("⬇️ Export CSV", filtered.to_csv(index=False), "transactions.csv", "text/csv")