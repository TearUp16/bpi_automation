import streamlit as st # type: ignore
import pandas as pd # type: ignore
import os
from io import BytesIO

st.set_page_config(page_title="DRR CSV Processor", layout="wide")

st.title("📂 DRR CSV Processing Tool")

uploaded_file = st.file_uploader("Upload DRR CSV File", type=["csv"])


# -------------------------------
# PROCESS FUNCTION
# -------------------------------
def process_file(file):
    df = pd.read_csv(file, dtype=str)
    df.columns = df.columns.str.strip()

    # FIX ACCOUNT NUMBER
    if "Account No." in df.columns:
        def convert_value(x):
            try:
                if "E+" in str(x):
                    return '{:.0f}'.format(float(x))
                return x
            except:
                return x

        df["Account No."] = df["Account No."].apply(convert_value)

    # LOAD REFERENCE
    reference_path = os.path.join(os.getcwd(), "Reference.xlsx")

    if not os.path.exists(reference_path):
        st.error("❌ Reference.xlsx not found")
        return None

    ref_df = pd.read_excel(reference_path, dtype=str)
    ref_df.columns = ref_df.columns.str.strip()

    # STATUS mapping
    status_map = dict(zip(
        ref_df["Status"].str.strip().str.upper(),
        ref_df["Final Status"]
    ))

    df["STATUS"] = df["Status"].str.strip().str.upper().map(status_map)
    df["STATUS"] = df["STATUS"].replace("UNKNOWN", "").fillna("0")

    # LOOKUP KEY (MATCH FORMAT)
    ref_df["lookup_key"] = (
        ref_df["Cycle"].str.strip().str.upper() +
        pd.to_datetime(ref_df["Date"], errors="coerce", dayfirst=True).dt.strftime("%d/%m/%Y")
    )

    cutoff_map = dict(zip(ref_df["lookup_key"], ref_df["Cut off"]))

    # CYCLE
    df["CYCLE"] = "CYCLE " + df["Card No."].str[:2].fillna("")

    # MONTH EXTRACTED
    df["Month Extracted"] = pd.to_datetime(
        df["Date"], errors="coerce", dayfirst=True
    ).dt.strftime("%b")

    # MONTH CUT OFF
    df["lookup_key"] = (
        df["CYCLE"].str.strip().str.upper() +
        pd.to_datetime(df["Date"], errors="coerce", dayfirst=True).dt.strftime("%d/%m/%Y")
    )

    df["Month Cut Off"] = df["lookup_key"].map(cutoff_map).fillna("")
    df.drop(columns=["lookup_key"], inplace=True)

    # FINAL COLUMNS
    desired_columns = [
        "STATUS",
        "CYCLE",
        "Month Cut Off",
        "Month Extracted",
        "S.No",
        "Date",
        "Time",
        "Debtor",
        "Account No.",
        "Card No.",
        "Status",
        "Remark",
        "Remark By",
        "Client",
        "Product Type",
        "PTP Amount",
        "Next Call",
        "PTP Date",
        "Claim Paid Amount",
        "Claim Paid Date",
        "Dialed Number",
        "Balance",
        "Call Duration"
    ]

    df = df[[col for col in desired_columns if col in df.columns]]

    return df


# -------------------------------
# UI LOGIC
# -------------------------------
if uploaded_file is not None:

    st.success("✅ File uploaded")

    if st.button("🚀 Process File"):

        with st.spinner("Processing..."):
            processed_df = process_file(uploaded_file)

        if processed_df is not None:

            st.success("✅ Processing complete")

            st.dataframe(processed_df.head(50))

            # -------------------------------
            # 🔥 INSTANT DOWNLOAD (NO FILE SAVE)
            # -------------------------------
            output = BytesIO()
            processed_df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.download_button(
                label="📥 Download Excel File",
                data=output,
                file_name="processed_drr.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )