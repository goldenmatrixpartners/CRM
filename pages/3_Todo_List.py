import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title='To-Do List', layout='wide')

st.markdown('''
    <style>
    html, body, .stApp { background-color: #ffffff; color: #111827; }
    .stApp { padding: 2rem 2.5rem; }
    .page-title  { font-size: 2rem; font-weight: 800; margin-bottom: 0.25rem; }
    .page-subtitle { color: #6b7280; margin-bottom: 1.5rem; }
    .stButton>button { background-color: #d4af37; color: #111827; border: none; }
    div[data-baseweb='popover'], div[data-baseweb='menu'] {
        background-color: #ffffff !important; color: #000000 !important;
    }
    div[data-baseweb='menu'] [role='option'] {
        background-color: #ffffff !important; color: #000000 !important;
    }
    div[data-baseweb='menu'] [role='option']:hover {
        background-color: #f3f4f6 !important;
    }
    </style>
''', unsafe_allow_html=True)

if 'todo_items' not in st.session_state:
    st.session_state.todo_items = pd.DataFrame([
        {'Done': False, 'Task Name': 'Review strategy deck',
         'Description': 'Finalize the RR3 analysis notes.',
         'Assigned To': 'Orel', 'Due Date': date.today()},
        {'Done': False, 'Task Name': 'Check server health',
         'Description': 'Verify main node connections and latency.',
         'Assigned To': 'Meytan', 'Due Date': date.today() + pd.Timedelta(days=2)},
    ])

st.markdown('<div class="page-title">Shared To-Do List</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">A collaborative task board for Orel and Meytan.</div>', unsafe_allow_html=True)

b1, b2 = st.columns(2)
add_new      = b1.button('Add New Task')
save_changes = b2.button('Save Changes')

if add_new:
    new_row = pd.DataFrame([{
        'Done': False, 'Task Name': '', 'Description': '',
        'Assigned To': 'Orel', 'Due Date': date.today(),
    }])
    st.session_state.todo_items = pd.concat([st.session_state.todo_items, new_row], ignore_index=True)

column_config = {
    'Done':        st.column_config.CheckboxColumn('Done'),
    'Task Name':   st.column_config.TextColumn('Task Name'),
    'Description': st.column_config.TextColumn('Description'),
    'Assigned To': st.column_config.SelectboxColumn('Assigned To', options=['Orel', 'Meytan']),
    'Due Date':    st.column_config.DateColumn('Due Date'),
}

edited = st.data_editor(
    st.session_state.todo_items,
    column_config=column_config,
    use_container_width=True,
    num_rows='dynamic',
    hide_index=True,
    key='todo_data_editor',
)
st.session_state.todo_items = edited.copy()

if save_changes:
    st.success('Task list saved successfully.')

completed = int(edited['Done'].sum())
if completed:
    st.success(f'{completed} completed task({"s" if completed != 1 else ""}) -- great progress!')
