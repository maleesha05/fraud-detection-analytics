import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.data_generator import generate_transactions, get_summary_stats

CARD = "#111827"
GRID = "#1e2d3d"

def apply_dark(fig, height=300, margin=None, extra=None):
    m = margin or dict(l=10, r=10, t=20, b=10)
    layout = dict(
        height=height, plot_bgcolor=CARD, paper_bgcolor=CARD,
        margin=m, font=dict(family="Inter", color="#94a3b8", size=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    )
    if extra:
        layout.update(extra)
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor=GRID, linecolor=GRID, zeroline=False,
                     tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8"))
    fig.update_yaxes(gridcolor=GRID, linecolor=GRID, zeroline=False,
                     tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8"))
    return fig

def render(date_range, risk_filter):
    df = generate_transactions(500, date_range)
    df_f = df[df["risk_level"].isin(risk_filter)] if risk_filter else df
    stats = get_summary_stats(df_f)

    st.markdown(f"""
    <div class="page-header">
        <h2>📊 Fraud Detection Overview</h2>
        <p>{date_range} &nbsp;·&nbsp; {stats['total_transactions']:,} transactions analyzed &nbsp;·&nbsp; Risk levels: {', '.join(risk_filter) if risk_filter else 'All'}</p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "red",   "Fraud Rate",          f"{stats['fraud_rate']}%",           "up",   "▲ +0.3% vs prior period"),
        (c2, "amber", "Flagged Transactions", f"{stats['flagged_transactions']:,}", "",     f"of {stats['total_transactions']:,} total"),
        (c3, "red",   "Fraud Amount",         f"${stats['fraud_amount']:,.0f}",    "up",   f"{stats['fraud_amount_pct']}% of total volume"),
        (c4, "green", "Avg Risk Score",       f"{stats['avg_risk_score']}",        "down", "▼ -2.1 vs prior period"),
    ]
    for col, color, label, value, delta_cls, delta_text in cards:
        with col:
            st.markdown(f"""
            <div class="kpi-card {color}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-delta {delta_cls}">{delta_text}</div>
            </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="section-title">Transaction Volume & Fraud Trend</div>', unsafe_allow_html=True)
        df_f["date"] = pd.to_datetime(df_f["timestamp"]).dt.date
        daily = df_f.groupby("date").agg(total=("amount","count"), fraud=("is_fraud","sum")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=daily["date"], y=daily["total"], name="Total",
                             marker=dict(color="#6366f1", opacity=0.35),
                             hovertemplate="%{y} txns<extra>Total</extra>"))
        fig.add_trace(go.Scatter(x=daily["date"], y=daily["fraud"], name="Fraudulent",
                                 line=dict(color="#ef4444", width=2.5), mode="lines+markers",
                                 marker=dict(size=5, color="#ef4444"),
                                 hovertemplate="%{y} fraud<extra></extra>"))
        apply_dark(fig, height=290,
                   extra=dict(legend=dict(orientation="h", y=1.12, x=0,
                                          bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"))))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Risk Distribution</div>', unsafe_allow_html=True)
        rc = df_f["risk_level"].value_counts()
        fig2 = go.Figure(go.Pie(
            labels=rc.index, values=rc.values, hole=0.65,
            marker=dict(colors=["#ef4444","#f59e0b","#10b981"],
                        line=dict(color=CARD, width=3)),
            textinfo="percent", textfont=dict(size=12, color="#ffffff"),
        ))
        apply_dark(fig2, height=290,
                   extra=dict(
                       showlegend=True,
                       legend=dict(orientation="h", y=-0.1, font=dict(color="#94a3b8")),
                       annotations=[dict(text=f"<b>{stats['flagged_transactions']}</b><br>Flagged",
                                         x=0.5, y=0.5, font=dict(size=14, color="#e2e8f0"), showarrow=False)]
                   ))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title">Top Fraud Merchants</div>', unsafe_allow_html=True)
        fm = df_f[df_f["is_fraud"]].groupby("merchant")["amount"].sum().sort_values(ascending=True).tail(8)
        fig3 = go.Figure(go.Bar(
            x=fm.values, y=fm.index, orientation="h",
            marker=dict(color=fm.values, colorscale=[[0,"#7f1d1d"],[1,"#ef4444"]], showscale=False),
            hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>"
        ))
        apply_dark(fig3, height=290,
                   extra=dict(
                       xaxis=dict(title="Fraud Amount ($)", gridcolor=GRID, linecolor=GRID,
                                  tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8")),
                       yaxis=dict(showgrid=False, tickfont=dict(color="#94a3b8"))
                   ))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">Fraud by Country</div>', unsafe_allow_html=True)
        cf = df_f[df_f["is_fraud"]].groupby("country").size().reset_index(name="count")
        fig4 = px.choropleth(cf, locations="country", color="count",
                             color_continuous_scale=["#1a2332","#ef4444"], locationmode="ISO-3")
        fig4.update_layout(
            height=290, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor=CARD,
            geo=dict(showframe=False, bgcolor=CARD, landcolor="#1e293b",
                     oceancolor=CARD, showocean=True, coastlinecolor="#334155", showcoastlines=True),
            coloraxis_showscale=False,
            font=dict(color="#94a3b8")
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-title">Recent High-Risk Transactions</div>', unsafe_allow_html=True)
    rh = df_f[df_f["risk_level"]=="High"].head(8)[["transaction_id","timestamp","merchant","amount","country","risk_score","status"]].copy()
    rh["timestamp"] = pd.to_datetime(rh["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
    rh["amount"] = rh["amount"].apply(lambda x: f"${x:,.2f}")
    rh.columns = ["Transaction ID","Time","Merchant","Amount","Country","Risk Score","Status"]
    st.dataframe(rh, use_container_width=True, hide_index=True)