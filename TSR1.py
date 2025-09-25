import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ---------------- Page setup ----------------
st.set_page_config(page_title="Technical Support Representative Talent Pool", layout="wide")

# Widen sidebar & prevent slider labels from clipping
st.markdown("""
<style>
/* Make the sidebar wider (tweak widths as needed) */
[data-testid="stSidebar"] { min-width: 480px; max-width: 560px; }

/* Give sliders room and prevent clipping of end labels */
[data-testid="stSidebar"] [data-baseweb="slider"] { padding-right: 24px; }
[data-testid="stSidebar"] [data-baseweb="slider"] > div { overflow: visible; }

/* Optional: slightly smaller label font inside sliders */
[data-testid="stSidebar"] [data-baseweb="slider"] span { font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

st.title("Technical Support Representative Talent Pool")

# ---------------- Load CSV ----------------
# Change filename/path if needed. Auto-detects comma or tab delimiters.
CSV_PATH = "Technical Support.csv"
df = pd.read_csv("Technical Supp.csv", encoding="latin1")

# ---------------- Prepare data ----------------
# Coerce numeric fields
df["Total IT Experience"] = pd.to_numeric(df["Total IT Experience"], errors="coerce")
df["Troubleshooting Experience"] = pd.to_numeric(df["Troubleshooting Experience"], errors="coerce")

win_col  = "Microsoft Windows (desktop & server, including Active Directory)"
net_col  = "Network management"
m365_col = "Microsoft 365"
for c in [win_col, net_col, m365_col]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Candidate full name
df["Candidate Name"] = (
    df["First Name"].astype(str).str.strip() + " " + df["Last Name"].astype(str).str.strip()
).str.replace(r"\s+", " ", regex=True).str.strip()

# Normalize radios (Yes/No)
df["ActivelyLookingYN"] = np.where(
    df["Actively Looking"].astype(str).str.strip().str.lower().isin(["yes", "y", "true", "1"]),
    "Yes", "No"
)
df["GameFilmYN"] = np.where(
    df["Gaming/Films Experience"].astype(str).str.strip().str.lower().isin(["yes", "y", "true", "1"]),
    "Yes", "No"
)

# ---------------- Defaults for filters ----------------
cities    = ["All"] + sorted(df["City"].dropna().astype(str).unique().tolist())
companies = ["All"] + sorted(df["Last Company"].dropna().astype(str).unique().tolist())

# Numeric maxima (fallbacks if empty)
max_it  = int(np.nanmax(df["Total IT Experience"])) if df["Total IT Experience"].notna().any() else 35
max_tr  = int(np.nanmax(df["Troubleshooting Experience"])) if df["Troubleshooting Experience"].notna().any() else 35
max_win = int(np.nanmax(df[win_col])) if df[win_col].notna().any() else 10
max_net = int(np.nanmax(df[net_col])) if df[net_col].notna().any() else 10
max_m36 = int(np.nanmax(df[m365_col])) if df[m365_col].notna().any() else 10

# ---------------- Session state init ----------------
ss = st.session_state
ss.setdefault("city", "All")
ss.setdefault("company", "All")
ss.setdefault("active", "All")
ss.setdefault("game", "All")
# Range sliders for X/Y (axes fields)
ss.setdefault("it_range", (0, max_it))
ss.setdefault("tr_range", (0, max_tr))
# Tech ranges
ss.setdefault("win_range", (0, max_win))
ss.setdefault("net_range", (0, max_net))
ss.setdefault("m36_range", (0, max_m36))

# ---------------- Sidebar filters ----------------
with st.sideb
