import streamlit as st

st.set_page_config(
    page_title="FraudShield | Detection Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f1923;
        border-right: 1px solid #1e3048;
    }
    [data-testid="stSidebar"] * {
        color: #c8d8e8 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #c8d8e8 !important;
        font-size: 0.9rem;
    }

    /* Main background */
    .main {
        background-color: #f4f6f9;
    }

    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 20px 24px;
        border-left: 4px solid #1a56db;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .metric-card.danger { border-left-color: #e02424; }
    .metric-card.warning { border-left-color: #e3a008; }
    .metric-card.success { border-left-color: #057a55; }
    .metric-card h3 { font-size: 0.78rem; color: #6b7280; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; margin: 0 0 8px 0; }
    .metric-card .value { font-size: 2rem; font-weight: 700; color: #111827; margin: 0; font-family: 'IBM Plex Mono', monospace; }
    .metric-card .delta { font-size: 0.8rem; margin-top: 4px; color: #6b7280; }
    .metric-card .delta.up { color: #e02424; }
    .metric-card .delta.down { color: #057a55; }

    /* Section headers */
    .section-title {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #374151;
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Alert badges */
    .badge-high { background: #fde8e8; color: #c81e1e; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .badge-medium { background: #fdf6b2; color: #9f580a; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .badge-low { background: #def7ec; color: #03543f; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }

    /* Hide default streamlit branding */
    #MainMenu, footer { visibility: hidden; }

    /* Dataframe */
    [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

    /* Tabs */
    .stTabs [data-baseweb="tab"] { font-size: 0.88rem; font-weight: 500; }

    /* Buttons */
    .stButton button {
        background-color: #1a56db;
        color: white;
        border: none;
        border-radius: 6px;
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 500;
    }
    .stButton button:hover { background-color: #1e429f; }

    /* Sidebar logo area */
    .sidebar-logo {
        padding: 8px 0 24px 0;
        border-bottom: 1px solid #1e3048;
        margin-bottom: 20px;
    }
    .sidebar-logo h2 {
        color: white !important;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.02em;
    }
    .sidebar-logo span {
        color: #3b82f6 !important;
    }
    .sidebar-subtitle {
        color: #64748b !important;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h2>🛡️ Fraud<span>Shield</span></h2>
        <div class="sidebar-subtitle">Detection & Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**NAVIGATION**")
    page = st.radio(
        "",
        ["📊  Overview", "🔍  Transaction Monitor", "🤖  ML Detection", "⚠️  Alert Center", "📈  Analytics"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**FILTERS**")
    date_range = st.selectbox("Time Period", ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last Quarter"])
    risk_filter = st.multiselect("Risk Level", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
    st.markdown("---")
    st.caption("FraudShield v2.1.0 · Last sync: 2 min ago")

# Route pages
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
