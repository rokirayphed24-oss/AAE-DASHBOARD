# aee_dashboard_app.py
# Jal Jeevan Mission — Assistant Executive Engineer (AEE) Dashboard
# Aggregated overview across multiple Section Officers (SOs)
# Shows functionality summary, updates summary, and per-SO performance list

import streamlit as st
import pandas as pd
import random
import datetime
import plotly.express as px

# --------------------------- Page Setup ---------------------------
st.set_page_config(page_title="JJM AEE Dashboard", layout="wide")
st.title("💧 Jal Jeevan Mission — AEE Dashboard")
st.markdown("Overview of all Section Officers (SOs) under your division.")
st.markdown("---")

# --------------------------- Generate Aggregated Demo Data ---------------------------
def generate_aee_demo_data(num_sos=5, schemes_per_so=15):
    """Simulate data aggregated from multiple SO dashboards."""
    sos = ["Roki Ray", "Sanjay Das", "Anup Bora", "Ranjit Kalita", "Bikash Deka", "Manoj Das", "Dipankar Nath"]
    sos = sos[:num_sos]

    data = []
    all_schemes = []
    today = datetime.date.today()

    for so in sos:
        func_count = random.randint(8, schemes_per_so)
        non_func_count = schemes_per_so - func_count
        total_func = func_count + non_func_count
        updated_today = random.randint(int(func_count * 0.6), func_count)

        schemes = [f"{so.split()[0]}_Scheme_{i}" for i in range(total_func)]
        for s in schemes:
            scheme_type = "Functional" if random.random() > 0.25 else "Non-Functional"
            all_schemes.append({"SO": so, "Scheme": s, "Functionality": scheme_type})

        total_water = round(random.uniform(200, 1200), 2)
        data.append({
            "SO Name": so,
            "Functional Schemes": func_count,
            "Non-Functional Schemes": non_func_count,
            "Total Schemes": total_func,
            "Updated Today": updated_today,
            "Total Water (m³)": total_water,
            "Score": round((updated_today/func_count)*0.5 + (total_water/1200)*0.5, 3)
        })

    return pd.DataFrame(data), pd.DataFrame(all_schemes)

aee_metrics, scheme_df = generate_aee_demo_data()

# --------------------------- Overview Pie Charts ---------------------------
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Scheme Functionality Overview")
    func_counts = scheme_df["Functionality"].value_counts()
    fig1 = px.pie(
        names=func_counts.index,
        values=func_counts.values,
        color=func_counts.index,
        color_discrete_map={"Functional": "#4CAF50", "Non-Functional": "#F44336"},
    )
    fig1.update_traces(textinfo="percent+label")
    st.plotly_chart(fig1, use_container_width=True, height=300)

with col2:
    st.markdown("### SO Updates (Today)")
    updated_total = aee_metrics["Updated Today"].sum()
    total_possible = aee_metrics["Functional Schemes"].sum()
    df_upd = pd.DataFrame(
        {"status": ["Updated", "Not Updated"], "count": [updated_total, total_possible - updated_total]}
    )
    fig2 = px.pie(
        df_upd,
        names="status",
        values="count",
        color="status",
        color_discrete_map={"Updated": "#4CAF50", "Not Updated": "#F44336"},
    )
    fig2.update_traces(textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True, height=300)

st.markdown("---")

# --------------------------- SO Performance Table ---------------------------
st.subheader("📊 Section Officer (SO) Performance Summary")

aee_metrics = aee_metrics.sort_values(by="Score", ascending=False).reset_index(drop=True)
aee_metrics.insert(0, "Rank", range(1, len(aee_metrics) + 1))

# Styled table
st.dataframe(
    aee_metrics.style.format({"Total Water (m³)": "{:.2f}", "Score": "{:.3f}"})
    .background_gradient(subset=["Score"], cmap="Greens"),
    use_container_width=True,
    height=400,
)

st.info("💡 Tap on an SO Name (coming soon) to open their full dashboard view.")

# --------------------------- Export ---------------------------
st.markdown("---")
st.subheader("📤 Export Summary")
st.download_button(
    "Download AEE Metrics CSV",
    aee_metrics.to_csv(index=False).encode("utf-8"),
    file_name="aee_dashboard_metrics.csv",
)
st.download_button(
    "Download Scheme Functionality CSV",
    scheme_df.to_csv(index=False).encode("utf-8"),
    file_name="scheme_functionality.csv",
)

st.success("✅ Demo data for AEE Dashboard generated successfully.")
