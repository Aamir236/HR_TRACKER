import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, timedelta

# ---------------- DATABASE ----------------

conn = sqlite3.connect("hr_clients.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    company TEXT,
    email TEXT,
    cc_email TEXT,
    phone TEXT,
    position TEXT,
    contact_date TEXT,
    status TEXT,
    follow_up TEXT,
    notes TEXT
)
""")

# Add the CC field to databases created by earlier versions of the tracker.
columns = {
    row[1] for row in conn.execute("PRAGMA table_info(clients)")
}
if "cc_email" not in columns:
    conn.execute("ALTER TABLE clients ADD COLUMN cc_email TEXT")

conn.commit()

# ---------------- SETTINGS ----------------

st.set_page_config(
    page_title="Ms Sahar HR",
    page_icon="🤝",
    layout="wide"
)

st.title("Ms Sahar HR")
st.caption("A refined workspace for client relationships, communication, and follow-ups.")

today = date.today()

# ---------------- LOAD DATA ----------------

def load_clients():
    return pd.read_sql_query(
        """
        SELECT id, name, company, email, cc_email, phone,
               position, contact_date, status, follow_up, notes
        FROM clients
        ORDER BY contact_date DESC
        """,
        conn
    )

df = load_clients()

# ---------------- DASHBOARD ----------------

total = len(df)

pending = len(
    df[df["status"] == "Waiting for Reply"]
)

replied = len(
    df[df["status"] == "Replied"]
)

if not df.empty:
    overdue = len(
        df[
            (df["follow_up"] < str(today))
            & (df["status"] != "Replied")
        ]
    )
else:
    overdue = 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Clients", total)
col2.metric("Waiting for Reply", pending)
col3.metric("Clients Replied", replied)
col4.metric("Overdue Follow-ups", overdue)

st.divider()

# ---------------- ADD CLIENT ----------------

st.subheader("➕ Add New Client")

with st.form("client_form"):

    name = st.text_input("Client Name")
    company = st.text_input("Company Name")

    email = st.text_input("Email Address")
    cc_email = st.text_input("CC Email Address (optional)")
    phone = st.text_input("Phone Number")

    position = st.text_input("Job Position")

    contact_date = st.date_input(
        "Date Contacted",
        value=today
    )

    status = st.selectbox(
        "Client Status",
        [
            "Waiting for Reply",
            "Replied",
            "Interested",
            "Not Interested",
            "Meeting Scheduled",
            "Closed"
        ]
    )

    follow_up = st.date_input(
        "Next Follow-up Date",
        value=today + timedelta(days=60)
    )

    notes = st.text_area(
        "Notes / Communication Details"
    )

    submitted = st.form_submit_button(
        "Save Client"
    )

    if submitted:

        if not name.strip():
            st.error("Please enter the client name.")

        else:

            conn.execute("""
                INSERT INTO clients (
                    name, company, email, cc_email, phone,
                    position, contact_date,
                    status, follow_up, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                company,
                email,
                cc_email,
                phone,
                position,
                str(contact_date),
                status,
                str(follow_up),
                notes
            ))

            conn.commit()

            st.success("Client saved successfully!")

            st.rerun()

# ---------------- SEARCH CLIENTS ----------------

st.divider()

st.subheader("🔎 Search Client")

search = st.text_input(
    "Search by client, company, email/CC, or phone"
)

df = load_clients()

if search:

    df = df[
        df.astype(str)
        .apply(
            lambda row: row.str.contains(
                search,
                case=False,
                na=False
            ).any(),
            axis=1
        )
    ]

st.dataframe(
    df,
    width="stretch",
    hide_index=True
)

# ---------------- FOLLOW-UP REMINDERS ----------------

st.divider()

st.subheader("⏰ Follow-up Reminders")

if not df.empty:

    reminders = df[
        (df["follow_up"] <= str(today))
        & (~df["status"].isin(["Replied", "Closed"]))
    ]

    if not reminders.empty:

        st.warning(
            f"{len(reminders)} client(s) need follow-up."
        )

        st.dataframe(
            reminders[
                [
                    "name",
                    "company",
                    "phone",
                    "status",
                    "follow_up"
                ]
            ],
            width="stretch",
            hide_index=True
        )

    else:

        st.success("No overdue follow-ups.")

# ---------------- EXPORT EXCEL ----------------

st.divider()

st.subheader("📥 Export Client Records")

df = load_clients()

if not df.empty:

    excel_file = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Client Records CSV",
        data=excel_file,
        file_name="HR_Client_Records.csv",
        mime="text/csv"
    )

# ---------------- CLOSE DATABASE ----------------

conn.close()
