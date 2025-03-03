import streamlit as st
import mysql.connector
import re
from datetime import datetime
import time
import webbrowser  # To open scan_logs page


# **Database Connection**
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="Joslep101",
            password="JoslepRESORT*1001",
            database="tracom-proj-db"
        )
    except mysql.connector.Error as err:
        st.error(f"Database Connection Failed: {err}")
        return None


# **Fetch Attendee Details**
def fetch_attendee_details(afpsn):
    conn = connect_db()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM attendees WHERE afpsn = %s", (afpsn,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


# **Log Scan Function**
def log_scan(afpsn, name, unit, rank, status):
    if status != "Registered":
        return  # Skip logging for unregistered AFPSN

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()
    query = "INSERT INTO scan_logs (afpsn, name, unit, rank, scan_time, status) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (afpsn, name, unit, rank, timestamp, status))
    conn.commit()
    cursor.close()
    conn.close()


# **Extract AFPSN from QR Code**
def extract_afpsn(scanned_text):
    match = re.search(r"AFPSN[:\s]+([A-Za-z0-9-]+)", scanned_text, re.IGNORECASE)
    return match.group(1).strip() if match else None


# **Check AFPSN**
def check_afpsn(afpsn):
    attendee = fetch_attendee_details(afpsn)

    if attendee:
        return attendee['name'], attendee['unit'], attendee['rank'], "Registered"
    else:
        return "N/A", "N/A", "N/A", "Not Registered"


# **Clear Inputs Callback**
def clear_inputs():
    st.session_state["qr_detected"] = ""  # Clear scanned QR code data
    st.session_state["manual_afpsn"] = ""  # Clear manual input
    st.session_state["afpsn_to_search"] = ""  # Reset AFPSN to search


# **Streamlit UI**
st.set_page_config(
    page_title="QR Code Scanner",
    page_icon="images/logo.png",
    layout="wide"
)

st.markdown("<h1 style='text-align: center; color: black;'>QR Code Scanner System</h1>", unsafe_allow_html=True)
st.divider()

# **QR Code Scanning Section**
st.subheader("🔍 QR Code Scanner")

# **Initialize Session State for QR Detection**
if "qr_detected" not in st.session_state:
    st.session_state["qr_detected"] = ""

if "afpsn_to_search" not in st.session_state:
    st.session_state["afpsn_to_search"] = ""

if "last_qr_scan" not in st.session_state:
    st.session_state["last_qr_scan"] = ""

if "manual_afpsn" not in st.session_state:
    st.session_state["manual_afpsn"] = ""

# **Define a Callback Function to Clear QR Code Scan Input**
def clear_qr_input():
    st.session_state["qr_detected"] = ""  # Clear scanned QR data
    st.session_state["afpsn_to_search"] = ""  # Reset search AFPSN

# **QR Scanner Output (Text Area)**
new_qr_data = st.text_area("📸 Scan QR:", key="qr_detected",
                           help="This field updates automatically when a QR code is scanned.")

# **Clear Button Below Scan Output**
st.button("🧹 Clear Scan", on_click=clear_qr_input)


# **Detect Change and Auto-Search**
if st.session_state["qr_detected"] and st.session_state["qr_detected"] != st.session_state["last_qr_scan"]:
    extracted_afpsn = extract_afpsn(st.session_state["qr_detected"])

    if extracted_afpsn:
        st.session_state["afpsn_to_search"] = extracted_afpsn
        st.session_state["last_qr_scan"] = st.session_state["qr_detected"]  # Store last scanned value
        time.sleep(1)  # Small delay to prevent race conditions
        st.rerun()  # **Auto-refresh to trigger search**

# **Manual AFPSN Input & Search Button**
manual_afpsn = st.text_input("⌨️ Enter AFPSN Manually:", key="manual_afpsn")
search_button_clicked = st.button("🔍 Search")

if search_button_clicked and manual_afpsn:
    st.session_state["afpsn_to_search"] = manual_afpsn.strip()

# **If AFPSN is found (QR or Manual)**
if st.session_state["afpsn_to_search"]:
    afpsn_to_search = st.session_state["afpsn_to_search"]
    name, unit, rank, status = check_afpsn(afpsn_to_search)

    # Log scan if registered
    log_scan(afpsn_to_search, name, unit, rank, status)

    # Display extracted AFPSN details
    st.write(f"**AFPSN:** {afpsn_to_search}")
    st.write(f"**Name:** {name}")
    st.write(f"**Unit:** {unit}")
    st.write(f"**Rank:** {rank}")

    if status == "Registered":
        st.success("✔ Registered")
    else:
        st.error("❌ Not Registered")

    # **Clear input after verification**
    st.button("✅ Done", on_click=clear_inputs)  # Button to clear inputs

st.divider()

# **Open Scan Logs in New Tab**
st.subheader("📜 Logs")
scan_logs_url = "http://localhost:8502"  # Update with the actual URL if needed

if st.button("📂 Attendees"):
    webbrowser.open_new_tab(scan_logs_url)
st.info("Click the button to view attendees.")
