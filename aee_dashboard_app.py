# aee_dashboard_app.py
# AEE Dashboard — Pie charts restored + Top/Worst tables + clickable SO view
# - Shows Functionality pie and SO Updates pie (uses plotly if available)
# - Top 7 / Worst 7 tables (styled), SO names as buttons below each table
# - Clicking a name shows a non-interactive matplotlib chart and a small summary

import streamlit as st
import pandas as pd
import random
import datetime
import matplotlib.pyplot as plt

# try to import plotly for nicer pies; fallback if missing
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False

# --------------------------- Page setup ---------------------------
st.set_page_config(page_title="JJM AEE Dashboard", layout="wide")
AEE_NAME = "Er. ROKI RAY"
SUBDIVISION = "Guwahati Subdivision"

st.title("💧 Jal Jeevan Mission — AEE Dashboard")
st.markdown(f"**Subdivision:** {SUBDIVISION}  •  **AEE:** {AEE_NAME}")
st.markdown(f"**DATE:** {datetime.date.today().strftime('%A, %d %B %Y').upper()}")
st.markdown("---")

# --------------------------- Demo data generator ---------------------------
def generate_aee_demo_data(num_sos=14, schemes_per_so=20):
    sos = [
        "Roki Ray", "Sanjay Das", "Anup Bora", "Ranjit Kalita", "Bikash Deka", "Manoj Das", "Dipankar Nath",
        "Himangshu Deka", "Kamal Choudhury", "Rituraj Das", "Debojit Gogoi", "Utpal Saikia", "Pritam Bora", "Amit Baruah"
    ][:num_sos]

    records = []
    scheme_rows = []
    # create per-SO aggregated numbers (base for 7-day window)
    for so in sos:
        func_count = random.randint(10, schemes_per_so)
        non_func_count = schemes_per_so - func_count
        updated_today = random.randint(int(func_count * 0.5), func_count)
        total_water_7d = round(random.uniform(300, 1500), 2)  # interpret as 7-day baseline
        records.append({
            "SO Name": so,
            "Functional Schemes": func_count,
            "Non-Functional Schemes": non_func_count,
            "Total Schemes": func_count + non_func_count,
            "Updated Today (7d-baseline)": updated_today,
            "Total Water (7d-baseline m³)": total_water_7d
        })
        for i in range(schemes_per_so):
            scheme_rows.append({"SO": so, "Scheme": f"{so.split()[0]}_Scheme_{i+1}",
                                "Functionality": "Functional" if random.random() > 0.25 else "Non-Functional"})
    return pd.DataFrame(records), pd.DataFrame(scheme_rows)

base_metrics, scheme_df = generate_aee_demo_data()

# --------------------------- Overview pies (plotly if available) ---------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Scheme Functionality")
    func_counts = scheme_df["Functionality"].value_counts()
    if PLOTLY_AVAILABLE:
        fig = px.pie(names=func_counts.index, values=func_counts.values,
                     color=func_counts.index,
                     color_discrete_map={"Functional": "#4CAF50", "Non-Functional": "#F44336"},
                     title="")
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True, height=300)
    else:
        st.write(func_counts.to_frame(name="Count"))

with col2:
    st.subheader("SO Updates (today baseline)")
    total_updated = base_metrics["Updated Today (7d-baseline)"].sum()
    total_func = base_metrics["Functional Schemes"].sum()
    upd_df = pd.DataFrame({"status": ["Updated", "Absent"],
                           "count": [int(total_updated), int(max(total_func - total_updated, 0))]})
    if PLOTLY_AVAILABLE:
        fig2 = px.pie(upd_df, names="status", values="count",
                      color="status", color_discrete_map={"Updated":"#4CAF50","Absent":"#F44336"})
        fig2.update_traces(textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True, height=300)
    else:
        st.write(upd_df)

st.markdown("---")

# --------------------------- Duration selector ---------------------------
st.subheader("Section Officer Performance (AEE view)")
days = st.selectbox("Select window", [7, 15, 30], index=0, format_func=lambda x: f"{x} days")
st.markdown(f"Showing results for last **{days} days**")
st.markdown("")

# --------------------------- Compute metrics for selected window ---------------------------
def compute_period_metrics(base_df: pd.DataFrame, days: int):
    # base_df has 7-day baseline numbers; scale to chosen days
    df = base_df.copy()
    # scale Updated baseline proportionally (assume Updated Today baseline for 7-day window)
    df["Days Updated (last N)"] = (df["Updated Today (7d-baseline)"] * (days / 7)).round().astype(int)
    df["Total Water (m³)"] = (df["Total Water (7d-baseline m³)"] * (days / 7)).round(2)
    # score: 50% frequency (days updated / days) + 50% quantity scaled by max
    max_water = df["Total Water (m³)"].max() if not df["Total Water (m³)"].empty else 1.0
    df["Score"] = (0.5 * (df["Days Updated (last N)"] / days)) + (0.5 * (df["Total Water (m³)"] / max_water))
    df = df.sort_values(by=["Score", "Total Water (m³)"], ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df

metrics = compute_period_metrics(base_metrics, days)

# --------------------------- Top & Worst tables (styled) ---------------------------
top7 = metrics.head(7).copy()
worst7 = metrics.tail(7).sort_values(by="Score", ascending=True).reset_index(drop=True)

st.markdown("#### Top 7 Performing SOs")
st.dataframe(
    top7.style.format({
        "Total Water (m³)": "{:.2f}",
        "Score": "{:.3f}"
    }).background_gradient(subset=["Days Updated (last N)", "Total Water (m³)", "Score"], cmap="Greens")
, use_container_width=True, height=300)

st.markdown("#### Worst 7 Performing SOs")
st.dataframe(
    worst7.style.format({
        "Total Water (m³)": "{:.2f}",
        "Score": "{:.3f}"
    }).background_gradient(subset=["Days Updated (last N)", "Total Water (m³)", "Score"], cmap="Reds_r")
, use_container_width=True, height=300)

st.markdown("---")

# --------------------------- Clickable SO names below tables ---------------------------
st.subheader("Open SO Dashboard (click a name)")

left_col, right_col = st.columns(2)

with left_col:
    st.markdown("**Top 7 — click to view**")
    for i, r in top7.iterrows():
        name = r["SO Name"]
        if st.button(f"{r['Rank']}. {name}", key=f"topbtn_{name}_{days}"):
            st.session_state["aee_selected_so"] = name

with right_col:
    st.markdown("**Worst 7 — click to view**")
    for i, r in worst7.iterrows():
        name = r["SO Name"]
        if st.button(f"{r['Rank']}. {name}", key=f"worstbtn_{name}_{days}"):
            st.session_state["aee_selected_so"] = name

# --------------------------- Show SO dashboard-like view when selected ---------------------------
if "aee_selected_so" in st.session_state and st.session_state["aee_selected_so"]:
    so_name = st.session_state["aee_selected_so"]
    st.markdown("---")
    st.subheader(f"Section Officer Dashboard — {so_name}")
    # find metrics row
    row = metrics[metrics["SO Name"] == so_name].iloc[0]

    # summary (visible card)
    st.markdown(
        f"""
        <div style="background:#ffffff;border:1px solid #e6e6e6;padding:12px;border-radius:8px;">
          <b>SO:</b> {so_name} &nbsp;&nbsp; | &nbsp;&nbsp;
          <b>Days Updated:</b> {int(row['Days Updated (last N)'])}/{days} &nbsp;&nbsp; | &nbsp;&nbsp;
          <b>Total Water:</b> {row['Total Water (m³)']:.2f} m³ &nbsp;&nbsp; | &nbsp;&nbsp;
          <b>Score:</b> {row['Score']:.3f}
        </div>
        """,
        unsafe_allow_html=True
    )

    # simulate daily data for this SO (deterministic by seed)
    random.seed(hash(so_name) % 9999)
    dates = [(datetime.date.today() - datetime.timedelta(days=i)).isoformat() for i in reversed(range(days))]
    vals = [round(random.uniform(30, 100), 2) for _ in range(days)]
    daily_df = pd.DataFrame({"Date": dates, "Water (m³)": vals})

    # non-interactive matplotlib bar chart (compact)
    fig, ax = plt.subplots(figsize=(8, 2.8))
    ax.bar(daily_df["Date"], daily_df["Water (m³)"], color="#2b7a0b")
    ax.set_xlabel("Date")
    ax.set_ylabel("Water (m³)")
    ax.set_title(f"{so_name} — Daily Water Supplied (Last {days} days)")
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    plt.tight_layout()
    st.pyplot(fig)

    # Close button
    if st.button("Close SO View", key=f"close_so_{so_name}_{days}"):
        st.session_state["aee_selected_so"] = None

st.markdown("---")
st.subheader("Export")
st.download_button("Download AEE metrics (CSV)", metrics.to_csv(index=False).encode("utf-8"), file_name=f"aee_metrics_{days}d.csv")
st.download_button("Download Scheme list (CSV)", scheme_df.to_csv(index=False).encode("utf-8"), file_name="aee_schemes.csv")
st.success("AEE dashboard ready.")
