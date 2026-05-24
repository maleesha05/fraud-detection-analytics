import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data_generator import generate_transactions, get_summary_stats
from utils.chart_theme import apply_theme

def render(date_range, risk_filter):
    df = generate_transactions(500, date_range)
    if risk_filter:
        df_filtered = df[df["risk_level"].isin(risk_filter)]
    else:
        df_filtered = df

    stats = get_summary_stats(df_filtered)

    st.markdown("## 📊 Fraud Detection Overview")
    st.caption(f"Showing data for **{date_range}** · {stats['total_transactions']:,} transactions analyzed")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card danger">
            <h3>Fraud Rate</h3>
            <div class="value">{stats['fraud_rate']}%</div>
            <div class="delta up">▲ +0.3% vs prior period</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card warning">
            <h3>Flagged Transactions</h3>
            <div class="value">{stats['flagged_transactions']:,}</div>
            <div class="delta">of {stats['total_transactions']:,} total</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card danger">
            <h3>Fraud Amount</h3>
            <div class="value">${stats['fraud_amount']:,.0f}</div>
            <div class="delta up">{stats['fraud_amount_pct']}% of total volume</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card success">
            <h3>Avg Risk Score</h3>
            <div class="value">{stats['avg_risk_score']}</div>
            <div class="delta down">▼ -2.1 vs prior period</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="section-title">Transaction Volume & Fraud Trend</div>', unsafe_allow_html=True)
        df_filtered["date"] = pd.to_datetime(df_filtered["timestamp"]).dt.date
        daily = df_filtered.groupby("date").agg(
            total=("amount", "count"),
            fraud=("is_fraud", "sum")
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=daily["date"], y=daily["total"],
            name="Total Transactions",
            marker_color="#3b82f6", opacity=0.7
        ))
        fig.add_trace(go.Scatter(
            x=daily["date"], y=daily["fraud"],
            name="Fraudulent",
            line=dict(color="#f87171", width=2.5),
            mode="lines+markers",
            marker=dict(size=5)
        ))
        apply_theme(fig, height=280,
                    xaxis=dict(gridcolor="#2d3f55", linecolor="#2d3f55", tickfont=dict(color="#94a3b8")),
                    yaxis=dict(gridcolor="#2d3f55", linecolor="#2d3f55", tickfont=dict(color="#94a3b8")),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color="#e2e8f0")))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Risk Distribution</div>', unsafe_allow_html=True)
        risk_counts = df_filtered["risk_level"].value_counts()
        fig2 = go.Figure(go.Pie(
            labels=risk_counts.index,
            values=risk_counts.values,
            hole=0.62,
            marker_colors=["#f87171", "#fbbf24", "#34d399"],
            textinfo="percent",
            textfont=dict(size=13, color="#ffffff"),
        ))
        apply_theme(fig2, height=280,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15, font=dict(color="#e2e8f0")),
                    annotations=[dict(text=f"<b>{stats['flagged_transactions']}</b><br>Flagged",
                                      x=0.5, y=0.5, font=dict(size=14, color="#e2e8f0"), showarrow=False)])
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns([1, 1])

    with col3:
        st.markdown('<div class="section-title">Top Fraud Merchants</div>', unsafe_allow_html=True)
        fraud_merchants = (
            df_filtered[df_filtered["is_fraud"]]
            .groupby("merchant")["amount"].sum()
            .sort_values(ascending=True)
            .tail(8)
        )
        fig3 = go.Figure(go.Bar(
            x=fraud_merchants.values,
            y=fraud_merchants.index,
            orientation="h",
            marker_color="#f87171",
            opacity=0.85,
        ))
        apply_theme(fig3, height=280,
                    xaxis=dict(gridcolor="#2d3f55", title="Fraud Amount ($)", title_font=dict(color="#cbd5e1"), tickfont=dict(color="#94a3b8")),
                    yaxis=dict(showgrid=False, tickfont=dict(color="#cbd5e1")))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">Fraud by Country</div>', unsafe_allow_html=True)
        country_fraud = df_filtered[df_filtered["is_fraud"]].groupby("country").size().reset_index(name="count")
        fig4 = px.choropleth(
            country_fraud, locations="country",
            color="count",
            color_continuous_scale=["#2d3f55", "#f87171"],
            locationmode="ISO-3",
        )
        fig4.update_layout(
            height=280, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="#1a2332",
            geo=dict(showframe=False, showcoastlines=True, bgcolor="#1a2332",
                     landcolor="#2d3f55", oceancolor="#1a2332", showocean=True,
                     coastlinecolor="#4a5568"),
            coloraxis_showscale=False,
            font=dict(family="IBM Plex Sans", color="#e2e8f0"),
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-title">Recent High-Risk Transactions</div>', unsafe_allow_html=True)
    recent_high = df_filtered[df_filtered["risk_level"] == "High"].head(8)[[
        "transaction_id", "timestamp", "merchant", "amount", "country", "risk_score", "status"
    ]].copy()
    recent_high["timestamp"] = pd.to_datetime(recent_high["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
    recent_high["amount"] = recent_high["amount"].apply(lambda x: f"${x:,.2f}")
    recent_high.columns = ["Transaction ID", "Time", "Merchant", "Amount", "Country", "Risk Score", "Status"]
    st.dataframe(recent_high, use_container_width=True, hide_index=True)