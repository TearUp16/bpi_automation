import streamlit as st
import streamlit.components.v1 as components
import io
import re
import os
from io import BytesIO

import polars as pl
import pandas as pd

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="BPI Automation", layout="wide")


# =========================
# GLOBAL THEME
# =========================
def apply_global_theme() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

    :root {
        --bg-main: #ffffff;  /* Set the background to white */
        --bg-soft: #f0f0f0;  /* Light gray for soft elements */
        --bg-panel: #ffffff;  /* Panel background white */
        --bg-input: #ffffff;  /* Input background white */
        --bg-card: #f9f9f9;  /* Card background */
        --text-main: #333333;  /* Dark gray for primary text */
        --text-soft: #666666;  /* Lighter gray for secondary text */
        --text-dim: #999999;  /* Dimmed gray for lesser emphasis */
        --accent: #ff3b30;  /* Red accent */
        --border: #ddd;  /* Light border color */
        --success: #0f8b4c;  /* Green for success */
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-main);  /* Set the background to white */
        color: var(--text-main);  /* Set text color to dark gray */
        font-family: 'Syne', sans-serif;
    }

    * {
        font-family: 'Syne', sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"] {
        right: 0.75rem;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px;
    }

    /* =========================
       TITLE STYLE - REMARKS GENERATOR (H1 Style)
       ========================= */
    .app-title {
        font-size: 3rem;  /* Large font size for H1 style */
        font-weight: 800;
        color: #000000;  /* Black color */
        letter-spacing: -0.03em;
        margin-bottom: 1rem;  /* Add margin at the bottom */
        text-transform: uppercase;  /* Optional: Uppercase to give it a header feel */
    }

    /* =========================
       SIDEBAR - LIGHT
       ========================= */
    [data-testid="stSidebar"] {
        background: var(--bg-panel);  /* White background for sidebar */
        border-right: 1px solid var(--border);  /* Light border for sidebar */
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
    }

    [data-testid="stSidebar"] * {
        color: var(--text-main);  /* Dark text for sidebar */
    }

    .sidebar-brand {
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 1.2rem;
        color: #000000;  /* Black */
        letter-spacing: -0.03em;

        /* remove gradient effect */
        background: none;
        -webkit-text-fill-color: initial;
    }

    .sidebar-section {
        background: var(--bg-card);  /* Light background for sidebar sections */
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.9rem 0.85rem 0.95rem 0.85rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.1);
    }

    .sidebar-label {
        color: var(--text-soft);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    /* =========================
       BUTTONS AND INTERACTIONS
       ========================= */
    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em;
        background: linear-gradient(135deg, var(--accent), var(--accent-dark));
        color: white !important;
        transition: all 0.2s ease;
        box-shadow: 0 8px 22px rgba(179, 0, 0, 0.18);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.06);
    }

    .stAlert {
        border-radius: 12px !important;
    }

    /* =========================
       TEXT STYLES
       ========================= */
    h1, h2, h3, h4, p, label, .stMarkdown, .stText, div {
        color: var(--text-main);  /* Dark text for headings and content */
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input,
    [data-baseweb="select"] > div {
        background: var(--bg-input) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }

    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: var(--text-dim) !important;
        opacity: 1 !important;
        font-family: 'DM Mono', monospace !important;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(255, 59, 48, 0.15) !important;
    }

    .output-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.15rem 1.2rem;
        margin-bottom: 0.9rem;
    }

    .output-text {
        font-family: 'DM Mono', monospace !important;
        font-size: 0.9rem;
        color: var(--text-main);
        line-height: 1.6;
    }

    .output-empty {
        color: var(--text-dim);
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)


apply_global_theme()


# =========================
# SHARED HELPERS
# =========================
def render_page_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="app-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def clean_sheet_name(name: str, used_names: set[str]) -> str:
    cleaned = re.sub(r'[\\/*?:\[\]]', "_", str(name).strip())

    if not cleaned:
        cleaned = "BLANK_STATUS"

    cleaned = cleaned[:31]
    original = cleaned
    counter = 1

    while cleaned in used_names:
        suffix = f"_{counter}"
        cleaned = original[:31 - len(suffix)] + suffix
        counter += 1

    used_names.add(cleaned)
    return cleaned


def escape_js(text: str) -> str:
    return text.replace("\\", "\\\\").replace("`", "\\`").replace("</", "<\\/")


# =========================
# SIDEBAR NAVIGATION
# =========================
st.sidebar.markdown('<div class="sidebar-brand">BPI Tools</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-label">Module</div>', unsafe_allow_html=True)

main_mode = st.sidebar.selectbox(
    "Choose Module",
    [
        "📋 Remarks Generator",
        "📊 Report Generator",
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown('</div>', unsafe_allow_html=True)

if main_mode == "📊 Report Generator":
    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-label">Functions</div>', unsafe_allow_html=True)

    report_mode = st.sidebar.selectbox(
        "Choose Function",
        [
            "📂 DRR CSV Processor",
            "✅ POSITIVE Status",
            "❌ NEGATIVE Status",
            "🏍️ FIELD RESULT"
        ],
        label_visibility="collapsed"
    )

    st.sidebar.markdown('</div>', unsafe_allow_html=True)
else:
    report_mode = None


# =========================================================
# DRR CSV PROCESSOR
# =========================================================
def process_drr_file(file):
    df = pd.read_csv(file, dtype=str)
    df.columns = df.columns.str.strip()

    if "Account No." in df.columns:
        def convert_value(x):
            try:
                value = str(x).strip()
                if "E+" in value.upper():
                    return "{:.0f}".format(float(value))
                return x
            except Exception:
                return x

        df["Account No."] = df["Account No."].apply(convert_value)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    reference_path = os.path.join(base_dir, "Reference.xlsx")

    if not os.path.exists(reference_path):
        st.error("❌ Reference.xlsx not found")
        return None

    ref_df = pd.read_excel(reference_path, dtype=str)
    ref_df.columns = ref_df.columns.str.strip()

    required_ref_cols = ["Status", "Final Status", "Cycle", "Date", "Cut off"]
    missing_ref_cols = [col for col in required_ref_cols if col not in ref_df.columns]
    if missing_ref_cols:
        st.error(f"❌ Missing columns in Reference.xlsx: {', '.join(missing_ref_cols)}")
        return None

    required_csv_cols = ["Status", "Card No.", "Date"]
    missing_csv_cols = [col for col in required_csv_cols if col not in df.columns]
    if missing_csv_cols:
        st.error(f"❌ Missing columns in uploaded CSV: {', '.join(missing_csv_cols)}")
        return None

    status_map = dict(zip(
        ref_df["Status"].fillna("").str.strip().str.upper(),
        ref_df["Final Status"].fillna("0")
    ))

    df["STATUS"] = df["Status"].fillna("").str.strip().str.upper().map(status_map)
    df["STATUS"] = df["STATUS"].replace("UNKNOWN", "").fillna("0")

    ref_df["lookup_key"] = (
        ref_df["Cycle"].fillna("").str.strip().str.upper() + "|" +
        pd.to_datetime(ref_df["Date"], errors="coerce", dayfirst=True).dt.strftime("%d/%m/%Y").fillna("")
    )

    cutoff_map = dict(zip(ref_df["lookup_key"], ref_df["Cut off"].fillna("")))

    df["CYCLE"] = "CYCLE " + df["Card No."].fillna("").str[:2]

    df["Month Extracted"] = pd.to_datetime(
        df["Date"], errors="coerce", dayfirst=True
    ).dt.strftime("%b").fillna("")

    df["lookup_key"] = (
        df["CYCLE"].fillna("").str.strip().str.upper() + "|" +
        pd.to_datetime(df["Date"], errors="coerce", dayfirst=True).dt.strftime("%d/%m/%Y").fillna("")
    )

    df["Month Cut Off"] = df["lookup_key"].map(cutoff_map).fillna("")
    df.drop(columns=["lookup_key"], inplace=True)

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


# =========================================================
# POSITIVE STATUS
# =========================================================
def process_positive_status(file) -> pl.DataFrame:
    df = pl.read_excel(file, engine="calamine")
    df.columns = [col.strip() for col in df.columns]

    if "STATUS" not in df.columns:
        raise ValueError("Missing STATUS column.")

    required_defaults = {
        "Account No.": "",
        "Dialed Number": "",
        "Month Extracted": "",
    }

    for col_name, default_value in required_defaults.items():
        if col_name not in df.columns:
            df = df.with_columns(pl.lit(default_value).alias(col_name))

    df = df.with_columns([
        pl.col("STATUS").cast(pl.Utf8).fill_null("").str.strip_chars(),
        pl.col("Account No.").cast(pl.Utf8).fill_null("").str.strip_chars().str.replace(r"\.0$", ""),
        pl.col("Dialed Number").cast(pl.Utf8).fill_null("").str.strip_chars().str.replace(r"\.0$", ""),
        pl.col("Month Extracted").cast(pl.Utf8).fill_null("").str.strip_chars(),
    ])

    df = df.with_columns(
        pl.when(
            (pl.col("Dialed Number") != "") &
            (~pl.col("Dialed Number").str.starts_with("+"))
        )
        .then(pl.lit("+") + pl.col("Dialed Number"))
        .otherwise(pl.col("Dialed Number"))
        .alias("Dialed Number")
    )

    df = df.filter(
        (pl.col("STATUS").str.to_uppercase() != "NEGATIVE") &
        (pl.col("STATUS").str.to_uppercase() != "0") &
        (pl.col("STATUS") != "")
    )

    df = df.with_columns(
        (pl.col("Account No.") + pl.lit(" | ") + pl.col("Month Extracted"))
        .alias("Account No. + Month Extracted")
    )

    new_order = ["Account No. + Month Extracted"] + [
        col for col in df.columns if col != "Account No. + Month Extracted"
    ]

    return df.select(new_order)


def to_excel_bytes_by_status(df: pl.DataFrame) -> bytes:
    output = io.BytesIO()
    used_sheet_names = set()

    status_values = (
        df.select("STATUS")
        .unique()
        .sort("STATUS")
        .to_series()
        .to_list()
    )

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for status_value in status_values:
            sheet_name = clean_sheet_name(status_value, used_sheet_names)
            sheet_df = df.filter(pl.col("STATUS") == status_value)
            sheet_df.to_pandas().to_excel(writer, index=False, sheet_name=sheet_name)

    output.seek(0)
    return output.getvalue()


# =========================================================
# NEGATIVE STATUS
# =========================================================
def filter_negative_status(file) -> pl.DataFrame:
    df = pl.read_excel(file, engine="calamine")
    df.columns = [col.strip() for col in df.columns]

    if "STATUS" not in df.columns:
        raise ValueError("Missing STATUS column.")

    required_defaults = {
        "Account No.": "",
        "Dialed Number": "",
        "Month Extracted": "",
    }

    for col_name, default_value in required_defaults.items():
        if col_name not in df.columns:
            df = df.with_columns(pl.lit(default_value).alias(col_name))

    df = df.with_columns([
        pl.col("STATUS").cast(pl.Utf8).fill_null("").str.strip_chars(),
        pl.col("Account No.").cast(pl.Utf8).fill_null("").str.strip_chars().str.replace(r"\.0$", ""),
        pl.col("Dialed Number").cast(pl.Utf8).fill_null("").str.strip_chars().str.replace(r"\.0$", ""),
        pl.col("Month Extracted").cast(pl.Utf8).fill_null("").str.strip_chars(),
    ])

    df = df.filter(pl.col("STATUS").str.to_uppercase() == "NEGATIVE")

    df = df.with_columns(
        pl.when(
            (pl.col("Dialed Number") != "") &
            (~pl.col("Dialed Number").str.starts_with("+"))
        )
        .then(pl.lit("+") + pl.col("Dialed Number"))
        .otherwise(pl.col("Dialed Number"))
        .alias("Dialed Number")
    )

    df = df.with_columns(
        (pl.col("Account No.") + pl.lit(" | ") + pl.col("Month Extracted"))
        .alias("Account No. + Month Extracted")
    )

    new_order = ["Account No. + Month Extracted"] + [
        col for col in df.columns if col != "Account No. + Month Extracted"
    ]

    return df.select(new_order)


def to_excel_bytes(df: pl.DataFrame) -> bytes:
    output = io.BytesIO()
    df.to_pandas().to_excel(output, index=False)
    output.seek(0)
    return output.getvalue()


# =========================================================
# FIELD RESULT
# =========================================================
@st.cache_data
def convert_df_to_excel(df: pd.DataFrame):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="FilteredData")
    output.seek(0)
    return output


# =========================================================
# REMARKS GENERATOR PAGE
# =========================================================
def render_remarks_generator() -> None:
    render_page_header("Remarks Generator", "Collections · Volare & F1 Format")

    if "clear_trigger" not in st.session_state:
        st.session_state.clear_trigger = 0

    ct = st.session_state.clear_trigger
    key = lambda k: f"{k}_{ct}"

    RFD_OPTIONS = {
        "": "— Select RFD —",
        "INSU": "INSU – Financial Difficulty (Lack/Awaiting Funds)",
        "UNEM": "UNEM – Unemployed",
        "BUSL": "BUSL – Business Closure/Slowdown",
        "OVLK": "OVLK – Forgot/Overlooked",
        "SICK": "SICK – Family Member/Client Hospitalized",
        "PRIO": "PRIO – Prioritize Other Expenses",
        "OOTC": "OOTC – OOTC/OOT",
        "NONB": "NONB – Payment Channel Issue",
        "TYPH": "TYPH – Natural Disaster or Calamity",
        "NLRS": "NLRS – NRS/LRS",
        "DISP": "DISP – Dispute",
        "PAPO": "PAPO – Pending Nego/Reversal",
        "PAPB": "PAPB – Pending Nego/Reversal",
        "BS": "BS – Business Slowdown",
        "CC": "CC – Contested Charges/Dispute",
        "DC": "DC – Deceased Cardholder",
        "FE": "FE – Family Emergency",
        "FTP": "FTP – Forgot to Pay/Overlooked Payment",
        "IL": "IL – ILL/Sickness in the family",
        "OL": "OL – Old age/Retired",
        "OT": "OT – Out of the country/Migrated",
        "OV": "OV – Over extended/Lack or Short of funds",
        "SK": "SK – Skip in both RA and BA/No lead",
        "UK": "UK – Unknown reason/Third party contact only",
        "UN": "UN – Loss of job/Unemployment",
        "AR": "AR – Awaiting Remittance",
        "AC": "AC – Awaiting Collection",
        "CV": "CV – Victim of Calamity (typhoon, fire, earthquake, pandemic or war)",
    }

    SRC_OPTIONS = {
        "": "— Select SRC —",
        "EML": "EML – Email",
        "FLD": "FLD – Field",
        "SMS": "SMS – SMS",
        "CAL": "CAL – Call",
    }

    col1, col2 = st.columns([1, 2])
    with col1:
        confidence = st.selectbox(
            "Confidence Level",
            ["", "1_", "0_"],
            key=key("conf"),
            format_func=lambda x: "— Select —" if x == "" else x
        )
    with col2:
        number_email = st.text_input(
            "Number / Email",
            placeholder="e.g. 09176308527 or email@example.com",
            key=key("num")
        )

    col3, col4 = st.columns(2)
    with col3:
        rfd_key = st.selectbox(
            "RFD – Reason for Delinquency",
            list(RFD_OPTIONS.keys()),
            format_func=lambda x: RFD_OPTIONS[x],
            key=key("rfd")
        )
    with col4:
        src_key = st.selectbox(
            "SRC – Source of Contact",
            list(SRC_OPTIONS.keys()),
            format_func=lambda x: SRC_OPTIONS[x],
            key=key("src")
        )

    soi = st.text_input(
        "SOI – Source of Income",
        placeholder="e.g. business, job, etc...",
        key=key("soi")
    )

    remarks = st.text_area(
        "Remarks",
        placeholder="Enter your remarks here…",
        key=key("remarks"),
        height=90
    )

    v_parts = []
    if confidence or number_email:
        v_parts.append(f"{confidence}{number_email}".strip())
    if rfd_key:
        v_parts.append(f"RFD:{rfd_key}")
    if src_key:
        v_parts.append(f"SRC:{src_key}")
    if soi:
        v_parts.append(f"SOI:{soi}")
    if remarks:
        v_parts.append(f"REMARKS:{remarks}")

    v_text = " | ".join([part for part in v_parts if part])
    f1_text = " - ".join([part for part in [number_email, remarks] if part])

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### Generated Remarks")

    st.markdown(f"""
    <div class="output-card">
      <div class="output-label">🔴 For Volare</div>
      <div class="output-text {'output-empty' if not v_text else ''}">
        {v_text if v_text else 'Fill in the fields above to generate…'}
      </div>
    </div>
    <div class="output-card">
      <div class="output-label">⚫ For F1</div>
      <div class="output-text {'output-empty' if not f1_text else ''}">
        {f1_text if f1_text else 'Fill in Number/Email and Remarks…'}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    b1, b2, b3 = st.columns(3)

    with b1:
        st.markdown("""
        <style>
        div[data-testid="column"]:nth-child(1) .stButton > button{
            background:#191919 !important;
            color:#ff5b5b !important;
            border:1px solid #4a1414 !important;
            box-shadow:none !important;
        }
        div[data-testid="column"]:nth-child(1) .stButton > button:hover{
            background:#2a0a0a !important;
        }
        </style>
        """, unsafe_allow_html=True)

        if st.button("🗑️ CLEAR", key="clear_btn"):
            st.session_state.clear_trigger += 1
            st.rerun()

    v_safe = escape_js(v_text)
    f1_safe = escape_js(f1_text)

    with b2:
        components.html(f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700&display=swap');
          body {{ margin:0; background:transparent; }}
          button {{
            width:100%;
            padding:0.65rem 1rem;
            background:linear-gradient(135deg,#ff3b30,#b30000);
            color:#fff;
            border:none;
            border-radius:10px;
            font-family:'Syne',sans-serif;
            font-weight:700;
            font-size:0.78rem;
            letter-spacing:0.05em;
            cursor:pointer;
            transition:opacity 0.2s;
          }}
          button:hover {{ opacity:0.9; }}
          button.ok {{ background:linear-gradient(135deg,#0f8b4c,#0a5e34); }}
        </style>
        <button id="btn" onclick="copyText()">📋 VOLARE REMARKS</button>
        <script>
          function copyText() {{
            const txt = `{v_safe}`;
            if (!txt.trim()) {{
              alert('Nothing to copy — fill in the fields first.');
              return;
            }}
            navigator.clipboard.writeText(txt).then(() => {{
              const b = document.getElementById('btn');
              b.textContent = '✅ COPIED!';
              b.classList.add('ok');
              setTimeout(() => {{
                b.textContent = '📋 VOLARE REMARKS';
                b.classList.remove('ok');
              }}, 2000);
            }}).catch(() => {{
              const ta = document.createElement('textarea');
              ta.value = txt;
              ta.style.position = 'fixed';
              ta.style.opacity = '0';
              document.body.appendChild(ta);
              ta.select();
              document.execCommand('copy');
              document.body.removeChild(ta);
              const b = document.getElementById('btn');
              b.textContent = '✅ COPIED!';
              b.classList.add('ok');
              setTimeout(() => {{
                b.textContent = '📋 VOLARE REMARKS';
                b.classList.remove('ok');
              }}, 2000);
            }});
          }}
        </script>
        """, height=45)

    with b3:
        components.html(f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700&display=swap');
          body {{ margin:0; background:transparent; }}
        button {{
            width:100%; 
            padding:0.65rem 1rem;
            background:linear-gradient(135deg,#ff3b30,#b30000);
            color:#fff;
            border:none;
            border-radius:10px;
            font-family:'Syne',sans-serif;
            font-weight:700;
            font-size:0.78rem;
            letter-spacing:0.05em;
            cursor:pointer;
            transition:opacity 0.2s;
        }}
          button:hover {{ opacity:0.9; }}
          button.ok {{ background:linear-gradient(135deg,#0f8b4c,#0a5e34); }}
        </style>
        <button id="btn" onclick="copyText()">📋 F1 REMARKS</button>
        <script>
          function copyText() {{
            const txt = `{f1_safe}`;
            if (!txt.trim()) {{
              alert('Nothing to copy — fill in Number/Email and Remarks first.');
              return;
            }}
            navigator.clipboard.writeText(txt).then(() => {{
              const b = document.getElementById('btn');
              b.textContent = '✅ COPIED!';
              b.classList.add('ok');
              setTimeout(() => {{
                b.textContent = '📋 F1 REMARKS';
                b.classList.remove('ok');
              }}, 2000);
            }}).catch(() => {{
              const ta = document.createElement('textarea');
              ta.value = txt;
              ta.style.position = 'fixed';
              ta.style.opacity = '0';
              document.body.appendChild(ta);
              ta.select();
              document.execCommand('copy');
              document.body.removeChild(ta);
              const b = document.getElementById('btn');
              b.textContent = '✅ COPIED!';
              b.classList.add('ok');
              setTimeout(() => {{
                b.textContent = '📋 F1 REMARKS';
                b.classList.remove('ok');
              }}, 2000);
            }});
          }}
        </script>
        """, height=45)

    with st.expander("📖 RFD Quick Reference"):
        ref_data = {k: v.split("–")[-1].strip() for k, v in RFD_OPTIONS.items() if k}
        cols = st.columns(2)
        items = list(ref_data.items())
        half = len(items) // 2

        for i, (code, desc) in enumerate(items):
            with cols[0 if i < half else 1]:
                st.markdown(f"**`{code}`** — {desc}")


# =========================================================
# REPORT GENERATOR PAGE
# =========================================================
def render_report_generator(report_mode: str) -> None:
    if report_mode == "📂 DRR CSV Processor":
        render_page_header("📂 DRR CSV Processing Tool", "Report Generator")

        uploaded_file = st.file_uploader("Upload DRR CSV File", type=["csv"])

        if uploaded_file is not None:
            st.success("✅ File uploaded")

            if st.button("🚀 Process File"):
                with st.spinner("Processing..."):
                    processed_df = process_drr_file(uploaded_file)

                if processed_df is not None:
                    st.success("✅ Processing complete")
                    st.dataframe(processed_df.head(50), use_container_width=True)

                    output = BytesIO()
                    processed_df.to_excel(output, index=False, engine="openpyxl")
                    output.seek(0)

                    st.download_button(
                        label="📥 Download Excel File",
                        data=output.getvalue(),
                        file_name="processed_drr.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

    elif report_mode == "✅ POSITIVE Status":
        render_page_header("✅ Positive Status", "Report Generator")

        uploaded_file = st.file_uploader("Upload CMS EXTRACTION file", type=["xlsx"])

        if uploaded_file:
            try:
                df = process_positive_status(uploaded_file)
                st.dataframe(df.head(100).to_pandas(), use_container_width=True)

                excel_data = to_excel_bytes_by_status(df)

                st.download_button(
                    "Download POS STATUS by Sheet",
                    data=excel_data,
                    file_name=f"POS_STATUS_{uploaded_file.name}"
                )

            except Exception as e:
                st.error(f"Error: {e}")

    elif report_mode == "❌ NEGATIVE Status":
        render_page_header("❌ Negative Status", "Report Generator")

        uploaded_file = st.file_uploader("Upload CMS EXTRACTION file", type=["xlsx"])

        if uploaded_file:
            try:
                df = filter_negative_status(uploaded_file)

                if df.height == 0:
                    st.warning("No NEGATIVE rows found.")
                else:
                    st.dataframe(df.head(100).to_pandas(), use_container_width=True)

                    st.download_button(
                        "Download Filtered File",
                        data=to_excel_bytes(df),
                        file_name=uploaded_file.name
                    )

            except Exception as e:
                st.error(f"Error: {e}")

    elif report_mode == "🏍️ FIELD RESULT":
        render_page_header("🏍️ FIELD RESULT", "Report Generator · BPI Cards XDays")

        uploaded_file = st.file_uploader("Upload FIELD RESULT file", type=["xlsx"])

        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file, sheet_name="RESULT")
                df.columns = [col.strip().lower() for col in df.columns]

                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%m/%d/%Y")

                if "bank" not in df.columns:
                    st.error("❌ Missing 'bank' column.")
                    return

                filtered_df = df[df["bank"].str.contains("bpi cards xdays", case=False, na=False)]

                columns_to_display = [
                    "chcode", "status", "sub status", "informant", "client number",
                    "dl received/unreceived", "message", "ptp-date", "ptp amount",
                    "field_name", "date", "bank"
                ]

                filtered_columns = [col for col in columns_to_display if col in filtered_df.columns]

                st.write("Filtered Data:")
                st.dataframe(filtered_df[filtered_columns], use_container_width=True)

                excel_data = convert_df_to_excel(filtered_df[filtered_columns])

                st.download_button(
                    label="Download Filtered Data as Excel",
                    data=excel_data.getvalue(),
                    file_name="filtered_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"Error: {e}")


# =========================================================
# MAIN ROUTER
# =========================================================
if main_mode == "📋 Remarks Generator":
    render_remarks_generator()
elif main_mode == "📊 Report Generator" and report_mode is not None:
    render_report_generator(report_mode)