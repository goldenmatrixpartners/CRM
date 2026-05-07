import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(page_title='Strategy Analysis', layout='wide')

st.markdown('''
    <style>
    html, body, .stApp { background-color: #ffffff; color: #111827; }
    .stApp { padding: 2rem 2.5rem; }
    .page-title { font-size: 2.1rem; font-weight: 800; margin-bottom: 0.15rem; }
    .page-subtitle { color: #6b7280; margin-bottom: 1.5rem; }
    .metric-card {
        background: #fffaf0;
        border: 1px solid rgba(212,175,55,0.35);
        border-radius: 18px;
        padding: 1rem 1.25rem;
        min-height: 120px;
    }
    .metric-label { color: #6b7280; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.04em; }
    .metric-value { color: #b8860b; font-size: 1.9rem; font-weight: 800; }
    .metric-note  { color: #4b5563; font-size: 0.9rem; margin-top: 0.35rem; }
    </style>
''', unsafe_allow_html=True)

@st.cache_data
def load_strategy_data():
    sample = {
        'Trade ID': range(201, 221),
        'Entry Timestamp': [
            '2026-03-20 09:15','2026-03-20 14:40','2026-03-21 08:10','2026-03-21 17:25',
            '2026-03-22 10:05','2026-03-22 15:50','2026-03-23 11:30','2026-03-23 18:10',
            '2026-03-24 09:55','2026-03-24 13:45','2026-03-25 10:20','2026-03-25 16:15',
            '2026-03-26 08:50','2026-03-26 14:05','2026-03-27 11:05','2026-03-27 17:40',
            '2026-03-28 09:20','2026-03-28 15:10','2026-03-29 12:25','2026-03-29 18:35',
        ],
        'Exit Timestamp': [
            '2026-03-20 13:30','2026-03-20 20:10','2026-03-21 13:20','2026-03-22 01:05',
            '2026-03-22 14:25','2026-03-22 21:40','2026-03-23 14:00','2026-03-24 00:20',
            '2026-03-24 12:15','2026-03-24 18:35','2026-03-25 12:05','2026-03-25 21:10',
            '2026-03-26 12:30','2026-03-26 19:15','2026-03-27 14:20','2026-03-28 02:05',
            '2026-03-28 12:45','2026-03-28 20:30','2026-03-29 16:40','2026-03-30 01:25',
        ],
        'Symbol': ['XAU/USD'] * 20,
        'Strategy': ['RR3','GoldLong'] * 10,
        'Timeframe':['2H','3H','4H','2H','3H','4H','2H','4H','3H','2H',
                     '4H','3H','2H','4H','3H','2H','4H','3H','2H','4H'],
        'Direction':['Long','Long','Short','Long','Short','Long','Long','Short',
                     'Long','Short','Long','Long','Short','Long','Long','Short',
                     'Long','Long','Short','Long'],
        'PnL ($)':  [820,450,-280,720,-175,980,320,-240,310,270,
                     910,560,-310,740,650,-190,430,1020,-290,680],
    }
    df = pd.DataFrame(sample)
    df['Entry Timestamp'] = pd.to_datetime(df['Entry Timestamp'])
    df['Exit Timestamp']  = pd.to_datetime(df['Exit Timestamp'])
    df['Duration Hours']  = (df['Exit Timestamp'] - df['Entry Timestamp']).dt.total_seconds() / 3600
    df['Hour']            = df['Entry Timestamp'].dt.hour
    return df

data = load_strategy_data()

st.markdown('<div class="page-title">Strategy Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Executive view of strategy performance, hourly edge, and the metrics that matter.</div>', unsafe_allow_html=True)

today = datetime.now().date()
inner_cols = st.columns([2, 1])
selected_strategy = inner_cols[0].selectbox('Select strategy', options=['All Strategies', 'RR3', 'GoldLong'])
date_range = inner_cols[1].date_input('Date Range', value=(today - timedelta(days=30), today), max_value=today)

start_date, end_date = (date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (date_range, date_range))

filtered = data[(data['Entry Timestamp'].dt.date >= start_date) & (data['Entry Timestamp'].dt.date <= end_date)].copy()
if selected_strategy != 'All Strategies':
    filtered = filtered[filtered['Strategy'] == selected_strategy]

def best_win_streak(series):
    max_s = cur = 0
    for v in series:
        cur = cur + 1 if v > 0 else 0
        max_s = max(max_s, cur)
    return max_s

avg_duration  = filtered['Duration Hours'].mean() if len(filtered) else 0
best_streak   = best_win_streak(filtered['PnL ($)'])
gross_profit  = filtered.loc[filtered['PnL ($)'] > 0, 'PnL ($)'].sum()
gross_loss    = -filtered.loc[filtered['PnL ($)'] < 0, 'PnL ($)'].sum()
profit_factor = gross_profit / gross_loss if gross_loss else float('nan')

ma, mb, mc = st.columns(3)
for col, label, value, note in [
    (ma, 'Avg Trade Duration', str(round(avg_duration,1))+'h', 'Based on entry and exit timestamps.'),
    (mb, 'Best Winning Streak', str(best_streak)+' trades', 'Longest consecutive profitable trades.'),
    (mc, 'Profit Factor', str(round(profit_factor, 2)), 'Gross profits divided by gross losses.'),
]:
    col.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )

strategy_stats = data.groupby('Strategy').agg(win_rate=('PnL ($)', lambda x: (x > 0).mean())).reset_index()

win_rate_chart = (
    alt.Chart(strategy_stats).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X('Strategy:N'),
        y=alt.Y('win_rate:Q', axis=alt.Axis(format='.0%', title='Win Rate')),
        color=alt.Color('Strategy:N', scale=alt.Scale(range=['#b8860b', '#f0c674'])),
        tooltip=[alt.Tooltip('Strategy:N'), alt.Tooltip('win_rate:Q', format='.1%')],
    ).properties(height=320)
)

cum_pl_df = filtered.sort_values('Entry Timestamp').assign(CumulativePnL=lambda d: d['PnL ($)'].cufsum())
cum_pl_chart = (
    alt.Chart(cum_pl_df).mark_line(color='#b8860b', strokeWidth=3)
    .encode(
        x=alt.X('Entry Timestamp:T', title='Entry Date'),
        y=alt.Y('CumulativePnL:Q', title='Cumulative PnL'),
        tooltip=[alt.Tooltip('Entry Timestamp:T'), alt.Tooltip('CumulativePnL:Q', format=',.0f')],
    ).properties(height=320)
)

hourly_df = (filtered.groupby('Hour').agg(
    total_pnl=('PnL ($)', 'sum'), trade_count=('Trade ID', 'count'),
    win_rate=('PnL ($)', lambda x: (x > 0).mean())).reset_index())

hourly_chart = (
    alt.Chart(hourly_df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X('Hour:O', title='Hour of Day'),
        y=alt.Y('total_pnl:Q', title='Profit by Hour'),
        color=alt.condition(alt.datum.total_pnl > 0, alt.value('#22c55e'), alt.value('#ef4444')),
        tooltip=[alt.Tooltip('Hour:O'), alt.Tooltip('total_pnl:Q', format=',.0f'),
                 alt.Tooltip('trade_count:Q'), alt.Tooltip('win_rate:Q', format='.0%')],
    ).properties(height=320)
)

st.markdown('### Performance Visuals')
c1, c2 = st.columns(2)
with c1:
    st.markdown('**Win Rate by Strategy**')
    st.altair_chart(win_rate_chart, use_container_width=True)
with c2:
    st.markdown('**Cumulative PnL Over Time**')
    st.altair_chart(cum_pl_chart, use_container_width=True)

st.markdown('### Time-of-Day Edge')
st.altair_chart(hourly_chart, use_container_width=True)
