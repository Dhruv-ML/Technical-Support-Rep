import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Technical Support Representative", layout="wide")
st.title("Technical Support Representative")

# -------- Simple CSV loading --------
# Assumes the CSV file is in the same folder with this exact name
df = pd.read_csv("Technical Support.csv")

# Ensure numeric for axes
df["Total IT Experience"] = pd.to_numeric(df["Total IT Experience"], errors="coerce")
df["Troubleshooting Experience"] = pd.to_numeric(df["Troubleshooting Experience"], errors="coerce")

# Normalize Gaming/Films Experience into Yes/No
df["GameFilmYN"] = np.where(
    df["Gaming/Films Experience"].astype(str).str.strip().str.lower().isin(["yes","y","true","1"]),
    "Yes", "No"
)

# -------- Sidebar Filters + Reset --------
if "filters_initialized" not in st.session_state:
    st.session_state.filters_initialized = True
    st.session_state.city = "All"
    st.session_state.company = "All"
    st.session_state.game = "All"
    st.session_state.min_it = 0.0
    st.session_state.min_tr = 0.0

with st.sidebar:
    st.subheader("Filters")
    # Reset button
    if st.button("Reset filters"):
        st.session_state.city = "All"
        st.session_state.company = "All"
        st.session_state.game = "All"
        st.session_state.min_it = 0.0
        st.session_state.min_tr = 0.0
        st.experimental_rerun()

    # Build choices
    cities = ["All"] + sorted(df["City"].dropna().astype(str).unique().tolist())
    companies = ["All"] + sorted(df["Current Company"].dropna().astype(str).unique().tolist())

    max_it = float(df["Total IT Experience"].max()) if not df["Total IT Experience"].dropna().empty else 10.0
    max_tr = float(df["Troubleshooting Experience"].max()) if not df["Troubleshooting Experience"].dropna().empty else 10.0

    st.session_state.city = st.selectbox("City", options=cities, index=cities.index(st.session_state.city) if st.session_state.city in cities else 0)
    st.session_state.company = st.selectbox("Current Company", options=companies, index=companies.index(st.session_state.company) if st.session_state.company in companies else 0)
    st.session_state.game = st.radio("Gaming/Films", options=["All","Yes","No"], index=["All","Yes","No"].index(st.session_state.game))
    st.session_state.min_it = st.slider("Min Total IT exp", min_value=0.0, max_value=max_it, step=0.5, value=float(st.session_state.min_it))
    st.session_state.min_tr = st.slider("Min Troubleshoot exp", min_value=0.0, max_value=max_tr, step=0.5, value=float(st.session_state.min_tr))

# -------- Filter DataFrame --------
mask = (
    (df["Total IT Experience"] >= st.session_state.min_it) &
    (df["Troubleshooting Experience"] >= st.session_state.min_tr) &
    ((st.session_state.city == "All") | (df["City"].astype(str) == st.session_state.city)) &
    ((st.session_state.company == "All") | (df["Current Company"].astype(str) == st.session_state.company)) &
    ((st.session_state.game == "All") | (df["GameFilmYN"] == st.session_state.game))
)
df_f = df.loc[mask].copy()

# -------- Metrics (top of the plot) --------
n_candidates = int(len(df_f))
avg_it = float(df_f["Total IT Experience"].mean()) if n_candidates > 0 else 0.0
avg_tr = float(df_f["Troubleshooting Experience"].mean()) if n_candidates > 0 else 0.0

c1, c2, c3 = st.columns(3)
c1.metric("Total Candidates", f"{n_candidates:,}")
c2.metric("Avg Total IT Experience", f"{avg_it:.1f} yrs")
c3.metric("Avg Troubleshooting Experience", f"{avg_tr:.1f} yrs")

# -------- Chart (no color, fixed size, Y-axis capped at 30) --------
alt.data_transformers.disable_max_rows()

chart = (
    alt.Chart(df_f)
      .mark_circle(size=80, opacity=0.6)
      .encode(
          x=alt.X("Total IT Experience:Q", title="Total IT Experience (years)"),
          y=alt.Y(
              "Troubleshooting Experience:Q",
              title="Troubleshooting Experience (years)",
              scale=alt.Scale(domain=[0, 30])
          ),
          tooltip=[
              alt.Tooltip("Total IT Experience:Q", title="Total IT Exp"),
              alt.Tooltip("Troubleshooting Experience:Q", title="Troubleshoot Exp"),
              alt.Tooltip("City:N", title="City"),
              alt.Tooltip("Current Company:N", title="Company"),
              alt.Tooltip("GameFilmYN:N", title="Gaming/Films"),
          ],
      )
      .properties(height=520)
      .interactive()
)

st.altair_chart(chart, use_container_width=True)

# -------- Filtered list below the plot --------
st.subheader("Filtered Candidates")
st.dataframe(df_f.reset_index(drop=True))
