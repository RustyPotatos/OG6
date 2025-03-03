import mysql.connector
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import re


# Database Connection Test
def test_db_connection():
    """Check if the database connection is working."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="Joslep101",
            password="JoslepRESORT*1001",
            database="tracom-proj-db"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # Test Query
        conn.close()
        print("✅ Successfully connected to the database!")
    except mysql.connector.Error as err:
        print(f"❌ Database Connection Failed: {err}")
        lbl_status.config(text="⚠ Database Error", fg="orange")


# Fetch Attendee Details
def fetch_attendee_details(afpsn):
    """Fetch attendee details from the database using the scanned AFPSN."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="Joslep101",
            password="JoslepRESORT*1001",
            database="tracom-proj-db"
        )
        cursor = conn.cursor(dictionary=True)

        print(f"🔍 Querying AFPSN: '{afpsn}'")  # Debugging
        query = "SELECT * FROM attendees WHERE afpsn = %s"
        cursor.execute(query, (afpsn,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        print(f"Database Result: {result}")  # Debugging
        return result

    except mysql.connector.Error as err:
        print(f"❌ Database Query Error: {err}")
        lbl_status.config(text="⚠ Database Error", fg="orange")
        return None


# Log Scan Function
def log_scan(afpsn, name, unit, rank, status):
    """Log scanned or searched AFPSN with timestamp, but only if registered."""
    if status != "Registered":
        print(f"❌ Not logging unregistered AFPSN: {afpsn}")
        return  # Do not log if the attendee is not registered

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="Joslep101",
            password="JoslepRESORT*1001",
            database="tracom-proj-db"
        )
        cursor = conn.cursor()

        # Insert scan record into 'scan_logs' table only if registered
        query = """
        INSERT INTO scan_logs (afpsn, name, unit, rank, scan_time, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (afpsn, name, unit, rank, timestamp, status))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Scan Logged in Database: {afpsn} at {timestamp} - Status: {status}")

    except mysql.connector.Error as err:
        print(f"❌ Database Insert Error: {err}")
        lbl_status.config(text="⚠ Error Logging Scan", fg="orange")

    # Also log in a text file (for backup)
    with open("scan_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} - Name: {name}, Unit: {unit}, Rank: {rank}, Status: {status}\n")

    # Update Last Scanned Label
    lbl_last_scanned.config(text=f"Last Checked: {afpsn} ({status})", fg="blue")

    # Insert scanned data into the table for display
    table.insert("", "end", values=(name, unit, rank, status))


# Extract AFPSN from Scanned Text
def extract_afpsn(scanned_text):
    """Extract AFPSN using flexible regex."""
    match = re.search(r"AFPSN:\s*([A-Za-z0-9-]+)", scanned_text, re.IGNORECASE)
    return match.group(1).strip() if match else None


# **QR Code Auto-Detect Function**
def on_qr_scanned(*args):
    """Detect when AFPSN is scanned and process it automatically."""
    raw_afpsn = entry_afpsn.get().strip()

    if not raw_afpsn:
        return  # Ignore empty scans

    print(f"Scanned AFPSN Raw Data: '{raw_afpsn}'")  # Debugging Output

    scanned_afpsn = extract_afpsn(raw_afpsn)

    if not scanned_afpsn:
        lbl_status.config(text="⚠ Invalid QR Data", fg="orange")
        return

    check_afpsn(scanned_afpsn)  # Process scanned AFPSN

    # Clear input field after scanning
    entry_afpsn.delete(0, tk.END)
    root.after(100, lambda: entry_afpsn.focus())  # Refocus input field


# **Manual AFPSN Search Function**
def search_manual():
    """Manually search for an AFPSN entered in the manual input field."""
    manual_afpsn = entry_manual_afpsn.get().strip()

    if not manual_afpsn:
        lbl_status.config(text="⚠ Enter AFPSN to search", fg="orange")
        return

    check_afpsn(manual_afpsn)  # Process manually entered AFPSN


# **Common Function for Checking AFPSN**
def check_afpsn(afpsn):
    """Check if the AFPSN is registered and display results."""
    attendee = fetch_attendee_details(afpsn)

    if attendee:
        lbl_status.config(text="✔ Registered", fg="green")
        name = attendee['name']
        unit = attendee['unit']
        rank = attendee['rank']
        status = "Registered"
    else:
        lbl_status.config(text="❌ Not Registered", fg="red")
        name, unit, rank, status = "N/A", "N/A", "N/A", "Not Registered"

    # Log and display the scan result
    log_scan(afpsn, name, unit, rank, status)

# Log Scan Function (Now Inserts Data into Database)
# Log Scan Function (Now Includes Status)
# Log Scan Function (Now Includes Status)
def log_scan(afpsn, name, unit, rank, status):
    """Log scanned or searched AFPSN with timestamp, including registration status."""
    if status != "Registered":
        print(f"❌ Not logging unregistered AFPSN: {afpsn}")
        return  # Do not log if the attendee is not registered

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="Joslep101",
            password="JoslepRESORT*1001",
            database="tracom-proj-db"
        )
        cursor = conn.cursor()

        # Insert scan record into 'scan_logs' table
        query = """
        INSERT INTO scan_logs (afpsn, name, unit, rank, scan_time, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (afpsn, name, unit, rank, timestamp, status))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Scan Logged in Database: {afpsn} at {timestamp} - Status: {status}")

    except mysql.connector.Error as err:
        print(f"❌ Database Insert Error: {err}")
        lbl_status.config(text="⚠ Error Logging Scan", fg="orange")

    # Also log in a text file (for backup)
    with open("scan_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} - Name: {name}, Unit: {unit}, Rank: {rank}, Status: {status}\n")

    # Update Last Scanned Label
    lbl_last_scanned.config(text=f"Last Checked: {afpsn} ({status})", fg="blue")

    # Insert scanned data into the table for display
    table.insert("", "end", values=(name, unit, rank, status))


# **GUI Setup**
root = tk.Tk()
root.title("QR Code Scanner System")
root.geometry("700x600")

# **Status Label**
lbl_status = tk.Label(root, text="Scan QR Code or Enter AFPSN", font=("Arial", 14, "bold"), fg="black")
lbl_status.pack(pady=10)

# **QR Scanner Input Field (Auto-Detects Input)**
entry_afpsn = tk.Entry(root, font=("Arial", 14), justify="center")
entry_afpsn.pack(pady=5)

# **Auto-Detect QR Code Scans Without Button Press**
entry_afpsn_var = tk.StringVar()
entry_afpsn.config(textvariable=entry_afpsn_var)
entry_afpsn_var.trace_add("write", lambda *args: root.after(500, on_qr_scanned))

# **Manual AFPSN Search Section**
lbl_manual = tk.Label(root, text="Or Enter AFPSN Manually:", font=("Arial", 12))
lbl_manual.pack(pady=5)

entry_manual_afpsn = tk.Entry(root, font=("Arial", 14), justify="center")
entry_manual_afpsn.pack(pady=5)

# **Function to Clear Manual Input**
def clear_manual_input():
    """Clears the manual AFPSN input field."""
    entry_manual_afpsn.delete(0, tk.END)
    entry_manual_afpsn.focus()  # Refocus the input field

# **Button Frame for Manual Input Actions**
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

# **Clear Button (New)**
btn_clear = tk.Button(btn_frame, text="Clear", font=("Arial", 12), command=clear_manual_input, fg="red")
btn_clear.pack(side="left", padx=5)

# **Search Button**
btn_search = tk.Button(btn_frame, text="Search", font=("Arial", 12), command=search_manual)
btn_search.pack(side="left", padx=5)


# **Table for Scanned QR Codes**
table_frame = tk.Frame(root)
table_frame.pack(pady=10)

columns = ("Name", "Unit", "Rank", "Status")
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)  # Slightly increased height

for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", width=150)  # Slightly increased width

table.pack()

# **Last Scanned Label**
lbl_last_scanned = tk.Label(root, text="Last Checked: None", font=("Arial", 10, "italic"), fg="gray")
lbl_last_scanned.pack(pady=10)

# **Fetch Scan Logs from Database**
# **Function to Fetch and Display Scan Logs**
# **Function to Fetch and Display Scan Logs**
def fetch_scan_logs(tree):
    """Fetch scan logs from the database and update the Treeview table."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="Joslep101",
            password="JoslepRESORT*1001",
            database="tracom-proj-db"
        )
        cursor = conn.cursor(dictionary=True)

        # Fetch ID, Rank, Name, and Unit from scan_logs
        query = "SELECT id, rank, name, unit FROM scan_logs ORDER BY scan_time ASC"
        cursor.execute(query)
        logs = cursor.fetchall()

        cursor.close()
        conn.close()

        # Clear existing table rows
        for row in tree.get_children():
            tree.delete(row)

        # Insert new data (Newest logs at the bottom)
        for log in logs:
            tree.insert("", "end", values=(log["id"], log["rank"], log["name"], log["unit"]))

    except mysql.connector.Error as err:
        print(f"❌ Database Query Error: {err}")

    # Auto-refresh every 5 seconds
    tree.after(5000, lambda: fetch_scan_logs(tree))



# **Function to Open Scan Logs Window**
# **Function to Open Scan Logs Window**
def open_scan_logs_window():
    """Open a new window displaying scan logs."""
    log_window = tk.Toplevel(root)
    log_window.title("Logs")
    log_window.geometry("600x400")  # Adjusted width for ID column

    lbl_title = tk.Label(log_window, text="WELCOME", font=("Arial", 25, "bold"))
    lbl_title.pack(pady=5)

    # Configure style for larger font in the table
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 13))  # Increase row font size
    style.configure("Treeview.Heading", font=("Arial", 15, "bold"))  # Increase header font size

    # Include ID in the table
    columns = ("Guest", "Rank", "Name", "Unit")
    tree = ttk.Treeview(log_window, columns=columns, show="headings", height=150, style="Treeview")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150 if col == "ID" else 250)

    tree.pack(pady=5)

    # Fetch logs and start auto-refresh
    fetch_scan_logs(tree)


# **Button to Open Scan Logs Window**
btn_logs = tk.Button(root, text="View Scan Logs", font=("Arial", 12), command=open_scan_logs_window)
btn_logs.pack(pady=10)



# **Auto-focus on QR Scanner Input Field**
entry_afpsn.focus()

# **Test database connection before starting**
test_db_connection()

# **Run GUI**
root.mainloop()
