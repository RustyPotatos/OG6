import streamlit as st
import mysql.connector
import re
from datetime import datetime
import webbrowser  # To open scan logs page


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
    cursor.fetchall()  # Clear unread results
    cursor.close()
    conn.close()
    return result


# **Check if Already Scanned Today**
def is_already_scanned_today(afpsn):
    conn = connect_db()
    if not conn:
        return False

    cursor = conn.cursor()
    today_date = datetime.now().strftime("%Y-%m-%d")  # Get today's date
    query = "SELECT COUNT(*) FROM scan_logs WHERE afpsn = %s AND DATE(scan_time) = %s"
    cursor.execute(query, (afpsn, today_date))
    count = cursor.fetchone()[0]  # Get count of scans for today
    cursor.close()
    conn.close()

    return count > 0  # Return True if already scanned today


# **Log Scan Function with Duplicate Check**
def log_scan(afpsn, name, unit, rank, status):
    if status != "Registered":
        return  # Skip logging for unregistered AFPSN

    # **Check if already scanned today**
    if is_already_scanned_today(afpsn):
        st.warning(f"⚠️ Duplicate Scan Detected: AFPSN {afpsn} was already scanned today!")
        return  # **Skip Logging**

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
    st.success(f"✔ Scan Logged for {name} ({afpsn})")


# **Extract AFPSN from QR Code**
def extract_afpsn(scanned_text):
    match = re.search(r"\bAFPSN[:\s]*([A-Za-z0-9-]+)\b", scanned_text, re.IGNORECASE)
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


# **Define clear_manual_input function**
def clear_manual_input():
    st.session_state["manual_afpsn"] = ""  # Reset the input field


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

# **Initialize Session State Variables**
for key in ["qr_detected", "afpsn_to_search", "last_qr_scan", "manual_afpsn"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# **Define a Callback Function to Clear QR Code Scan Input**
def clear_qr_input():
    st.session_state["qr_detected"] = ""  # Clear scanned QR data
    st.session_state["afpsn_to_search"] = ""  # Reset search AFPSN


# **Create two columns for input and details display**
col1, col2 = st.columns([1, 1])

with col1:
    # **QR Scanner Output (Text Input)**
    new_qr_data = st.text_input("📸 Scan QR:", key="qr_detected",
                                help="Press Enter after scanning the QR code.")

    # **Handle QR Scan Input**
    if new_qr_data and new_qr_data != st.session_state["last_qr_scan"]:
        afpsn_from_qr = extract_afpsn(new_qr_data)  # Extract AFPSN
        if afpsn_from_qr:
            st.session_state["afpsn_to_search"] = afpsn_from_qr
            st.session_state["last_qr_scan"] = new_qr_data  # Store last scanned QR

    # **Clear Button Below Scan Output**
    st.button("🧹 Clear Scan", on_click=clear_qr_input)

    # **Manual AFPSN Input**
    manual_afpsn = st.text_input("⌨️ Enter AFPSN Manually:", key="manual_afpsn")

    # **Buttons (Search & Clear) in One Row**
    col_btn1, col_btn2, col_btn3 = st.columns([1, 4, 1])

    with col_btn1:
        st.button("🧹 Clear", on_click=clear_manual_input)

    with col_btn3:
        search_button_clicked = st.button("🔍 Search")

    # **Handle Search Button Click**
    if search_button_clicked and manual_afpsn:
        st.session_state["afpsn_to_search"] = manual_afpsn.strip()

with col2:
    # **If AFPSN is found (QR or Manual)**
    if st.session_state["afpsn_to_search"]:
        afpsn_to_search = st.session_state["afpsn_to_search"]
        name, unit, rank, status = check_afpsn(afpsn_to_search)

        # **Log scan if registered**
        log_scan(afpsn_to_search, name, unit, rank, status)

        # **Display extracted AFPSN details**
        st.subheader("📄Details")
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
