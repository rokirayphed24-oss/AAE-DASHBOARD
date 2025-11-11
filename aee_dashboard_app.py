# aee_dashboard_app.py
# AEE Dashboard — Professional UI + Animated SO Expansion + Improved Layout

import streamlit as st
import pandas as pd
import random
import datetime
import plotly.express as px
import time

# --------------------------- Page Setup ---------------------------
st.set_page_config(page_title="JJM AEE Dashboard", layout="wide")

AEE_NAME = "Er. ROKI RAY"
SUBDIVISION = "Guwahati Subdivision"

st.markdown(
    """
    <style>
        /* Global page styling */
        .main {
            background-color: #F9FAFB;
        }
        h1, h2, h3 {
            color: #1E3A8A;
            font-weight: 700;
        }
        .metric-box {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            padding: 12px 16px;
            margin-bottom: 12px;
            border-left: 5px solid #3B82F6;
        }
        .so-card {
            border-radius: 12px;
            background-color: white;
            box-shadow: 0 3px 8px rgba(0,0,0,0.07);
            padding: 10px 16px;
            margin-bottom: 10px;
            transition: all 0.25s ease-in-out;
        }
        .so-card:hover {
            transform: scale(1.01);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💧 Jal Jeevan Mission — Assistant Executive Engineer Dashboard")
st.markdown(f"### Subdivision: **{SUBDIVISION}**")
st.markdown(f"**AEE Name:** {AEE_NAME}")
st.markdown(f"**DATE:** {datetime.date.today().strftime('%A, %d %B %Y').upper()}")
st.markdown("---")

# --------------------------- Generate Aggregated Demo Data ---------------------------
def generate_aee_demo_data(num_sos=14, schemes_per_so=20):
    sos = [
        "Roki Ray", "Sanjay Das", "Anup Bora", "Ranjit Kalita", "Bikash Deka", "Manoj Das", "Dipankar Nath",
        "Himangshu Deka", "Kamal Choudhury", "Rituraj Das", "Debojit Gogoi", "Utpal Saikia", "Pritam Bora", "Amit Baruah"
    ][:num_sos]

    data = []
    all_schemes = []
    for so in sos:
        func_count = random.randint(10, schemes_per_so)
        non_func_count = schemes_per_so - func_count
        updated_today = random.randint(int(func_count * 0.5), func_count)
        total_water = round(random.uniform(300, 1500), 2)
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
        for i in range(schemes_per_so):
            scheme_type = "Functional" if random.random() > 0.25 else "Non-Functional"
            all_schemes.append({
                "SO": so,
                "Scheme": f"{so.split()[0]}_Scheme_{i+1}",
                "Functionality": scheme_type
            })
    return pd.DataFrame(data), pd.DataFrame(all_schemes)

# Generate base data
aee_base_metrics, scheme_df = generate_aee_demo_data()

# --------------------------- Overview Charts ---------------------------
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Scheme Functionality Overview")
    func_counts = scheme_df["Functionality"].value_counts()
    fig1 = px.pie(
        names=func_counts.index,
        values=func_counts.values,
        color=func_counts.index,
        color_discrete_map={"Functional": "#22C55E", "Non-Functional": "#EF4444"}
    )
    fig1.update_traces(textinfo="percent+label", pull=[0.03, 0])
    st.plotly_chart(fig1, use_container_width=True, height=280)

with col2:
    st.markdown("### SO Updates (Today)")
    updated_total = aee_base_metrics["Updated Today"].sum()
    total_possible = aee_base_metrics["Functional Schemes"].sum()
    df_upd = pd.DataFrame({"status": ["Updated", "Not Updated"],
                           "count": [updated_total, total_possible - updated_total]})
    fig2 = px.pie(
        df_upd,
        names="status",
        values="count",
        color="status",
        color_discrete_map={"Updated": "#16A34A", "Not Updated": "#DC2626"}
    )
    fig2.update_traces(textinfo="percent+label", pull=[0.05, 0])
    st.plotly_chart(fig2, use_container_width=True, height=280)

st.markdown("---")

# --------------------------- Duration Filter ---------------------------
st.subheader("🏅 Section Officer Performance Summary (Across Subdivision)")
days_filter = st.selectbox("📅 Duration", [7, 15, 30], index=0)
st.markdown(f"Showing results for **last {days_filter} days**.")
st.markdown("---")

# --------------------------- Data Transformation ---------------------------
aee_metrics = aee_base_metrics.copy()
aee_metrics["Updated Days"] = aee_metrics["Updated Today"] * (days_filter / 7)
aee_metrics["Total Water (m³)"] = aee_metrics["Total Water (m³)"] * (days_filter / 7)

max_water = aee_metrics["Total Water (m³)"].max()
aee_metrics["Score"] = 0.5 * (aee_metrics["Updated Days"] / days_filter) + \
                       0.5 * (aee_metrics["Total Water (m³)"] / max_water)
aee_metrics = aee_metrics.sort_values(by="Score", ascending=False).reset_index(drop=True)
aee_metrics.insert(0, "Rank", range(1, len(aee_metrics) + 1))

if "expanded_so" not in st.session_state:
    st.session_state["expanded_so"] = None

# --------------------------- Helper: Animated Chart Expansion ---------------------------
def show_inline_chart(so_name, accent_color):
    random.seed(hash(so_name) % 9999)
    dates = [(datetime.date.today() - datetime.timedelta(days=i)).isoformat() for i in reversed(range(days_filter))]
    water_values = [round(random.uniform(40, 100), 2) for _ in range(days_filter)]
    df_chart = pd.DataFrame({"Date": dates, "Water Supplied (m³)": water_values})

    total = sum(water_values)
    updated_days = sum(1 for v in water_values if v > 0)
    score = round((updated_days / days_filter) * 0.5 + (total / (days_filter * 100)) * 0.5, 3)

    with st.container():
        st.markdown(
            f"""
            <div style='background:white;border:2px solid {accent_color};border-radius:10px;
                        padding:10px 15px;margin:8px 0;'>
                <b>Days Updated:</b> {updated_days}/{days_filter} | 
                <b>Total Water:</b> {total:.2f} m³ | 
                <b>Score:</b> {score:.3f}
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig = px.area(df_chart, x="Date", y="Water Supplied (m³)",
                      title=f"{so_name} — Water Supplied (Last {days_filter} Days)")
        fig.update_traces(line_color=accent_color, fillcolor=f"{accent_color}33")
        fig.update_layout(showlegend=False, height=260, margin=dict(l=30, r=30, t=40, b=20),
                          paper_bgcolor="white", plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

# --------------------------- Tables ---------------------------
col_t, col_w = st.columns(2)
top_table = aee_metrics.head(7).copy()
worst_table = aee_metrics.tail(7).sort_values(by="Score", ascending=True).reset_index(drop=True)

# --------------------------- Top 7 ---------------------------
with col_t:
    st.markdown("### 🟢 Top 7 Performing SOs")
    for _, row in top_table.iterrows():
        so = row["SO Name"]
        with st.container():
            st.markdown(
                f"""
                <div class="so-card" style="border-left:5px solid #22C55E;">
                    <b>{row['Rank']}. {so}</b><br>
                    Functional: {row['Functional Schemes']} | Updated Days: {row['Updated Days']:.0f} |
                    Total Water: {row['Total Water (m³)']:.2f} | Score: {row['Score']:.3f}
                </div>
                """, unsafe_allow_html=True
            )
            if st.button(f"View {so}", key=f"expand_top_{so}"):
                st.session_state["expanded_so"] = so if st.session_state["expanded_so"] != so else None
            if st.session_state["expanded_so"] == so:
                time.sleep(0.1)
                show_inline_chart(so, "#22C55E")

# --------------------------- Worst 7 ---------------------------
with col_w:
    st.markdown("### 🔴 Worst 7 Performing SOs")
    for _, row in worst_table.iterrows():
        so = row["SO Name"]
        with st.container():
            st.markdown(
                f"""
                <div class="so-card" style="border-left:5px solid #EF4444;">
                    <b>{row['Rank']}. {so}</b><br>
                    Functional: {row['Functional Schemes']} | Updated Days: {row['Updated Days']:.0f} |
                    Total Water: {row['Total Water (m³)']:.2f} | Score: {row['Score']:.3f}
                </div>
                """, unsafe_allow_html=True
            )
            if st.button(f"View {so}", key=f"expand_worst_{so}"):
                st.session_state["expanded_so"] = so if st.session_state["expanded_so"] != so else None
            if st.session_state["expanded_so"] == so:
                time.sleep(0.1)
                show_inline_chart(so, "#EF4444")

st.markdown("---")
st.subheader("📤 Export Summary")
st.download_button(
    "📁 Download All AEE Metrics CSV",
    aee_metrics.to_csv(index=False).encode("utf-8"),
    file_name=f"aee_metrics_{days_filter}days.csv",
)
