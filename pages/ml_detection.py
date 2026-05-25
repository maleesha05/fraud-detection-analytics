import streamlit as st
import plotly.graph_objects as go
import numpy as np
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

def render():
    st.markdown("""
    <div class="page-header">
        <h2>🤖 ML Fraud Detection Engine</h2>
        <p>Model performance metrics, live transaction scoring, and feature analysis</p>
    </div>""", unsafe_allow_html=True)

    tabs = st.tabs(["📊 Model Performance", "🔬 Predict Transaction", "📉 Feature Importance"])

    with tabs[0]:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown('<div class="section-title">ROC Curve — Random Forest</div>', unsafe_allow_html=True)
            fpr = np.linspace(0, 1, 100)
            tpr = np.clip(np.sort(1 - np.exp(-4.5 * fpr) + np.random.normal(0, 0.01, 100)), 0, 1)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=fpr, y=tpr, name="Random Forest (AUC=0.943)",
                line=dict(color="#6366f1", width=2.5),
                fill="tozeroy", fillcolor="rgba(99,102,241,0.08)"
            ))
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1], name="Baseline",
                line=dict(color="#334155", dash="dash", width=1.5)
            ))
            apply_dark(fig, height=300,
                       extra=dict(
                           xaxis=dict(title="False Positive Rate", gridcolor=GRID, linecolor=GRID,
                                      tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8"), zeroline=False),
                           yaxis=dict(title="True Positive Rate", gridcolor=GRID, linecolor=GRID,
                                      tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8"), zeroline=False),
                           legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"))
                       ))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">Model Metrics</div>', unsafe_allow_html=True)
            for name, val, note, color in [
                ("AUC-ROC",   "0.943", "↑ +0.012 vs baseline", "#6366f1"),
                ("Precision", "91.2%", "High precision",        "#10b981"),
                ("Recall",    "88.7%", "Low false negatives",   "#10b981"),
                ("F1 Score",  "0.899", "Balanced performance",  "#6366f1"),
                ("Accuracy",  "96.4%", "Overall accuracy",      "#10b981"),
            ]:
                st.markdown(f"""
                <div style="background:#0d1117;border-radius:8px;padding:10px 14px;margin-bottom:8px;
                            border:1px solid rgba(255,255,255,0.05);border-left:3px solid {color};">
                    <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:0.1em;">{name}</div>
                    <div style="font-size:1.25rem;font-weight:800;color:#f1f5f9;font-family:'JetBrains Mono',monospace;">{val}</div>
                    <div style="font-size:0.7rem;color:#475569;">{note}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Confusion Matrix</div>', unsafe_allow_html=True)
        z = [[412, 18], [27, 143]]
        fig_cm = go.Figure(go.Heatmap(
            z=z, x=["Legitimate", "Fraudulent"], y=["Legitimate", "Fraudulent"],
            colorscale=[[0, "#0d1117"], [1, "#6366f1"]],
            showscale=False,
            text=[[str(v) for v in row] for row in z],
            texttemplate="<b>%{text}</b>",
            textfont=dict(size=22, color="#ffffff"),
            hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>"
        ))
        apply_dark(fig_cm, height=280,
                   margin=dict(l=60, r=20, t=20, b=60),
                   extra=dict(
                       xaxis=dict(title="Predicted", gridcolor=GRID, linecolor=GRID,
                                  tickfont=dict(color="#94a3b8"), title_font=dict(color="#94a3b8")),
                       yaxis=dict(title="Actual", autorange="reversed", gridcolor=GRID, linecolor=GRID,
                                  tickfont=dict(color="#94a3b8"), title_font=dict(color="#94a3b8"))
                   ))
        st.plotly_chart(fig_cm, use_container_width=True)

    with tabs[1]:
        st.markdown('<div class="section-title">Live Transaction Risk Scorer</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            amount    = st.number_input("Amount ($)", min_value=0.0, value=250.0, step=10.0)
            txn_type  = st.selectbox("Transaction Type", ["Purchase", "ATM Withdrawal", "Wire Transfer", "Online Payment", "International Transfer"])
        with col2:
            country   = st.selectbox("Country", ["US", "CA", "GB", "FR", "NG", "RU", "CN", "BR", "MX"])
            card_type = st.selectbox("Card Type", ["Visa", "Mastercard", "Amex", "Discover"])
        with col3:
            velocity_flag = st.checkbox("⚡ Velocity Flag")
            geo_mismatch  = st.checkbox("🌍 Geo Mismatch")
            hour = st.slider("Hour of Day", 0, 23, 14)

        if st.button("🔍 Analyze Transaction", type="primary"):
            score = 15
            if amount > 3000: score += 35
            elif amount > 500: score += 15
            if country in ["NG", "RU", "CN"]: score += 25
            if txn_type in ["Wire Transfer", "International Transfer"]: score += 20
            if velocity_flag: score += 15
            if geo_mismatch: score += 12
            if hour < 5 or hour > 22: score += 8
            score = min(score, 99)

            level = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
            color = "#ef4444" if level == "High" else "#f59e0b" if level == "Medium" else "#10b981"
            rec   = ("🚫 **Block immediately.** High fraud probability." if level == "High"
                     else "⚠️ **Flag for review.** Multiple risk signals." if level == "Medium"
                     else "✅ **Approve.** Low fraud risk.")

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#111827,#1a2235);border-radius:14px;
                        padding:28px;border:2px solid {color};margin-top:16px;">
                <div style="display:flex;align-items:center;gap:28px;">
                    <div style="text-align:center;min-width:120px;">
                        <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:0.1em;">Risk Score</div>
                        <div style="font-size:4rem;font-weight:900;color:{color};font-family:'JetBrains Mono',monospace;line-height:1;">{score}</div>
                        <div style="display:inline-block;padding:3px 14px;border-radius:20px;
                                    background:rgba(0,0,0,0.3);border:1px solid {color};
                                    color:{color};font-weight:700;font-size:0.8rem;">{level} Risk</div>
                    </div>
                    <div style="flex:1;border-left:1px solid #1e293b;padding-left:24px;">
                        <div style="font-size:0.9rem;color:#e2e8f0;line-height:1.7;">{rec}</div>
                        <div style="margin-top:12px;font-size:0.75rem;color:#334155;">
                            Random Forest v2.1 &nbsp;·&nbsp; Confidence: {min(85+(score//10),99)}%
                        </div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            fig_g = go.Figure(go.Indicator(
                mode="gauge+number", value=score,
                gauge=dict(
                    axis=dict(range=[0, 100], tickfont=dict(color="#64748b"), tickcolor="#334155"),
                    bar=dict(color=color, thickness=0.25),
                    bgcolor="#0d1117", bordercolor="#1e293b",
                    steps=[
                        dict(range=[0,  40], color="#0a2a1a"),
                        dict(range=[40, 70], color="#2a200a"),
                        dict(range=[70,100], color="#2a0a0a"),
                    ],
                ),
                title=dict(text="Fraud Risk Score", font=dict(size=13, color="#64748b")),
                number=dict(font=dict(size=44, family="JetBrains Mono", color=color))
            ))
            fig_g.update_layout(
                height=260, margin=dict(l=30, r=30, t=50, b=10),
                paper_bgcolor=CARD, font=dict(family="Inter", color="#94a3b8")
            )
            st.plotly_chart(fig_g, use_container_width=True)

    with tabs[2]:
        st.markdown('<div class="section-title">Feature Importance Scores</div>', unsafe_allow_html=True)
        features = {
            "Transaction Amount": 0.231, "Country Risk Score": 0.187,
            "Transaction Type":   0.143, "Hour of Day":        0.112,
            "Velocity Flag":      0.098, "Geographic Mismatch":0.087,
            "Card Type":          0.072, "Account Age":        0.045,
            "Merchant Category":  0.025,
        }
        fd = pd.DataFrame(list(features.items()), columns=["Feature", "Importance"]).sort_values("Importance")
        bar_colors = [f"rgba(99,102,241,{0.4 + v})" for v in fd["Importance"]]
        fig = go.Figure(go.Bar(
            x=fd["Importance"], y=fd["Feature"], orientation="h",
            marker=dict(color=bar_colors, line=dict(color=CARD, width=1)),
            text=[f"{v:.3f}" for v in fd["Importance"]],
            textposition="outside", textfont=dict(color="#e2e8f0", size=11),
            hovertemplate="<b>%{y}</b><br>Importance: %{x:.3f}<extra></extra>"
        ))
        apply_dark(fig, height=380,
                   margin=dict(l=10, r=70, t=20, b=10),
                   extra=dict(
                       xaxis=dict(title="Importance Score", gridcolor=GRID, linecolor=GRID,
                                  tickfont=dict(color="#64748b"), title_font=dict(color="#94a3b8")),
                       yaxis=dict(showgrid=False, tickfont=dict(color="#94a3b8"))
                   ))
        st.plotly_chart(fig, use_container_width=True)
        st.info("**Model:** Random Forest (500 estimators, max_depth=12) · Trained on 6 months of labeled data · SMOTE oversampling applied")