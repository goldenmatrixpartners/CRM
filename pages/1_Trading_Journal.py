import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title='Trading Journal', layout='wide')

st.markdown('''
    <style>
    html, body, .stApp { background-color: #ffffff; color: #1f2937; }
    .stApp { padding: 2rem 2.5rem; }
    .page-title { font-size: 2rem; font-weight: 700; margin-bottom: 0.15rem; }
    .page-subtitle { color: #6b7280; margin-top: 0; margin-bottom: 1.75rem; }
    .summary-card {
        background: #fffdf7;
        border: 1px solid rgba(212,175,55,0.25);
        border-radius: 18px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
    }
    .summary-label { color: #6b7280; font-size: 0.85rem; margin-bottom: 0.25rem; }
    .summary-value { color: #b8860b; font-size: 1.55rem; font-weight: 700; }
    .stButton>button { background-color: #d4af37; color: #111827; border: none; }
    </style>
''', unsafe_allow_html=True)

@st.cache_data
def load_trade_data():
    sample = {
        'Trade ID': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'Timestamp': ['2026-03-25 10:00', '2026-03-26 14:00', '2026-03-28 12:30',
                      '2026-04-01 16:00', '2026-04-03 08:00', '2026-04-05 18:00',
                      '2026-04-07 10:00', '2026-04-09 12:00', '2026-04-10 09:00', '2026-04-11 15:00'],
        'Symbol':        ['XAU/USD'] * 10,
        'Strategy':      ['RR3', 'GoldLong'] * 5,
        'Timeframe':     ['2H', '3H', '4H', '2H', '3H', '4H', '2H', '4H', '3H', '2H'],
        'Direction':     ['Long', 'Long', 'Short', 'Long', 'Short', 'Long', 'Long', 'Short', 'Long', 'Short'],
        'Entry Price':   [2025.5, 2031.0, 2029.2, 2035.8, 2030.4, 2040.7, 2032.1, 2044.3, 2039.0, 2036.5],
        'Exit Price':    [2032.0, 2036.5, 2018.0, 2042.0, 2024.0, 2052.5, 2037.0, 2040.0, 2045.3, 2034.2],
        'Position Size': [0.75, 0.5, 0.8, 0.6, 0.7, 0.55, 0.65, 0.4, 0.6, 0.5],
        'PnL ($)':       [950, 450, -320, 710, -180, 1120, 500, -200, 340, 260],
        'Status':        ['Win', 'Win', 'Loss', 'Win', 'Loss', 'Win', 'Win', 'Loss', 'Win', 'Win'],
    }
    df = pd.DataFrame(sample)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

trade_data = load_trade_data()
today = datetime.now().date()
default_start = today - timedelta(days=30)

top_row = st.columns([4, 1])
with top_row[0]:
    st.markdown('<div class="page-title">Trading Journal</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Spreadsheet-style trade journal with instant filtering and live metrics.</div>', unsafe_allow_html=True)
with top_row[1]:
    date_range = st.date_input('Date Range', value=(default_start, today), max_value=today)

strategy_options  = sorted(trade_data['Strategy'].unique())
timeframe_options = sorted(trade_data['Timeframe'].unique())
filter_bar = st.columns(2)
strategy_selected  = filter_bar[0].multiselect('Strategy',  options=strategy_options,  default=strategy_options)
timeframe_selected = filter_bar[1].multiselect('Timeframe', options=timeframe_options, default=timeframe_options)

start_date, end_date = (date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (date_range, date_range))

filtered_data = trade_data[
    (trade_data['Timestamp'].dt.date >= start_date) &
    (trade_data['Timestamp'].dt.date <= end_date) &
    trade_data['Strategy'].isin(strategy_selected) &
    trade_data['Timeframe'].isin(timeframe_selected)
]

total_pnl = filtered_data['PnL ($)'].sum()
win_rate  = (filtered_data['PnL ($)'] > 0).mean() if len(filtered_data) else 0

m1, m2 = st.columns(2)
with m1:
    st.markdown(f'<div class="summary-card"><div class="summary-label">Total PnL</div><div class="summary-value">${total_pnl:,.0f}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="summary-card"><div class="summary-label">Win Rate</div><div class="summary-value">{win_rate:.0%}</div></div>', unsafe_allow_html=True)

st.markdown('### Trading Journal')
display_columns = ['Trade ID', 'Timestamp', 'Symbol', 'Strategy', 'Direction',
                   'Entry Price', 'Exit Price', 'Position Size', 'PnL ($)', 'Status']
journal_df = (filtered_data[display_columns]
              .sort_values('Timestamp', ascending=False)
              .reset_index(drop=True))

def pnl_color(val):
    if val > 0: return 'color: green; font-weight: 700;'
    if val < 0: return 'color: red; font-weight: 700;'
    return 'color: #1f2937;'

styled_journal = journal_df.style.map(pnl_color, subset=['PnL ($)'])
st.dataframe(styled_journal, use_container_width=True)
