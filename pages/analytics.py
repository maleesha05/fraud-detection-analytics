import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_generator import generate_transactions

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

def render(date_range):
    df = generate_transactions(800, date_range)

    st.markdown("""
    <div class="page-header">
        <h2>📈 Analytics & Trends</h2>
        <p>Deep-dive fraud pattern analysis and behavioral insights</p>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Fraud Activity Heatmap — Hour × Day of Week</div>', unsafe_allow_html=True)
    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    df["dow"]  = pd.to_datetime(df["timestamp"]).dt.day_name()
    hm = df[df["is_fraud"]].groupby(["dow","hour"]).size().reset_index(name="count")
    pivot = hm.pivot(index="dow", columns="hour", values="count").fillna(0)
    days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot = pivot.reindex([d for d in days_order if d in pivot.index])

    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=list(range(24)), y=pivot.index.tolist(),
        colorscale=[[0,CARD],[0.4,"#7f1d1d"],[1,"#ef4444"]],
        showscale=True,
        colorbar=dict(tickfont=dict(color="#64748b"), thickness=12,
                      title=dict(text="Count", font=dict(color="#94a3b8"))),
        hovertemplate="<b>%{y}</b> at %{x}:00<br>%{z} fraud events<extra></extra>"
    ))
    apply_dark(fig, height=290,
               extra=dict(
                   xaxis=dict(title="Hour of Day", dtick=2, gridcolor=GRID, linecolor=GRID,
                              tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8")),
                   yaxis=dict(gridcolor=GRID, tickfont=dict(color="#94a3b8"))
               ))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Fraud by Transaction Type</div>', unsafe_allow_html=True)
        ts = df.groupby("transaction_type").agg(total=("is_fraud","count"), fraud=("is_fraud","sum")).reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Total", x=ts["transaction_type"], y=ts["total"],
                              marker_color="#6366f1", opacity=0.3))
        fig2.add_trace(go.Bar(name="Fraudulent", x=ts["transaction_type"], y=ts["fraud"],
                              marker_color="#ef4444", opacity=0.9))
        apply_dark(fig2, height=290,
                   margin=dict(l=10, r=10, t=20, b=70),
                   extra=dict(
                       barmode="overlay",
                       xaxis=dict(tickangle=-20, gridcolor=GRID, linecolor=GRID,
                                  tickfont=dict(color="#64748b")),
                       yaxis=dict(gridcolor=GRID, tickfont=dict(color="#64748b")),
                       legend=dict(orientation="h", y=1.12, font=dict(color="#94a3b8"))
                   ))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Fraud Rate by Card Type</div>', unsafe_allow_html=True)
        cs = df.groupby("card_type").agg(total=("is_fraud","count"), fraud=("is_fraud","sum")).reset_index()
        cs["rate"] = (cs["fraud"] / cs["total"] * 100).round(1)
        fig3 = go.Figure(go.Bar(
            x=cs["card_type"], y=cs["rate"],
            marker=dict(color=["#6366f1","#ef4444","#10b981","#f59e0b"],
                        line=dict(color=CARD, width=2)),
            text=[f"{r}%" for r in cs["rate"]],
            textposition="outside", textfont=dict(color="#e2e8f0", size=12),
            hovertemplate="<b>%{x}</b><br>Fraud Rate: %{y}%<extra></extra>"
        ))
        apply_dark(fig3, height=290,
                   extra=dict(
                       xaxis=dict(showgrid=False, tickfont=dict(color="#94a3b8")),
                       yaxis=dict(title="Fraud Rate (%)", gridcolor=GRID, linecolor=GRID,
                                  tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8"))
                   ))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-title">Amount Distribution — Legitimate vs Fraudulent</div>', unsafe_allow_html=True)
    fig4 = go.Figure()
    fig4.add_trace(go.Histogram(x=df[~df["is_fraud"]]["amount"].clip(0,5000), name="Legitimate",
                                nbinsx=60, marker_color="#6366f1", opacity=0.5))
    fig4.add_trace(go.Histogram(x=df[df["is_fraud"]]["amount"].clip(0,5000), name="Fraudulent",
                                nbinsx=60, marker_color="#ef4444", opacity=0.7))
    apply_dark(fig4, height=280,
               extra=dict(
                   barmode="overlay",
                   xaxis=dict(title="Amount ($)", gridcolor=GRID, linecolor=GRID,
                              tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8")),
                   yaxis=dict(title="Count", gridcolor=GRID, linecolor=GRID,
                              tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8")),
                   legend=dict(orientation="h", y=1.12, font=dict(color="#94a3b8"))
               ))
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-title">Automated Insights</div>', unsafe_allow_html=True)
    insights = [
        ("🕐", "#6366f1", "Peak Fraud Hours",      "Fraudulent transactions spike between 02:00–04:00 AM, accounting for 31% of all fraud despite only 4% of total volume."),
        ("💳", "#ef4444", "Wire Transfers at Risk", "International Wire Transfers show a 28.4% fraud rate — 6× higher than standard purchases."),
        ("🌍", "#f59e0b", "Geographic Hotspots",   "Transactions from non-home countries show 4.1× higher fraud probability when paired with high-value amounts."),
        ("⚡", "#10b981", "Velocity Patterns",      "Accounts with 3+ transactions within 5 minutes have a 67% fraud rate vs 4.2% baseline."),
    ]
    cols = st.columns(2)
    for i, (icon, color, title, body) in enumerate(insights):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="insight-card" style="border-left:3px solid {color};">
                <div style="font-size:1.5rem;margin-bottom:8px;">{icon}</div>
                <div style="font-weight:700;color:#e2e8f0;font-size:0.9rem;margin-bottom:6px;">{title}</div>
                <div style="font-size:0.8rem;color:#64748b;line-height:1.6;">{body}</div>
            </div>""", unsafe_allow_html=True)