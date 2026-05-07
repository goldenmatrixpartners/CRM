import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Golden Matrix Partners",
    page_icon="logo.png" if os.path.exists("logo.png") else "star",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GMP Black & Gold CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Raleway:wght@300;400;600&display=swap');
html, body, [class*="css"] {
    background-color: #0a0a0a !important;
    color: #d4af37 !important;
    font-family: 'Raleway', sans-serif !important;
}
.stApp { background: linear-gradient(135deg, #0a0a0a 0%, #111111 100%) !important; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d0d 0%, #111111 100%) !important;
    border-right: 1px solid #d4af37 !important;
}
section[data-testid="stSidebar"] .stMarkdown p, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span { color: #d4af37 !important; }
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #111111 0%, #1a1a1a 100%) !important;
    border: 1px solid #d4af37 !important;
    border-radius: 8px !important;
    padding: 16px !important;
}
[data-testid="metric-container"] label { color: #9e7e2a !important; font-size: 0.8rem !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #d4af37 !important; font-size: 1.8rem !important; font-weight: 700 !important; }
.stButton > button {
    background: linear-gradient(135deg, #d4af37 0%, #b8952a 100%) !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}
.stButton > button:hover { background: linear-gradient(135deg, #f0cc50 0%, #d4af37 100%) !important; box-shadow: 0 4px 15px rgba(212,175,55,0.4) !important; }
h1, h2, h3 { color: #d4af37 !important; font-family: 'Cinzel', serif !important; letter-spacing: 2px !important; }
h1 { text-shadow: 0 0 20px rgba(212,175,55,0.3) !important; }
hr { border-color: #d4af37 !important; opacity: 0.3 !important; }
.stDataFrame { border: 1px solid #d4af37 !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("## GOLDEN MATRIX PARTNERS")
    st.markdown("---")

# Header
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
with col_title:
    st.markdown("# GOLDEN MATRIX PARTNERS")
    st.markdown("##### Algorithmic Trading Management System")
st.markdown("---")

# Data
DATA_FILE = "trading_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=["Date"])
    return pd.DataFrame(columns=["Date","Strategy","Symbol","Direction","Entry","Exit","PnL","Notes"])

df = load_data()
st.markdown("## DASHBOARD OVERVIEW")

if df.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", "0")
    col2.metric("Total PnL", "$0.00")
    col3.metric("Win Rate", "0%")
    col4.metric("Best Trade", "$0.00")
    st.info("No trading data yet. Go to Trading Journal to add trades.")
else:
    total_pnl = df["PnL"].sum()
    win_rate = (df["PnL"] > 0).mean() * 100
    best_trade = df["PnL"].max()
    total_trades = len(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", total_trades)
    col2.metric("Total PnL", f"${total_pnl:,.2f}")
    col3.metric("Win Rate", f"{win_rate:.1f}%")
    col4.metric("Best Trade", f"${best_trade:,.2f}")
    st.markdown("---")
    import plotly.graph_objects as go
    df_sorted = df.sort_values("Date")
    df_sorted["Cumulative PnL"] = df_sorted["PnL"].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sorted["Date"], y=df_sorted["Cumulative PnL"],
        mode="lines+markers", name="Cumulative PnL",
        line=dict(color="#d4af37", width=2),
        marker=dict(color="#d4af37", size=6),
        fill="tozeroy", fillcolor="rgba(212,175,55,0.15)"
    ))
    fig.update_layout(
        title="Cumulative PnL Over Time",
        plot_bgcolor="#111111", paper_bgcolor="#111111",
        font=dict(color="#d4af37"),
        xaxis=dict(gridcolor="#222222", color="#d4af37"),
        yaxis=dict(gridcolor="#222222", color="#d4af37")
    )
    st.plotly_chart(fig, use_container_width=True)
    if "Strategy" in df.columns and df["Strategy"].notna().any():
        st.markdown("### Strategy Performance")
        strat_df = df.groupby("Strategy")["PnL"].agg(["sum","count","mean"]).reset_index()
        strat_df.columns = ["Strategy","Total PnL","Trades","Avg PnL"]
        strat_df = strat_df.sort_values("Total PnL", ascending=False)
        st.dataframe(strat_df.style.format({"Total PnL":"${:.2f}","Avg PnL":"${:.2f}"}), use_container_width=True)

st.markdown("---")
st.markdown("<p style='text-align:center;color:#9e7e2a;font-size:0.8rem;'>2025 Golden Matrix Partners</p>", unsafe_allow_html=True)
