import streamlit as st # type: ignore
import pandas as pd # type: ignore
import pyodbc # type: ignore

# --- Connection ---
def get_connection():
    return pyodbc.connect(
        "DRIVER={MySQL ODBC 5.1 Driver};"
        "SERVER=172.16.128.79;"
        "DATABASE=volare;"
        "UID=usr4mis;"
        "PWD=usr4MIS#@!;"
        "PORT=3307;"
    )

# --- Base Query ---
BASE_QUERY = """
SELECT
    debtor.id AS 'S.NO',
    followup.date AS 'DATE',
    debtor.name AS 'DEBTOR',
    debtor.account AS 'ACCOUNT NUMBER',
    debtor.card_no AS 'CARD NO.',
    followup.status_code AS 'STATUS',
    followup.remark AS 'REMARK',
    followup.remark_by AS 'REMARK BY',
    debtor.client_name AS 'CLIENT',
    debtor.product_type AS 'PRODUCT TYPE',
    debtor_followup.ptp_amount AS 'PTP AMOUNT',
    debtor.next_call AS 'NEXT CALL',
    debtor_followup.next_call AS 'NEXT CALL 2',
    debtor_followup.ptp_date AS 'PTP DATE',
    debtor_followup.claim_paid_amount AS 'CLAIM PAID AMOUNT',
    debtor_followup.claim_paid_date AS 'CLAIM PAID DATE',
    followup.contact_number AS 'DIALED NUMBER',
    debtor.balance AS 'BALANCE',
    followup.call_duration AS 'CALL DURATION'
FROM debtor
JOIN debtor_followup
    ON debtor_followup.debtor_id = debtor.id
JOIN followup
    ON followup.id = debtor_followup.followup_id
WHERE debtor.client_id = 74
    AND debtor.is_aborted = 0
    AND debtor.is_locked = 0
    AND followup.datetime >= CURDATE() - INTERVAL 1 DAY
    AND followup.datetime < CURDATE()
"""

# --- Preview (fast) ---
@st.cache_data(ttl=300)
def fetch_preview():
    conn = get_connection()
    df = pd.read_sql(BASE_QUERY + " LIMIT 100", conn)
    conn.close()
    return df

# --- Full data (for download) ---
@st.cache_data(ttl=300)
def fetch_full():
    conn = get_connection()
    df = pd.read_sql(BASE_QUERY, conn)
    conn.close()
    return df

# --- UI ---
st.title("Debtor Follow-up Report")

# Preview table
df_preview = fetch_preview()
st.write(f"Showing {len(df_preview)} rows (preview)")
st.dataframe(df_preview)

# Download full data
if st.button("Prepare Full Download"):
    with st.spinner("Fetching full dataset..."):
        df_full = fetch_full()

    st.download_button(
        label="Download Full Report",
        data=df_full.to_csv(index=False),
        file_name="debtor_followup_report.csv",
        mime="text/csv"
    )