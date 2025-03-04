import streamlit as st
import mysql.connector
import pandas as pd
import time

# **Database Connection**
def connect_db():
    try:
        return mysql.connector.connect(
            host="127.0.0.1",
            user="Joslep101",
            password="JoslepRESORT*1001",
            database="tracom-proj-db"
        )
    except mysql.connector.Error as err:
        st.error(f"Database Connection Failed: {err}")
        return None


# **Fetch Scan Logs**
@st.cache_data(ttl=5)  # Auto-refresh every 5 seconds
def fetch_scan_logs():
    conn = connect_db()
    if not conn:
        return pd.DataFrame()

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name, rank, unit FROM scan_logs ORDER BY scan_time DESC")  # Latest first
    logs = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(logs)

    if not df.empty:
        df.insert(0, "No.", range(len(df), 0, -1))  # Numbering in descending order
        df = df.rename(columns={"name": "Full Name", "rank": "Rank", "unit": "Office"})
        df = df.reset_index(drop=True)

    return df


# **Streamlit UI**
st.set_page_config(page_title="Logs", page_icon="images/logo.png", layout="wide")

# **Custom CSS for Styling**
st.markdown("""
    <style>
    .welcome-text {
        text-align: center;
        font-size: 50px;
        font-weight: bold;
        color: black;
    }

    .entry-count {
        text-align: right;
        font-size: 35px;
        font-weight: bold;
        color: black;
    }

    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 24px;
        text-align: center;
    }

    .styled-table th, .styled-table td {
        padding: 12px;
        border: 1px solid black;
    }

    .styled-table th {
        background-color: #f4f4f4;
        font-size: 26px;
        text-align: center;
    }

    .styled-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }

    /* Align Search Box and Clear Button */
    .search-container {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .search-box input {
        width: 200px;
        height: 35px;
        font-size: 16px;
        padding: 5px;
        border: 1px solid #ccc;
        border-radius: 5px;
        text-align: center;
    }

    .clear-btn {
        padding: 8px 12px;
        background-color: red;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }

    .clear-btn:hover {
        background-color: darkred;
    }
    </style>
""", unsafe_allow_html=True)

# **Title & Divider**
st.markdown("<h1 class='welcome-text' style='font-size: 70px;'>🎉 Welcome</h1>", unsafe_allow_html=True)

# **Real-time Scan Logs Display**
scan_logs = fetch_scan_logs()
total_entries = len(scan_logs)

# **Display count at the upper right side**
st.markdown(f"<div class='entry-count'>Attendees: {total_entries}</div>", unsafe_allow_html=True)

# **Initialize session state for search**
if "search" not in st.session_state:
    st.session_state.search = ""

# **Define a callback function to clear the search input**
def clear_search():
    st.session_state.search = ""

# **Search Box with Clear Button (Aligned)**
col1, col2 = st.columns([3, 1])  # Adjust column ratio for alignment

with col1:
    search_query = st.text_input(
        "",
        value=st.session_state.search,
        key="search",
        placeholder="🔍 Search Name:",
        label_visibility="collapsed"
    )

with col2:
    st.button("Clear", on_click=clear_search)  # Calls clear_search() when clicked


# **Filter DataFrame Based on Search Query**
filtered_logs = scan_logs[scan_logs["Full Name"].str.contains(st.session_state.search.strip(), case=False, na=False)] if st.session_state.search else scan_logs

# **Convert DataFrame to Styled HTML Table**
if not filtered_logs.empty:
    html_table = filtered_logs.to_html(index=False, classes="styled-table", escape=False)
    st.markdown(html_table, unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align: center; font-size: 22px; color: gray;'>No matching scan logs found.</p>",
                unsafe_allow_html=True)

# **Auto Refresh every 5 seconds**
time.sleep(5)
st.rerun()
