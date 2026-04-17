import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Remarks Generator", page_icon="📋", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

* { font-family: 'Syne', sans-serif; }

html, body, [data-testid="stAppViewContainer"] { background: #0a0a0a; }
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 50%, #1e0000 0%, #0a0a0a 60%);
    min-height: 100vh;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem !important; max-width: 780px !important; }

h1 {
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #ff2a2a, #cc0000, #ff6b6b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    margin-bottom: 0 !important;
}
.subtitle {
    color: #555; font-size: 0.85rem; letter-spacing: 0.12em;
    text-transform: uppercase; margin-bottom: 2rem; font-weight: 600;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #1a0a0a !important; border: 1px solid #3a1a1a !important;
    border-radius: 8px !important; color: #fff !important;
    font-family: 'DM Mono', monospace !important; font-size: 0.9rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #cc0000 !important; box-shadow: 0 0 0 2px rgba(204,0,0,0.2) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #1a0a0a !important; border: 1px solid #3a1a1a !important;
    border-radius: 8px !important; color: #fff !important;
}
.output-card {
    background: #110505; border: 1px solid #3a1010;
    border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 0.8rem;
}
.output-label {
    font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase;
    color: #cc0000; font-weight: 700; margin-bottom: 0.5rem;
}
.output-text {
    font-family: 'DM Mono', monospace; font-size: 0.88rem;
    color: #e0e0e0; word-break: break-all; line-height: 1.6;
}
.output-empty { color: #443333; font-style: italic; font-size: 0.85rem; }
.stButton > button {
    border-radius: 8px !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; letter-spacing: 0.05em !important;
    font-size: 0.85rem !important; transition: all 0.2s ease !important;
    border: none !important; width: 100% !important; padding: 0.65rem 1rem !important;
}
hr { border-color: #1e0a0a !important; margin: 1.5rem 0 !important; }
label { color: #aaa !important; font-size: 0.82rem !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Remarks Generator</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Collections · Volare & F1 Format</p>', unsafe_allow_html=True)

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
    "BS":  "BS – Business Slowdown",
    "CC":  "CC – Contested Charges/Dispute",
    "DC":  "DC – Deceased Cardholder",
    "FE":  "FE – Family Emergency",
    "FTP": "FTP – Forgot to Pay/Overlooked Payment",
    "IL":  "IL – ILL/Sickness in the family",
    "OL":  "OL – Old age/Retired",
    "OT":  "OT – Out of the country/Migrated",
    "OV":  "OV – Over extended/Lack or Short of funds",
    "SK":  "SK – Skip in both RA and BA/No lead",
    "UK":  "UK – Unknown reason/Third party contact only",
    "UN":  "UN – Loss of job/Unemployment",
    "AR":  "AR – Awaiting Remittance",
    "AC":  "AC – Awaiting Collection",
    "CV":  "CV – Victim of Calamity (typhoon, fire, earthquake, pandemic or war)",
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
    confidence = st.selectbox("Confidence Level", ["", "1_", "0_"], key=key("conf"),
                               format_func=lambda x: "— Select —" if x == "" else x)
with col2:
    number_email = st.text_input("Number / Email", placeholder="e.g. 09176308527 or email@example.com", key=key("num"))

col3, col4 = st.columns(2)
with col3:
    rfd_key = st.selectbox("RFD – Reason for Delinquency", list(RFD_OPTIONS.keys()),
                            format_func=lambda x: RFD_OPTIONS[x], key=key("rfd"))
with col4:
    src_key = st.selectbox("SRC – Source of Contact", list(SRC_OPTIONS.keys()),
                            format_func=lambda x: SRC_OPTIONS[x], key=key("src"))

soi = st.text_input("SOI – Source of Income", placeholder="e.g. business, job, etc...", key=key("soi"))
remarks = st.text_area("Remarks", placeholder="Enter your remarks here…", key=key("remarks"), height=90)

v_text = f"{confidence}{number_email} | RFD:{rfd_key} | SRC:{src_key} | SOI:{soi} | REMARKS:{remarks}".strip(" |") \
         if any([confidence, number_email, rfd_key, src_key, soi, remarks]) else ""
f1_text = f"{number_email} - {remarks}".strip(" -") \
          if any([number_email, remarks]) else ""

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("#### Generated Remarks")

st.markdown(f"""
<div class="output-card">
  <div class="output-label">🔴 For Volare</div>
  <div class="output-text {'output-empty' if not v_text else ''}">{v_text if v_text else 'Fill in the fields above to generate…'}</div>
</div>
<div class="output-card">
  <div class="output-label">⚫ For F1</div>
  <div class="output-text {'output-empty' if not f1_text else ''}">{f1_text if f1_text else 'Fill in Number/Email and Remarks…'}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Clear button (Streamlit) ──────────────────────────────
b1, b2, b3 = st.columns(3)
with b1:
    st.markdown("""<style>div[data-testid="column"]:nth-child(1) .stButton>button{background:#1a1a1a;color:#ff4444;border:1px solid #440000 !important;}
    div[data-testid="column"]:nth-child(1) .stButton>button:hover{background:#2a0000;}</style>""", unsafe_allow_html=True)
    if st.button("🗑️ CLEAR", key="clear_btn"):
        st.session_state.clear_trigger += 1
        st.rerun()

# ── Copy buttons as real HTML inside components.html ─────
# These live in their own iframe so clipboard API works natively on click
def escape_js(s):
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("</", "<\\/")

v_safe  = escape_js(v_text)
f1_safe = escape_js(f1_text)

with b2:
    components.html(f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700&display=swap');
      body {{ margin:0; background:transparent; }}
      button {{
        width:100%; padding:0.65rem 1rem;
        background:linear-gradient(135deg,#cc0000,#8b0000);
        color:#fff; border:none; border-radius:8px;
        font-family:'Syne',sans-serif; font-weight:700;
        font-size:0.78rem; letter-spacing:0.05em;
        cursor:pointer; transition:opacity 0.2s;
      }}
      button:hover {{ opacity:0.88; }}
      button.ok {{ background:linear-gradient(135deg,#007700,#004400); }}
    </style>
    <button id="btn" onclick="copyText()">📋VOLARE REMARKS</button>
    <script>
      function copyText() {{
        const txt = `{v_safe}`;
        if (!txt.trim()) {{ alert('Nothing to copy — fill in the fields first.'); return; }}
        navigator.clipboard.writeText(txt).then(() => {{
          const b = document.getElementById('btn');
          b.textContent = '✅ COPIED!';
          b.classList.add('ok');
          setTimeout(() => {{ b.textContent = '📋 COPY VOLARE REMARKS'; b.classList.remove('ok'); }}, 2000);
        }}).catch(() => {{
          const ta = document.createElement('textarea');
          ta.value = txt; ta.style.position='fixed'; ta.style.opacity='0';
          document.body.appendChild(ta); ta.select();
          document.execCommand('copy'); document.body.removeChild(ta);
          const b = document.getElementById('btn');
          b.textContent = '✅ COPIED!';
          b.classList.add('ok');
          setTimeout(() => {{ b.textContent = '📋 COPY VOLARE REMARKS'; b.classList.remove('ok'); }}, 2000);
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
        width:100%; padding:0.65rem 1rem;
        background:linear-gradient(135deg,#2a2a2a,#111111);
        color:#fff; border:none; border-radius:8px;
        font-family:'Syne',sans-serif; font-weight:700;
        font-size:0.78rem; letter-spacing:0.05em;
        cursor:pointer; transition:opacity 0.2s;
      }}
      button:hover {{ opacity:0.88; }}
      button.ok {{ background:linear-gradient(135deg,#007700,#004400); }}
    </style>
    <button id="btn" onclick="copyText()">📋F1 REMARKS</button>
    <script>
      function copyText() {{
        const txt = `{f1_safe}`;
        if (!txt.trim()) {{ alert('Nothing to copy — fill in Number/Email and Remarks first.'); return; }}
        navigator.clipboard.writeText(txt).then(() => {{
          const b = document.getElementById('btn');
          b.textContent = '✅ COPIED!';
          b.classList.add('ok');
          setTimeout(() => {{ b.textContent = '📋 COPY F1 REMARKS'; b.classList.remove('ok'); }}, 2000);
        }}).catch(() => {{
          const ta = document.createElement('textarea');
          ta.value = txt; ta.style.position='fixed'; ta.style.opacity='0';
          document.body.appendChild(ta); ta.select();
          document.execCommand('copy'); document.body.removeChild(ta);
          const b = document.getElementById('btn');
          b.textContent = '✅ COPIED!';
          b.classList.add('ok');
          setTimeout(() => {{ b.textContent = '📋 COPY F1 REMARKS'; b.classList.remove('ok'); }}, 2000);
        }});
      }}
    </script>
    """, height=45)

# ── RFD Quick Reference ────────────────────────────────────
with st.expander("📖 RFD Quick Reference"):
    ref_data = {k: v.split("–")[-1].strip() for k, v in RFD_OPTIONS.items() if k}
    cols = st.columns(2)
    items = list(ref_data.items())
    half = len(items) // 2
    for i, (code, desc) in enumerate(items):
        with cols[0 if i < half else 1]:
            st.markdown(f"**`{code}`** — {desc}")