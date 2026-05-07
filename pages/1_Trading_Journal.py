import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Trading Journal | GMP", layout="wide")

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
.stButton > button:hover { background: linear-gradient(135deg, #f0cc50 0%, #d4af37 100%) !important; box-shadow: 0 4px 15px rgba(212,175,55,0.4) !important; }
h1, h2, h3 { color: #d4af37 !important; font-family: 'Cinzel', serif !important; letter-spacing: 2px !important; }
hr { border-color: #d4af37 !important; opacity: 0.3 !important; }
.stDataFrame { border: 1px solid #d4af37 !important; border-radius: 8px !important; }
.stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input, .stTextArea textarea {
    background-color: #1a1a1a !important; border: 1px solid #d4af37 !important; border-radius: 6px !important; color: #d4af37 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("## GMP")
    st.markdown("---")

st.markdown("# TRADING JOURNAL")
st.markdown("##### Record and analyze your trades")
st.markdown("---")

DATA_FILE = "trading_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    return pd.DataFrame(columns=["Date","Strategy","Symbol","Direction","Entry","Exit","PnL","Notes"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# Tabs
tab1, tab2, tab3 = st.tabs(["All Trades", "Add Trade", "Import / Export"])

# ── Tab 1: All Trades ─────────────────────────────────────────────
with tab1:
    if df.empty:
        st.info("No trades recorded yet. Use the 'Add Trade' tab to get started.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        total_pnl = df["PnL"].sum()
        win_rate = (df["PnL"] > 0).mean() * 100
        col1.metric("Total Trades", len(df))
        col2.metric("Total PnL", f"${total_pnl:,.2f}")
        col3.metric("Win Rate", f"{win_rate:.1f}%")
        col4.metric("Avg PnL", f"${df['PnL'].mean():,.2f}")
        st.markdown("---")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            strategies = ["All"] + sorted(df["Strategy"].dropna().unique().tolist())
            strat_filter = st.selectbox("Strategy", strategies)
        with col_f2:
            directions = ["All"] + sorted(df["Direction"].dropna().unique().tolist())
            dir_filter = st.selectbox("Direction", directions)
        with col_f3:
            symbols = ["All"] + sorted(df["Symbol"].dropna().unique().tolist())
            sym_filter = st.selectbox("Symbol", symbols)
        filtered = df.copy()
        if strat_filter != "All":
            filtered = filtered[filtered["Strategy"] == strat_filter]
        if dir_filter != "All":
            filtered = filtered[filtered["Direction"] == dir_filter]
        if sym_filter != "All":
            filtered = filtered[filtered["Symbol"] == sym_filter]
        def color_pnl(val):
            if isinstance(val, (int, float)):
                color = "#00cc44" if val > 0 else "#cc0000" if val < 0 else "#d4af37"
                return f"color: {color}; font-weight: bold"
            return ""
        styled = filtered.style.map(color_pnl, subset=["PnL"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

# ── Tab 2: Add Trade ─────────────────────────────────────────────
with tab2:
    st.markdown("### Add New Trade")
    with st.form("add_trade_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            trade_date = st.date_input("Date", value=datetime.today())
            strategy = st.text_input("Strategy", placeholder="e.g. Breakout, Trend Following")
            symbol = st.text_input("Symbol", placeholder="e.g. BTCUSD, EURUSD")
        with col2:
            direction = st.selectbox("Direction", ["Long", "Short"])
            entry = st.number_input("Entry Price", min_value=0.0, format="%.4f")
            exit_price = st.number_input("Exit Price", min_value=0.0, format="%.4f")
        pnl = st.number_input("PnL ($)", format="%.2f", help="Profit or loss in dollars")
        notes = st.text_area("Notes", placeholder="Optional trade notes...")
        submitted = st.form_submit_button("Add Trade")
        if submitted:
            new_row = {
                "Date": str(trade_date),
                "Strategy": strategy,
                "Symbol": symbol,
                "Direction": direction,
                "Entry": entry,
                "Exit": exit_price,
                "PnL": pnl,
                "Notes": notes
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("Trade added successfully!")
            st.rerun()

# ── Tab 3: Import / Export ────────────────────────────────────────
with tab3:
    st.markdown("### Import Data")
    uploaded = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded is not None:
        try:
            imported = pd.read_csv(uploaded)
            st.dataframe(imported.head(10), use_container_width=True)
            if st.button("Import this data"):
                imported.to_csv(DATA_FILE, index=False)
                st.success(f"Imported {len(imported)} rows successfully!")
                st.rerun()
        except Exception as e:
            st.error(f"Error reading file: {e}")
    st.markdown("---")
    st.markdown("### Export Data")
    if not df.empty:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download trades as CSV",
            data=csv_data,
            file_name="trading_journal.csv",
            mime="text/csv"
        )
        st.markdown(f"**{len(df)}** trades available for export")
    else:
        st.info("No data to export yet.")
    st.markdown("---")
    st.markdown("### CSV Format")
    sample = pd.DataFrame([{"Date":"2025-01-15","Strategy":"Breakout","Symbol":"BTCUSD",
                             "Direction":"Long","Entry":42000,"Exit":43500,"PnL":1500,"Notes":"Strong breakout"}])
    st.dataframe(sample, use_container_width=True)
