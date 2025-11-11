# aee_dashboard_app.py
# Jal Jeevan Mission — Assistant Executive Engineer (AEE) Dashboard
# Aggregated overview across 14 Section Officers (SOs)
# Shows functionality summary, update summary, top & worst SOs, AEE info, and export options

import streamlit as st
import pandas as pd
import random
import datetime
import plotly.express as px

# --------------------------- Page Setup ---------------------------
st.set_page_config(page_title="JJM AEE Dashboard", layout="wide")

AEE_NAME = "Er. ROKI RAY"
SUBDIVISION = "Guwahati Subdivision"

st.title("💧 Jal Jeevan Mission — Assistant Executive Engineer Dashboard")
st.markdown(f"### Subdivision: **{SUBDIVISION}**")
st.markdown(f"**AEE Name:** {AEE_NAME}")
st.markdown(f"**DATE:** {datetime.date.today().strftime('%A, %d %B %Y').upper()}")
st.markdown("---")

# --------------------------- Generate Aggregated Demo Data ---------------------------
def generate_aee_demo_data(num_sos=14, schemes_per_so=20):
    """Simulate data aggregated from multiple SO dashboards."""
    sos = [
        "Roki Ray", "Sanjay Das", "Anup Bora", "Ranjit Kalita", "Bikash Deka", "Manoj Das", "Dipankar Nath",
        "Himangshu Deka", "Kamal Choudhury", "Rituraj Das", "Debojit Gogoi", "Utpal Saikia", "Pritam Bora", "Amit Baruah"
    ]
    sos = sos[:num_sos]

    data = []
    all_schemes = []
    today = datetime.date.today()

    for so in sos:
        func_count = random.randint(10, schemes_per_so)
        non_func_count = schemes_per_so - func_count
        updated_today = random.randint(int(func_count * 0.5), func_count)
        total_water = round(random.uniform(300, 1500), 2)

        # create fake scheme list
        for i in range(schemes_per_so):
            scheme_type = "Functional" if random.random() > 0.25 else "Non-Functional"
            all_schemes.append({"SO": so, "Scheme": f"{so.split()[0]}_Scheme_{i+1}", "Functionality": scheme_type})

        # compute score (half weight for updates, half for water)
        score = round((updated_today / func_count) * 0.5 + (total_water / 1500) * 0.5, 3)

        data.append({
            "SO Name": so,
            "Functional Schemes": func_count,
            "Non-Functional Schemes": non_func_count,
            "Total Schemes": func_count + non_func_count,
            "Updated Today": updated_today,
            "Total Water (m³)": total_water,
            "Score": score
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

# --------------------------- Performance Rankings ---------------------------
st.subheader("🏅 Section Officer Performance Summary (Across Subdivision)")

# sort and rank
aee_metrics = aee_metrics.sort_values(by="Score", ascending=False).reset_index(drop=True)
aee_metrics.insert(0, "Rank", range(1, len(aee_metrics) + 1))

# Top 7 and Worst 7
top_table = aee_metrics.head(7).copy()
worst_table = aee_metrics.tail(7).sort_values(by="Score", ascending=True).reset_index(drop=True)

col_t, col_w = st.columns(2)
with col_t:
    st.markdown("### 🟢 Top 7 Performing SOs")
    st.dataframe(
        top_table.style.format({"Total Water (m³)": "{:.2f}", "Score": "{:.3f}"})
        .background_gradient(subset=["Functional Schemes", "Updated Today", "Score"], cmap="Greens")
        .set_table_styles([{"selector": "th", "props": [("font-weight", "600")]}]),
        use_container_width=True,
        height=380,
    )
    st.download_button("⬇️ Download Top 7 CSV", top_table.to_csv(index=False).encode("utf-8"), file_name="aee_top_7.csv")

with col_w:
    st.markdown("### 🔴 Worst 7 Performing SOs")
    st.dataframe(
        worst_table.style.format({"Total Water (m³)": "{:.2f}", "Score": "{:.3f}"})
        .background_gradient(subset=["Functional Schemes", "Updated Today", "Score"], cmap="Reds_r")
        .set_table_styles([{"selector": "th", "props": [("font-weight", "600")]}]),
        use_container_width=True,
        height=380,
    )
    st.download_button("⬇️ Download Worst 7 CSV", worst_table.to_csv(index=False).encode("utf-8"), file_name="aee_worst_7.csv")

st.markdown("---")

# --------------------------- Export ---------------------------
st.subheader("📤 Export Summary")
st.download_button(
    "📁 Download All AEE Metrics CSV",
    aee_metrics.to_csv(index=False).encode("utf-8"),
    file_name="aee_metrics_full.csv",
)
st.download_button(
    "📁 Download Scheme Functionality CSV",
    scheme_df.to_csv(index=False).encode("utf-8"),
    file_name="aee_scheme_functionality.csv",
)

st.success(f"✅ Dashboard ready for {AEE_NAME} — {SUBDIVISION}. Data auto-generated successfully.")
