import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Strategy Analysis | GMP", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Raleway:wght@300;400;600&display=swap');
html, body, [class*="css"] { background-color: #0a0a0a !important; color: #d4af37 !important; font-family: 'Raleway', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0a0a0a 0%, #111111 100%) !important; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d0d0d 0%, #111111 100%) !important; border-right: 1px solid #d4af37 !important; }
section[data-testid="stSidebar"] .stMarkdown p, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span { color: #d4af37 !important; }
[data-testid="metric-container"] { background: linear-gradient(135deg, #111111 0%, #1a1a1a 100%) !important; border: 1px solid #d4af37 !important; border-radius: 8px !important; padding: 16px !important; }
[data-testid="metric-container"] label { color: #9e7e2a !important; font-size: 0.8rem !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #d4af37 !important; font-size: 1.8rem !important; font-weight: 700 !important; }
.stButton > button { background: linear-gradient(135deg, #d4af37 0%, #b8952a 100%) !important; color: #0a0a0a !important; border: none !important; border-radius: 6px !important; font-weight: 600 !important; }
h1, h2, h3 { color: #d4af37 !important; font-family: 'Cinzel', serif !important; letter-spacing: 2px !important; }
hr { border-color: #d4af37 !important; opacity: 0.3 !important; }
.stDataFrame { border: 1px solid #d4af37 !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("## GMP")
    st.markdown("---")

st.markdown("# STRATEGY ANALYSIS")
st.markdown("##### Deep dive into your trading strategies")
st.markdown("---")

DATA_FILE = "trading_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    return pd.DataFrame(columns=["Date","Strategy","Symbol","Direction","Entry","Exit","PnL","Notes"])

df = load_data()

if df.empty:
    st.info("No trading data yet. Please add trades in the Trading Journal first.")
    st.stop()

# ── Filters ──────────────────────────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    strategies = ["All"] + sorted(df["Strategy"].dropna().unique().tolist())
    sel_strategy = st.selectbox("Filter by Strategy", strategies)
with col_f2:
    symbols = ["All"] + sorted(df["Symbol"].dropna().unique().tolist())
    sel_symbol = st.selectbox("Filter by Symbol", symbols)

filtered = df.copy()
if sel_strategy != "All":
    filtered = filtered[filtered["Strategy"] == sel_strategy]
if sel_symbol != "All":
    filtered = filtered[filtered["Symbol"] == sel_symbol]

if filtered.empty:
    st.warning("No data for selected filters.")
    st.stop()

# ── Metrics ───────────────────────────────────────────────────────
total_pnl = filtered["PnL"].sum()
win_rate = (filtered["PnL"] > 0).mean() * 100
avg_pnl = filtered["PnL"].mean()
max_dd = filtered["PnL"].min()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total PnL", f"${total_pnl:,.2f}")
col2.metric("Win Rate", f"{win_rate:.1f}%")
col3.metric("Avg PnL", f"${avg_pnl:,.2f}")
col4.metric("Worst Trade", f"${max_dd:,.2f}")
st.markdown("---")

# ── Charts ────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Cumulative PnL", "Strategy Breakdown", "Win/Loss Distribution"])

GOLD = "#d4af37"
BG   = "#111111"
GRID = "#222222"

def dark_layout(title):
    return dict(
        title=title,
        plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(color=GOLD),
        xaxis=dict(gridcolor=GRID, color=GOLD),
        yaxis=dict(gridcolor=GRID, color=GOLD),
        title_font=dict(color=GOLD, size=16)
    )

with tab1:
    df_sorted = filtered.sort_values("Date")
    df_sorted["Cumulative PnL"] = df_sorted["PnL"].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sorted["Date"], y=df_sorted["Cumulative PnL"],
        mode="lines+markers", name="Cumulative PnL",
        line=dict(color=GOLD, width=2),
        marker=dict(color=GOLD, size=6),
        fill="tozeroy", fillcolor="rgba(212,175,55,0.15)"
    ))
    fig.update_layout(**dark_layout("Cumulative PnL Over Time"))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    if "Strategy" in filtered.columns and filtered["Strategy"].notna().any():
        strat_pnl = filtered.groupby("Strategy")["PnL"].sum().reset_index().sort_values("PnL", ascending=False)
        colors = ["#00cc44" if v >= 0 else "#cc0000" for v in strat_pnl["PnL"]]
        fig2 = go.Figure(go.Bar(
            x=strat_pnl["Strategy"], y=strat_pnl["PnL"],
            marker_color=colors, name="PnL by Strategy"
        ))
        fig2.update_layout(**dark_layout("PnL by Strategy"))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("### Strategy Summary Table")
        summary = filtered.groupby("Strategy")["PnL"].agg(["sum","count","mean","max","min"]).reset_index()
        summary.columns = ["Strategy","Total PnL","Trades","Avg PnL","Best","Worst"]
        st.dataframe(summary.style.format({"Total PnL":"${:.2f}","Avg PnL":"${:.2f}","Best":"${:.2f}","Worst":"${:.2f}"}), use_container_width=True)
    else:
        st.info("No strategy data available.")

with tab3:
    wins   = filtered[filtered["PnL"] > 0]["PnL"]
    losses = filtered[filtered["PnL"] < 0]["PnL"]
    fig3 = go.Figure()
    if not wins.empty:
        fig3.add_trace(go.Histogram(x=wins, name="Wins", marker_color="#00cc44", opacity=0.75, nbinsx=20))
    if not losses.empty:
        fig3.add_trace(go.Histogram(x=losses, name="Losses", marker_color="#cc0000", opacity=0.75, nbinsx=20))
    fig3.update_layout(**dark_layout("Win/Loss Distribution"), barmode="overlay")
    st.plotly_chart(fig3, use_container_width=True)
    col_w, col_l = st.columns(2)
    with col_w:
        st.metric("Avg Win", f"${wins.mean():.2f}" if not wins.empty else "N/A")
        st.metric("Total Wins", len(wins))
    with col_l:
        st.metric("Avg Loss", f"${losses.mean():.2f}" if not losses.empty else "N/A")
        st.metric("Total Losses", len(losses))
