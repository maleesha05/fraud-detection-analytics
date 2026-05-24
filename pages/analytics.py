import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.data_generator import generate_transactions
from utils.chart_theme import apply_theme


def render(date_range):
    df = generate_transactions(800, date_range)

    st.markdown("## 📈 Analytics & Trends")
    st.caption("Deep-dive analytics and fraud pattern analysis")

    st.markdown('<div class="section-title">Fraud Activity Heatmap — Hour × Day of Week</div>', unsafe_allow_html=True)
    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    df["dow"] = pd.to_datetime(df["timestamp"]).dt.day_name()

    heatmap_data = df[df["is_fraud"]].groupby(["dow", "hour"]).size().reset_index(name="count")
    pivot = heatmap_data.pivot(index="dow", columns="hour", values="count").fillna(0)
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex([d for d in days_order if d in pivot.index])

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=list(range(24)),
        y=pivot.index.tolist(),
        colorscale=[[0, "#1a2332"], [0.5, "#7f1d1d"], [1, "#f87171"]],
        hoverongaps=False,
        showscale=True,
        colorbar=dict(tickfont=dict(color="#94a3b8"), title=dict(text="Count", font=dict(color="#94a3b8"))),
    ))
    apply_theme(fig, height=280,
                xaxis=dict(gridcolor="#2d3f55", title="Hour of Day", title_font=dict(color="#cbd5e1"), tickfont=dict(color="#94a3b8"), dtick=2),
                yaxis=dict(gridcolor="#2d3f55", tickfont=dict(color="#cbd5e1")))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Fraud by Transaction Type</div>', unsafe_allow_html=True)
        type_stats = df.groupby("transaction_type").agg(
            total=("is_fraud", "count"),
            fraud=("is_fraud", "sum")
        ).reset_index()

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Total", x=type_stats["transaction_type"], y=type_stats["total"],
                              marker_color="#3b82f6", opacity=0.5))
        fig2.add_trace(go.Bar(name="Fraudulent", x=type_stats["transaction_type"], y=type_stats["fraud"],
                              marker_color="#f87171", opacity=0.9))
        apply_theme(fig2, height=280,
                    barmode="overlay",
                    margin=dict(l=10, r=10, t=20, b=70),
                    xaxis=dict(gridcolor="#2d3f55", tickangle=-20, tickfont=dict(color="#94a3b8")),
                    yaxis=dict(gridcolor="#2d3f55", tickfont=dict(color="#94a3b8")),
                    legend=dict(orientation="h", y=1.1, font=dict(color="#e2e8f0")))
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Fraud Rate by Card Type</div>', unsafe_allow_html=True)
        card_stats = df.groupby("card_type").agg(
            total=("is_fraud", "count")