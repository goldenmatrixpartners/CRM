import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Todo List | GMP", layout="wide")

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
.stButton > button { background: linear-gradient(135deg, #d4af37 0%, #b8952a 100%) !important; color: #0a0a0a !important; border: none !important; border-radius: 6px !important; font-weight: 700 !important; font-size: 1rem !important; }
.stButton > button:hover { background: linear-gradient(135deg, #f0cc50 0%, #d4af37 100%) !important; box-shadow: 0 4px 15px rgba(212,175,55,0.4) !important; }
h1, h2, h3 { color: #d4af37 !important; font-family: 'Cinzel', serif !important; letter-spacing: 2px !important; }
hr { border-color: #d4af37 !important; opacity: 0.3 !important; }
.stDataFrame { border: 1px solid #d4af37 !important; border-radius: 8px !important; }
.stTextInput input, .stSelectbox select, .stDateInput input {
    background-color: #1a1a1a !important; border: 1px solid #d4af37 !important; border-radius: 6px !important; color: #d4af37 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("## GMP")
    st.markdown("---")

st.markdown("# TODO LIST")
st.markdown("##### Task and strategy management")
st.markdown("---")

TODO_FILE = "todos.csv"
TEAM = ["Meytan", "Orel", "Both"]

def load_todos():
    if os.path.exists(TODO_FILE):
        df = pd.read_csv(TODO_FILE)
        for col in ["Task","Category","Priority","Status","Due Date","Assign To"]:
            if col not in df.columns:
                df[col] = ""
        return df
    return pd.DataFrame(columns=["Task","Category","Priority","Status","Due Date","Assign To"])

def save_todos(df):
    df.to_csv(TODO_FILE, index=False)

todos = load_todos()

col1, col2, col3, col4 = st.columns(4)
total = len(todos)
done  = len(todos[todos["Status"] == "Done"]) if not todos.empty else 0
pct   = round(done / total * 100) if total > 0 else 0
high  = len(todos[(todos["Priority"] == "High") & (todos["Status"] != "Done")]) if not todos.empty else 0
col1.metric("Total Tasks", total)
col2.metric("Completed", done)
col3.metric("Completion", f"{pct}%")
col4.metric("High Priority", high)
st.markdown("---")

tab1, tab2 = st.tabs(["All Tasks", "Add Task"])

with tab1:
    if todos.empty:
        st.info("No tasks yet. Click the 'Add Task' tab to create your first task.")
    else:
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        with fcol1:
            sel_status = st.selectbox("Status", ["All","To Do","In Progress","Done"])
        with fcol2:
            sel_priority = st.selectbox("Priority", ["All","High","Medium","Low"])
        with fcol3:
            cats = ["All"] + sorted(todos["Category"].dropna().unique().tolist())
            sel_cat = st.selectbox("Category", cats)
        with fcol4:
            assignees = ["All"] + TEAM
            sel_assignee = st.selectbox("Assign To", assignees)
        filtered = todos.copy()
        if sel_status != "All":   filtered = filtered[filtered["Status"] == sel_status]
        if sel_priority != "All": filtered = filtered[filtered["Priority"] == sel_priority]
        if sel_cat != "All":      filtered = filtered[filtered["Category"] == sel_cat]
        if sel_assignee != "All": filtered = filtered[filtered["Assign To"] == sel_assignee]
        def sp(v):
            if v == "High":   return "color: #cc0000; font-weight: bold"
            if v == "Medium": return "color: #d4af37; font-weight: bold"
            if v == "Low":    return "color: #00cc44; font-weight: bold"
            return ""
        def ss(v):
            if v == "Done":        return "color: #00cc44"
            if v == "In Progress": return "color: #d4af37"
            return ""
        def sa(v):
            if v == "Meytan": return "color: #d4af37; font-weight: bold"
            if v == "Orel":   return "color: #b0c4de; font-weight: bold"
            if v == "Both":   return "color: #9370db; font-weight: bold"
            return ""
        styled = filtered.style.map(sp, subset=["Priority"]).map(ss, subset=["Status"]).map(sa, subset=["Assign To"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("### Add New Task")
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        task_name = st.text_input("Task Name *", placeholder="e.g. Review BTCUSD strategy", key="task_name")
    with r1c2:
        due_date = st.date_input("Due Date", value=date.today(), key="due_date")
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        category = st.selectbox("Category", ["Research","Strategy","Risk Management","Admin","Other"], key="category")
    with r2c2:
        priority = st.selectbox("Priority", ["High","Medium","Low"], key="priority")
    with r2c3:
        status = st.selectbox("Status", ["To Do","In Progress","Done"], key="status")
    with r2c4:
        assignee = st.selectbox("Assign To", TEAM, key="assignee")
    st.markdown("")
    if st.button("+ Add Task", use_container_width=True, type="primary"):
        if task_name.strip():
            new_row = {"Task": task_name, "Category": category, "Priority": priority,
                       "Status": status, "Due Date": str(due_date), "Assign To": assignee}
            todos = pd.concat([todos, pd.DataFrame([new_row])], ignore_index=True)
            save_todos(todos)
            st.success(f"Task '{task_name}' assigned to {assignee}!")
            st.rerun()
        else:
            st.error("Please enter a task name.")
