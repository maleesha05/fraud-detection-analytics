import streamlit as st

st.set_page_config(
    page_title="FraudShield | Detection Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a0f1e 100%);
    border-right: 1px solid rgba(99,102,241,0.15);
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }

.main { background: #0a0f1e; }
.block-container { padding-top: 1.5rem !important; }

.kpi-card {
    background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
    border-radius: 16px;
    padding: 22px 24px;
    border: 1px solid rgba(255,255,255,0.06);
    position: relative;
    overflow: hidden;
    margin-bottom: 4px;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}
.kpi-card.indigo::before { background: linear-gradient(90deg, #6366f1, #818cf8); }
.kpi-card.red::before    { background: linear-gradient(90deg, #ef4444, #f87171); }
.kpi-card.amber::before  { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.kpi-card.green::before  { background: linear-gradient(90deg, #10b981, #34d399); }

.kpi-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 2.1rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    color: #f1f5f9;
    line-height: 1;
    margin-bottom: 6px;
}
.kpi-delta { font-size: 0.75rem; color: #64748b; }
.kpi-delta.up   { color: #f87171; }
.kpi-delta.down { color: #34d399; }

.section-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569;
    margin: 28px 0 14px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(99,102,241,0.3), transparent);
}

.page-header {
    background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
    border-radius: 16px;
    padding: 24px 28px;
    border: 1px solid rgba(99,102,241,0.15);
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.page-header h2 { font-size: 1.6rem; font-weight: 800; color: #f1f5f9; margin: 0 0 4px 0; }
.page-header p  { font-size: 0.82rem; color: #64748b; margin: 0; }

.brand-block { padding: 8px 0 24px 0; border-bottom: 1px solid rgba(99,102,241,0.15); margin-bottom: 20px; }
.brand-name  { font-size: 1.25rem; font-weight: 800; color: #f1f5f9 !important; margin: 0; letter-spacing: -0.02em; }
.brand-name span { color: #6366f1 !important; }
.brand-sub   { font-size: 0.65rem; color: #334155 !important; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 2px; }

.stRadio > div { gap: 4px !important; }
.stRadio label { border-radius: 8px !important; padding: 8px 12px !important; transition: all 0.2s; }

.badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.04em; }
.badge-red   { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
.badge-amber { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); }
.badge-green { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.25); }

.alert-card { background: linear-gradient(135deg, #111827, #1a2235); border-radius: 12px; padding: 16px 18px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); }
.alert-card.high   { border-left: 3px solid #ef4444; }
.alert-card.medium { border-left: 3px solid #f59e0b; }

.insight-card { background: linear-gradient(135deg, #111827, #1a2235); border-radius: 12px; padding: 18px; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.05); }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

.stButton button {
    background: linear-gradient(135deg, #6366f1, #818cf8);
    color: white; border: none; border-radius: 8px;
    font-weight: 600; font-family: 'Inter', sans-serif; transition: all 0.2s;
}
.stButton button:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(99,102,241,0.4); }
.stTabs [data-baseweb="tab"] { font-weight: 500; font-size: 0.85rem; }
.stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid rgba(255,255,255,0.06); }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="brand-block">
        <div class="brand-name">🛡️ Fraud<span>Shield</span></div>
        <div class="brand-sub">Detection & Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.65rem;font-weight:700;letter-spacing:0.1em;color:#334155;text-transform:uppercase;margin-bottom:8px;">Navigation</div>', unsafe_allow_html=True)

    page = st.radio("", [
        "📊  Overview",
        "🔍  Transaction Monitor",
        "🤖  ML Detection",
        "⚠️  Alert Center",
        "📈  Analytics"
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div style="font-size:0.65rem;font-weight:700;letter-spacing:0.1em;color:#334155;text-transform:uppercase;margin-bottom:8px;">Filters</div>', unsafe_allow_html=True)
    date_range = st.selectbox("Time Period", ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last Quarter"])
    risk_filter = st.multiselect("Risk Level", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])

    st.markdown("---")
    st.markdown('<div style="font-size:0.7rem;color:#1e293b;">FraudShield v2.1 · <span style="color:#6366f1;">Live</span> · Synced 2m ago</div>', unsafe_allow_html=True)

page_name = page.split("  ")[1]

if page_name == "Overview":
    from pages import overview
    overview.render(date_range, risk_filter)
elif page_name == "Transaction Monitor":
    from pages import transactions
    transactions.render(date_range, risk_filter)
elif page_name == "ML Detection":
    from pages import ml_detection
    ml_detection.render()
elif page_name == "Alert Center":
    from pages import alerts
    alerts.render(risk_filter)
elif page_name == "Analytics":
    from pages import analytics
    analytics.render(date_range)