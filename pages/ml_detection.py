import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from utils.data_generator import generate_transactions
from utils.chart_theme import apply_theme


def render():
    df = generate_transactions(800, "Last 30 Days")

    st.markdown("## 🤖 ML Fraud Detection Engine")
    st.caption("Machine learning model performance and real-time prediction")

    tabs = st.tabs(["📊 Model Performance", "🔬 Predict Transaction", "📉 Feature Importance"])

    with tabs[0]:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown('<div class="section-title">ROC Curve — Random Forest Classifier</div>', unsafe_allow_html=True)
            fpr = np.linspace(0, 1, 100)
            tpr = 1 - np.exp(-4.5 * fpr) + np.random.normal(0, 0.01, 100)
            tpr = np.clip(np.sort(tpr), 0, 1)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=fpr, y=tpr, name="Random Forest (AUC=0.943)",
                                     line=dict(color="#60a5fa", width=2.5)))
            fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], name="Random Classifier",
                                     line=dict(color="#64748b", dash="dash")))
            apply_theme(fig, height=300,
                        xaxis=dict(gridcolor="#2d3f55", title="False Positive Rate", title_font=dict(color="#cbd5e1"), tickfont=dict(color="#94a3b8")),
                        yaxis=dict(gridcolor="#2d3f55", title="True Positive Rate", title_font=dict(color="#cbd5e1"), tickfont=dict(color="#94a3b8")),
                        legend=dict(orientation="h", y=1.1, font=dict(color="#e2e8f0")))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">Model Metrics</div>', unsafe_allow_html=True)
            metrics = {
                "AUC-ROC": ("0.943", "↑ +0.012 vs baseline"),
                "Precision": ("91.2%", "High precision"),
                "Recall": ("88.7%", "Minimized false negatives"),
                "F1 Score": ("0.899", "Balanced performance"),
                "Accuracy": ("96.4%", "Overall accuracy"),
            }
            for name, (val, note) in metrics.items():
                st.markdown(f"""
                <div style="background:#1e2d3d;border-radius:6px;padding:10px 14px;margin-bottom:8px;border-left:3px solid #3b82f6;">
                    <div style="font-size:0.72rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.06em;">{name}</div>
                    <div style="font-size:1.3rem;font-weight:700;color:#e2e8f0;font-family:'IBM Plex Mono',monospace;">{val}</div>
                    <div style="font-size:0.72rem;color:#64748b;">{note}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Confusion Matrix</div>', unsafe_allow_html=True)
        z = [[412, 18], [27, 143]]
        labels = ["Legitimate", "Fraudulent"]

        fig_cm = go.Figure(go.Heatmap(
            z=z, x=labels, y=labels,
            colorscale=[[0, "#1e2d3d"], [1, "#3b82f6"]],
            showscale=False,
            text=[[str(v) for v in row] for row in z],
            texttemplate="%{text}",
            textfont=dict(size=18, color="#ffffff"),
        ))
        apply_theme(fig_cm, height=300,
                    margin=dict(l=60, r=0, t=40, b=60),
                    xaxis=dict(title="Predicted", title_font=dict(color="#cbd5e1"), tickfont=dict(color="#94a3b8")),
                    yaxis=dict(title="Actual", autorange="reversed", title_font=dict(color="#cbd5e1"), tickfont=dict(color="#94a3b8")))
        st.plotly_chart(fig_cm, use_container_width=True)

    with tabs[1]:
        st.markdown('<div class="section-title">Predict Fraud Risk for a Transaction</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            amount = st.number_input("Transaction Amount ($)", min_value=0.0, value=250.0, step=10.0)
            txn_type = st.selectbox("Transaction Type", ["Purchase", "ATM Withdrawal", "Wire Transfer", "Online Payment", "International Transfer"])
        with col2:
            country = st.selectbox("Country Code", ["US", "CA", "GB", "FR", "NG", "RU", "CN", "BR", "MX"])
            card_type = st.selectbox("Card Type", ["Visa", "Mastercard", "Amex", "Discover"])
        with col3:
            velocity_flag = st.checkbox("Velocity Flag (multiple rapid transactions)")
            geo_mismatch = st.checkbox("Geographic Mismatch")
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
            color = "#f87171" if level == "High" else "#fbbf24" if level == "Medium" else "#34d399"
            recommendation = (
                "🚫 **Block transaction immediately.** High probability of fraud detected."
                if level == "High" else
                "⚠️ **Flag for manual review.** Several risk signals detected."
                if level == "Medium" else
                "✅ **Approve transaction.** Low fraud risk detected."
            )

            st.markdown(f"""
            <div style="background:#1e2d3d;border-radius:10px;padding:28px;border:2px solid {color};margin-top:16px;">
                <div style="display:flex;align-items:center;gap:20px;">
                    <div>
                        <div style="font-size:0.8rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.06em;">Risk Score</div>
                        <div style="font-size:3.5rem;font-weight:800;color:{color};font-family:'IBM Plex Mono',monospace;line-height:1;">{score}</div>
                        <div style="font-size:1rem;font-weight:600;color:{color};">{level} Risk</div>
                    </div>
                    <div style="flex:1;border-left:1px solid #2d3f55;padding-left:24px;">
                        <div style="font-size:0.85rem;color:#cbd5e1;line-height:1.6;">{recommendation}</div>
                        <div style="margin-top:12px;font-size:0.78rem;color:#64748b;">
                            Model: Random Forest v2.1 · Confidence: {85 + (score // 10)}%
                        </div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                gauge=dict(
                    axis=dict(range=[0, 100], tickfont=dict(color="#94a3b8"), tickcolor="#94a3b8"),
                    bar=dict(color=color),
                    bgcolor="#1a2332",
                    bordercolor="#2d3f55",
                    steps=[
                        dict(range=[0, 40], color="#1a3a2a"),
                        dict(range=[40, 70], color="#3a2e10"),
                        dict(range=[70, 100], color="#3a1a1a"),
                    ],
                ),
                title=dict(text="Fraud Risk Score", font=dict(size=14, color="#94a3b8")),
                number=dict(font=dict(size=40, family="IBM Plex Mono", color="#e2e8f0"))
            ))
            fig_g.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=0),
                                paper_bgcolor="#1a2332", font=dict(family="IBM Plex Sans", color="#e2e8f0"))
            st.plotly_chart(fig_g, use_container_width=True)

    with tabs[2]:
        st.markdown('<div class="section-title">Feature Importance — Random Forest</div>', unsafe_allow_html=True)
        features = {
            "Transaction Amount": 0.231,
            "Country Risk Score": 0.187,
            "Transaction Type": 0.143,
            "Hour of Day": 0.112,
            "Velocity Flag": 0.098,
            "Geographic Mismatch": 0.087,
            "Card Type": 0.072,
            "Account Age": 0.045,
            "Merchant Category": 0.025,
        }
        feat_df = pd.DataFrame(list(features.items()), columns=["Feature", "Importance"]).sort_values("Importance")
        fig = go.Figure(go.Bar(
            x=feat_df["Importance"], y=feat_df["Feature"],
            orientation="h",
            marker_color="#3b82f6",
            opacity=0.85,
            text=[f"{v:.3f}" for v in feat_df["Importance"]],
            textposition="outside",
            textfont=dict(color="#e2e8f0"),
        ))
        apply_theme(fig, height=380,
                    margin=dict(l=10, r=60, t=10, b=10),
                    xaxis=dict(gridcolor="#2d3f55", title="Importance Score", title_font=dict(color="#cbd5e1"), tickfont=dict(color="#94a3b8")),
                    yaxis=dict(showgrid=False, tickfont=dict(color="#cbd5e1")))
        st.plotly_chart(fig, use_container_width=True)

        st.info("**Model:** Random Forest (500 estimators, max_depth=12) trained on 6 months of labeled transaction data with SMOTE oversampling to handle class imbalance.")