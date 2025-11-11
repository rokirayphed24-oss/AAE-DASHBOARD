# aee_dashboard_app.py
# AEE Dashboard — Fixed inline click issue + improved visibility for SO chart sections

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
    for so in sos:
        func_count = random.randint(10, schemes_per_so)
        non_func_count = schemes_per_so - func_count
        updated_today = random.randint(int(func_count * 0.5), func_count)
        total_water = round(random.uniform(300, 1500), 2)
        score = round((updated_today / func_count) * 0.5 + (total_water / 1500) * 0.5, 3)

        for i in range(schemes_per_so):
            scheme_type = "Functional" if random.random() > 0.25 else "Non-Functional"
            all_schemes.append({"SO": so, "Scheme": f"{so.split()[0]}_Scheme_{i+1}", "Functionality": scheme_type})

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

# Generate base data
aee_base_metrics, scheme_df = generate_aee_demo_data()

# --------------------------- Overview Charts ---------------------------
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Scheme Functionality Overview")
    func_counts = scheme_df["Functionality"].value_counts()
    fig1 = px.pie(names=func_counts.index, values=func_counts.values,
                  color=func_counts.index,
                  color_discrete_map={"Functional": "#4CAF50", "Non-Functional": "#F44336"})
    fig1.update_traces(textinfo="percent+label")
    st.plotly_chart(fig1, use_container_width=True, height=300)

with col2:
    st.markdown("### SO Updates (Today)")
    updated_total = aee_base_metrics["Updated Today"].sum()
    total_possible = aee_base_metrics["Functional Schemes"].sum()
    df_upd = pd.DataFrame({"status": ["Updated", "Not Updated"],
                           "count": [updated_total, total_possible - updated_total]})
    fig2 = px.pie(df_upd, names="status", values="count",
                  color="status",
                  color_discrete_map={"Updated": "#4CAF50", "Not Updated": "#F44336"})
    fig2.update_traces(textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True, height=300)

st.markdown("---")

# --------------------------- Duration Filter ---------------------------
st.subheader("🏅 Section Officer Performance Summary (Across Subdivision)")
days_filter = st.selectbox("Select Duration", [7, 15, 30], index=0)
st.markdown(f"Showing performance for **last {days_filter} days**")

# --------------------------- Transform Data ---------------------------
aee_metrics = aee_base_metrics.copy()
aee_metrics["Updated Days"] = aee_metrics["Updated Today"] * (days_filter / 7)
aee_metrics["Total Water (m³)"] = aee_metrics["Total Water (m³)"] * (days_filter / 7)

max_water = aee_metrics["Total Water (m³)"].max()
aee_metrics["Score"] = 0.5 * (aee_metrics["Updated Days"] / days_filter) + \
                       0.5 * (aee_metrics["Total Water (m³)"] / max_water)
aee_metrics = aee_metrics.sort_values(by="Score", ascending=False).reset_index(drop=True)
aee_metrics.insert(0, "Rank", range(1, len(aee_metrics) + 1))

# --------------------------- Session Key ---------------------------
if "expanded_so" not in st.session_state:
    st.session_state["expanded_so"] = None

# --------------------------- Helper: Show Inline Chart ---------------------------
def show_inline_chart(so_name, border_color):
    """Display a static, visible chart and summary inside a styled box."""
    random.seed(hash(so_name) % 10000)
    dates = [(datetime.date.today() - datetime.timedelta(days=i)).isoformat() for i in reversed(range(days_filter))]
    water_values = [round(random.uniform(30, 100), 2) for _ in range(days_filter)]
    df_chart = pd.DataFrame({"Date": dates, "Water Supplied (m³)": water_values})
    total_water = sum(water_values)
    days_active = sum(1 for v in water_values if v > 0)
    avg_score = round((days_active / days_filter) * 0.5 + (total_water / (days_filter * 100)) * 0.5, 3)

    st.markdown(
        f"""
        <div style="background-color:white; border:2px solid {border_color};
                    border-radius:10px; padding:10px; margin-top:5px;">
            <b>Days Updated:</b> {days_active}/{days_filter} |
            <b>Total Water:</b> {total_water:.2f} m³ |
            <b>Score:</b> {avg_score:.3f}
        </div>
        """, unsafe_allow_html=True
    )

    fig = px.area(df_chart, x="Date", y="Water Supplied (m³)",
                  title=f"{so_name} — Water Supplied (Last {days_filter} Days)",
                  markers=False)
    fig.update_traces(line_color=border_color, fillcolor=f"rgba(33,150,243,0.2)")
    fig.update_layout(showlegend=False, height=250,
                      margin=dict(l=30, r=30, t=40, b=20),
                      paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

# --------------------------- Tables ---------------------------
top_table = aee_metrics.head(7).copy()
worst_table = aee_metrics.tail(7).sort_values(by="Score", ascending=True).reset_index(drop=True)

col_t, col_w = st.columns(2)

# --------------------------- Top Performing SOs ---------------------------
with col_t:
    st.markdown("### 🟢 Top 7 Performing SOs")
    for _, row in top_table.iterrows():
        so = row["SO Name"]
        with st.container():
            clicked = st.button(f"{row['Rank']}. {so}", key=f"top_{so}")
            if clicked:
                st.session_state["expanded_so"] = so if st.session_state["expanded_so"] != so else None

            st.markdown(
                f"<div style='background-color:rgba(76,175,80,0.1);padding:8px;border-radius:8px;border:1px solid #81C784;'>"
                f"<b>Functional:</b> {row['Functional Schemes']} | "
                f"<b>Updated Days:</b> {row['Updated Days']:.0f} | "
                f"<b>Total Water:</b> {row['Total Water (m³)']:.2f} | "
                f"<b>Score:</b> {row['Score']:.3f}</div>",
                unsafe_allow_html=True,
            )
            if st.session_state["expanded_so"] == so:
                show_inline_chart(so, "#4CAF50")

# --------------------------- Worst Performing SOs ---------------------------
with col_w:
    st.markdown("### 🔴 Worst 7 Performing SOs")
    for _, row in worst_table.iterrows():
        so = row["SO Name"]
        with st.container():
            clicked = st.button(f"{row['Rank']}. {so}", key=f"worst_{so}")
            if clicked:
                st.session_state["expanded_so"] = so if st.session_state["expanded_so"] != so else None

            st.markdown(
                f"<div style='background-color:rgba(244,67,54,0.1);padding:8px;border-radius:8px;border:1px solid #E57373;'>"
                f"<b>Functional:</b> {row['Functional Schemes']} | "
                f"<b>Updated Days:</b> {row['Updated Days']:.0f} | "
                f"<b>Total Water:</b> {row['Total Water (m³)']:.2f} | "
                f"<b>Score:</b> {row['Score']:.3f}</div>",
                unsafe_allow_html=True,
            )
            if st.session_state["expanded_so"] == so:
                show_inline_chart(so, "#F44336")

st.markdown("---")

# --------------------------- Export ---------------------------
st.subheader("📤 Export Summary")
st.download_button(
    "📁 Download All AEE Metrics CSV",
    aee_metrics.to_csv(index=False).encode("utf-8"),
    file_name=f"aee_metrics_{days_filter}days.csv",
)
st.download_button(
    "📁 Download Scheme Functionality CSV",
    scheme_df.to_csv(index=False).encode("utf-8"),
    file_name="aee_scheme_functionality.csv",
)

st.success(f"✅ Dashboard ready for {AEE_NAME} — {SUBDIVISION}. Data auto-generated successfully for last {days_filter} days.")
