import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

st.set_page_config(page_title="Golden Matrix Partners", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1.5])
with col1:
    st.title("Golden Matrix Partners")
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    else:
        st.markdown("### 📈 GMP")
st.markdown("""
    <style>
    html, body, .stApp { background-color: #000000 !important; color: #f8fafc !important; }
    .stApp { padding: 2rem 2.5rem; }
    .stButton>button { background-color: #d4af37; color: #0b0b0b; border: none; }
    .clock-card { background: linear-gradient(180deg, #fff8e7 0%, #f9f0d7 100%); border: 1px solid #d4af37; border-radius: 18px; padding: 1rem; text-align: center; margin-bottom: 1rem; }
    .clock-title { color: #b8860b; font-weight: 700; }
    .clock-time, .clock-subtitle { color: #111827 !important; }
    .server-term { background-color: #111827; color: #e5e7eb; border-radius: 16px; padding: 1rem 1.1rem; font-family: monospace; margin-bottom: 1rem; }
    .server-term span { color: #fbbf24; }
    </style>
""", unsafe_allow_html=True)

def format_clock(label, tz):
    now = datetime.now(ZoneInfo(tz))
    time_str = now.strftime('%H:%M')
    date_str = now.strftime('%b %d, %Y')
    return '<div class="clock-card"><div class="clock-title">'+label+'</div><div class="clock-time">'+time_str+'</div><div class="clock-subtitle">'+date_str+'</div></div>'

@st.cache_data
def get_trade_data():
    sample = {
        "Trade ID": [101, 102, 103, 104, 105, 106, 107, 108],
        "Timestamp": ["2026-03-25 10:00", "2026-03-26 14:00", "2026-03-28 12:00",
                      "2026-04-01 16:00", "2026-04-03 08:00", "2026-04-05 18:00",
                      "2026-04-07 10:00", "2026-04-09 12:00"],
        "Strategy":  ["RR3", "GoldLong", "RR3", "GoldLong", "RR3", "GoldLong", "RR3", "GoldLong"],
        "Timeframe": ["2H", "3H", "4H", "2H", "3H", "4H", "2H", "4H"],
        "Direction": ["Long", "Long", "Short", "Long", "Short", "Long", "Long", "Short"],
        "Pnl":       [950, 450, -320, 710, -180, 1120, 500, -200],
        "Validation Status": ["Actual", "Theoretical", "Actual", "Theoretical",
                              "Actual", "Theoretical", "Actual", "Actual"],
    }
    df = pd.DataFrame(sample)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

def get_performance_summary(df):
    total_pnl = df["Pnl"].sum()
    wins = (df["Pnl"] > 0).sum()
    trades = len(df)
    win_rate = wins / trades if trades else 0
    gross_profit = df.loc[df["Pnl"] > 0, "Pnl"].sum()
    gross_loss = -df.loc[df["Pnl"] < 0, "Pnl"].sum()
    profit_factor = gross_profit / gross_loss if gross_loss else float("nan")
    equity = df.sort_values("Timestamp")["Pnl"].cumsum().reset_index(drop=True)
    drawdown = equity - equity.cummax()
    return {"total_pnl": total_pnl, "win_rate": win_rate,
            "profit_factor": profit_factor, "equity_curve": equity, "drawdown": drawdown}

top_clocks = st.columns(3)
top_clocks[0].markdown(format_clock("London", "Europe/London"), unsafe_allow_html=True)
top_clocks[1].markdown(format_clock("New York", "America/New_York"), unsafe_allow_html=True)
top_clocks[2].markdown(format_clock("Israel", "Asia/Jerusalem"), unsafe_allow_html=True)

today = datetime.now().date()
date_range = st.sidebar.date_input("Select a date range", value=(today - timedelta(days=30), today))
st.sidebar.markdown("## Server Status")
st.sidebar.markdown('<div class="server-term"><span>Status:</span> Connected<br><span>Servers:</span><br>Main_Node_01</div>', unsafe_allow_html=True)

trade_data = get_trade_data()
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_data = trade_data[(trade_data["Timestamp"].dt.date >= start_date) & (trade_data["Timestamp"].dt.date <= end_date)]
else:
    filtered_data = trade_data

performance = get_performance_summary(filtered_data)

st.markdown("## Executive Summary")
c1, c2, c3 = st.columns(3)
c1.metric("Total PnL (USD)", "$" + str(int(performance["total_pnl"])))
c2.metric("Win Rate", str(round(performance["win_rate"]*100)) + "%")
c3.metric("Profit Factor", str(round(performance["profit_factor"], 2)))

st.markdown("## Strategy Analytics")
perf_by_tf = filtered_data.groupby(["Timeframe", "Strategy"], as_index=False)["Pnl"].sum()
chart = (
    alt.Chart(perf_by_tf).mark_bar()
    .encode(
        x=alt.X("Timeframe:N", sort=["2H", "3H", "4H"]),
        y=alt.Y("Pnl:Q", title="Total PnL"),
        color=alt.Color("Strategy:N", scale=alt.Scale(range=["#b8860b", "#f0c674"])),
        xOffset="Strategy:N",
    ).properties(height=380)
)
st.altair_chart(chart, use_container_width=True)

st.markdown("## Trade Ledger")
st.dataframe(filtered_data.sort_values("Timestamp", ascending=False), use_container_width=True)

st.markdown("## Financial Charts")
colL, colR = st.columns(2)
with colL:
    st.markdown("### Equity Curve")
    st.line_chart(performance["equity_curve"])
with colR:
    st.markdown("### Drawdown")
    st.area_chart(performance["drawdown"])
