import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ---------------- Page setup ----------------
st.set_page_config(page_title="Technical Support Representative Talent Pool", layout="wide")

# Widen the sidebar so long slider labels don't get cut off
st.markdown("""
    <style>
    /* Adjust sidebar width (tweak values if needed) */
    [data-testid="stSidebar"] {min-width: 380px; max-width: 440px;}
    </style>
""", unsafe_allow_html=True)

st.title("Technical Support Representative Talent Pool")

# ---------------- Load CSV ----------------
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
with st.sidebar:
    st.subheader("Filters")

    # Clear all filters
    if st.button("Clear all filters"):
        ss.city = "All"
        ss.company = "All"
        ss.active = "All"
        ss.game = "All"
        ss.it_range = (0, max_it)
        ss.tr_range = (0, max_tr)
        ss.win_range = (0, max_win)
        ss.net_range = (0, max_net)
        ss.m36_range = (0, max_m36)
        st.rerun()

    # Dropdowns
    ss.city = st.selectbox("City", options=cities, index=(cities.index(ss.city) if ss.city in cities else 0))
    ss.company = st.selectbox("Last Company", options=companies, index=(companies.index(ss.company) if ss.company in companies else 0))

    # Radios
    ss.active = st.radio("Actively Looking", options=["All", "Yes", "No"], index=["All","Yes","No"].index(ss.active))
    ss.game   = st.radio("Gaming/Films Experience", options=["All", "Yes", "No"], index=["All","Yes","No"].index(ss.game))

    # Range sliders for X/Y metrics (top)
    ss.it_range = st.slider(
        "Total IT Experience (years)",
        min_value=0, max_value=max_it,
        value=tuple(ss.it_range),
        step=1
    )
    ss.tr_range = st.slider(
        "Troubleshooting Experience (years)",
        min_value=0, max_value=max_tr,
        value=tuple(ss.tr_range),
        step=1
    )

    # Tech skill range sliders (min–max in one slider)
    ss.win_range = st.slider(
        "Microsoft Windows Server Exp",
        min_value=0, max_value=max_win,
        value=tuple(ss.win_range),
        step=1
    )
    ss.net_range = st.slider(
        "Network Management Exp",
        min_value=0, max_value=max_net,
        value=tuple(ss.net_range),
        step=1
    )
    ss.m36_range = st.slider(
        "Microsoft 365 Exp",
        min_value=0, max_value=max_m36,
        value=tuple(ss.m36_range),
        step=1
    )

# ---------------- Apply filters ----------------
it_lo, it_hi   = ss.it_range
tr_lo, tr_hi   = ss.tr_range
win_lo, win_hi = ss.win_range
net_lo, net_hi = ss.net_range
m36_lo, m36_hi = ss.m36_range

mask = (
    df["Total IT Experience"].between(it_lo, it_hi, inclusive="both") &
    df["Troubleshooting Experience"].between(tr_lo, tr_hi, inclusive="both") &
    df[win_col].between(win_lo, win_hi, inclusive="both") &
    df[net_col].between(net_lo, net_hi, inclusive="both") &
    df[m365_col].between(m36_lo, m36_hi, inclusive="both") &
    ((ss.active == "All") | (df["ActivelyLookingYN"] == ss.active)) &
    ((ss.game   == "All") | (df["GameFilmYN"] == ss.game)) &
    ((ss.city   == "All") | (df["City"].astype(str) == ss.city)) &
    ((ss.company == "All") | (df["Last Company"].astype(str) == ss.company))
)
df_f = df.loc[mask].copy()

# ---------------- Summary stats (top) ----------------
total_candidates = int(len(df_f))
avg_it = float(df_f["Total IT Experience"].mean()) if total_candidates > 0 else 0.0
avg_tr = float(df_f["Troubleshooting Experience"].mean()) if total_candidates > 0 else 0.0

c1, c2, c3 = st.columns(3)
c1.metric("Total Candidates", f"{total_candidates:,}")
c2.metric("Avg Total IT Experience", f"{avg_it:.1f} yrs")
c3.metric("Avg Troubleshooting Experience", f"{avg_tr:.1f} yrs")

# ---------------- Altair chart ----------------
alt.data_transformers.disable_max_rows()
level_sel = alt.selection_point(fields=["Level"], bind="legend", toggle="true")

tooltip_fields = [
    alt.Tooltip("Candidate Name:N", title="Candidate"),
    alt.Tooltip("Total IT Experience:Q", title="Total IT Exp"),
    alt.Tooltip("Troubleshooting Experience:Q", title="Troubleshoot Exp"),
    alt.Tooltip(f"{win_col}:Q",  title="Windows"),
    alt.Tooltip(f"{net_col}:Q",  title="Network"),
    alt.Tooltip(f"{m365_col}:Q", title="Microsoft 365"),
    alt.Tooltip("Level:N", title="Level"),
    alt.Tooltip("Title:N", title="Title"),
    alt.Tooltip("Last Company:N", title="Last Company"),
    alt.Tooltip("City:N", title="City"),
    alt.Tooltip("ActivelyLookingYN:N", title="Actively Looking"),
    alt.Tooltip("GameFilmYN:N", title="Gaming/Films Experience"),
]

chart = (
    alt.Chart(df_f)
      .mark_circle(size=80, opacity=0.75)
      .encode(
          x=alt.X("Total IT Experience:Q", title="Total IT Experience (years)", scale=alt.Scale(domain=[0, 35])),
          y=alt.Y("Troubleshooting Experience:Q", title="Troubleshooting Experience (years)", scale=alt.Scale(domain=[0, 35])),
          color=alt.Color("Level:N", title="Level", scale=alt.Scale(scheme="tableau20")),
          tooltip=tooltip_fields,
      )
      .add_params(level_sel)
      .transform_filter(level_sel)  # interactive legend
      .properties(height=520)
      .interactive()
)

st.altair_chart(chart, use_container_width=True)

# ---------------- Filtered list ----------------
st.subheader("Filtered Candidates")
st.dataframe(df_f.reset_index(drop=True))
