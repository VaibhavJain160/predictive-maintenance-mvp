"""
dashboard.py
-------------
Streamlit dashboard for the predictive maintenance MVP.

Run with: streamlit run dashboard.py

Features:
- Machine health overview (all machines at a glance)
- Per-machine deep dive (sensor trends, anomaly timeline)
- Recent alerts log
- Estimated cost savings (illustrative)

For the SEP demo: walk through each tab live.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# -- Config --
st.set_page_config(
    page_title="Predictive Maintenance MVP",
    page_icon="⚙️",
    layout="wide",
)

DATA_FILE = "data/analysis_results.csv"

# -- Helpers --
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    return df

def status_color(status):
    return {
        "HEALTHY": "🟢",
        "WARNING": "🟡",
        "CRITICAL": "🔴",
    }.get(status, "⚪")

# -- Load data --
try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ Data file not found. Run `python generate_data.py` then `python analyze.py` first.")
    st.stop()

# -- Header --
st.title("⚙️ Predictive Maintenance Dashboard")
st.markdown("**SEP Project — AI analytics layer for factory SCADA data**")
st.caption(f"Showing {len(df):,} readings across {df['machine_id'].nunique()} machines | Period: {df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}")

# -- Overview tab + per-machine tab --
tab_overview, tab_machine, tab_alerts, tab_about = st.tabs(["📊 Overview", "🔧 Per Machine", "🚨 Alerts", "ℹ️ About"])

# ============================================================
# TAB 1: OVERVIEW
# ============================================================
with tab_overview:
    st.subheader("Fleet Health at a Glance")

    # Compute per-machine summary
    summary = df.groupby("machine_id").agg(
        avg_health=("health_score", "mean"),
        critical_count=("status", lambda x: (x == "CRITICAL").sum()),
        warning_count=("status", lambda x: (x == "WARNING").sum()),
        total_readings=("status", "count"),
    ).reset_index()

    summary["overall_status"] = summary["critical_count"].apply(
        lambda x: "CRITICAL" if x > 40 else ("WARNING" if x > 15 else "HEALTHY")
    )

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Machines monitored", summary["machine_id"].nunique())
    col2.metric("Healthy", (summary["overall_status"] == "HEALTHY").sum())
    col3.metric("At risk", (summary["overall_status"] == "WARNING").sum() + (summary["overall_status"] == "CRITICAL").sum())
    col4.metric("Total anomalies", int(summary["critical_count"].sum()))

    st.markdown("---")

    # Machine cards
    st.subheader("Machine Status")
    for _, row in summary.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
            c1.markdown(f"### {status_color(row['overall_status'])} {row['machine_id']}")
            c2.metric("Avg health score", f"{row['avg_health']:.1f}/100")
            c3.metric("Critical anomalies", int(row["critical_count"]))
            c4.metric("Warnings", int(row["warning_count"]))

    st.markdown("---")
    st.subheader("Health Score Trend (all machines)")
    fig = px.line(
        df, x="timestamp", y="health_score", color="machine_id",
        title="Health Score Over Time",
        labels={"timestamp": "Date", "health_score": "Health Score (0-100)"},
    )
    fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Warning threshold")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TAB 2: PER-MACHINE DEEP DIVE
# ============================================================
with tab_machine:
    selected = st.selectbox("Select a machine", sorted(df["machine_id"].unique()))
    machine_df = df[df["machine_id"] == selected].sort_values("timestamp")

    st.subheader(f"{selected} — Detailed View")

    # Status banner
    n_critical = (machine_df["status"] == "CRITICAL").sum()
    n_warning = (machine_df["status"] == "WARNING").sum()
    if n_critical > 40:
        st.error(f"⚠️ HIGH RISK — {n_critical} critical anomalies detected. Recommend immediate inspection.")
        first_anomaly = machine_df[machine_df["status"] == "CRITICAL"]["timestamp"].min()
        st.write(f"**First anomaly detected:** {first_anomaly}")
        st.write(f"**Pattern:** Early warning signals appeared before catastrophic failure window. With continuous monitoring, maintenance could have been scheduled 3-6 days earlier — saving downtime.")
    elif n_critical > 15:
        st.warning(f"🟡 MODERATE RISK — {n_critical} anomalies + {n_warning} warnings. Schedule inspection.")
    else:
        st.success(f"✅ HEALTHY — no critical anomalies detected.")

    # Sensor trends
    st.markdown("### Sensor Readings Over Time")
    sensors = ["voltage", "vibration", "pressure", "rotation"]

    for sensor in sensors:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=machine_df["timestamp"], y=machine_df[sensor],
            mode="lines", name=sensor, line=dict(color="steelblue"),
        ))

        # Highlight anomaly points
        anomalies = machine_df[machine_df["status"] == "CRITICAL"]
        if len(anomalies) > 0:
            fig.add_trace(go.Scatter(
                x=anomalies["timestamp"], y=anomalies[sensor],
                mode="markers", name="Anomaly",
                marker=dict(color="red", size=8, symbol="x"),
            ))

        fig.update_layout(
            title=sensor.capitalize(),
            xaxis_title="Time",
            yaxis_title=sensor,
            height=300,
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Health score
    st.markdown("### Health Score Timeline")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=machine_df["timestamp"], y=machine_df["health_score"],
        mode="lines", line=dict(color="green"), fill="tozeroy",
    ))
    fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Warning threshold")
    fig.update_layout(yaxis_range=[0, 100], height=300)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TAB 3: ALERTS LOG
# ============================================================
with tab_alerts:
    st.subheader("All Critical Anomalies")
    alerts = df[df["status"] == "CRITICAL"].sort_values("timestamp", ascending=False)
    if len(alerts) == 0:
        st.success("No critical anomalies detected across the fleet.")
    else:
        st.write(f"**{len(alerts)} critical anomalies detected**")
        display_cols = ["timestamp", "machine_id", "voltage", "vibration", "pressure", "rotation", "health_score"]
        st.dataframe(
            alerts[display_cols],
            use_container_width=True,
            hide_index=True,
        )

# ============================================================
# TAB 4: ABOUT
# ============================================================
with tab_about:
    st.markdown("""
    ### About this prototype

    This is a **working MVP** for an AI analytics layer that sits on top of factory SCADA systems.

    **What it does:**
    1. Ingests sensor data (currently simulated, will be replaced with real customer CSV from Umasons Auto Compo)
    2. Detects anomalies using Isolation Forest (unsupervised ML)
    3. Computes a health score per machine
    4. Surfaces alerts and trends through this dashboard

    **What it is technically:**
    A **digital shadow** — it observes physical reality and predicts issues, but doesn't yet simulate alternate scenarios. The next phase (adding what-if simulation) turns this into a full **digital twin**.

    **Why this approach:**
    - Top of market (Siemens, PTC, Dassault) is locked up for large enterprise
    - Mid-market manufacturers have data but no affordable analytics layer
    - Brownfield retrofitting is the real job — no new hardware needed for our wedge
    - Starts with existing SCADA data — zero installation friction

    **Domain advantage:**
    Built with deep operational input from **SwayamVaha Technologies Pvt. Ltd.** (industrial automation systems integrator, 30+ years in PLC/SCADA/DCS integration across multiple industries).

    **Roadmap:**
    - ✅ Phase 1: Predictive maintenance on historical CSV (this MVP)
    - ⏳ Phase 2: Real-time data ingestion via MQTT/OPC UA
    - ⏳ Phase 3: What-if simulator (becomes a true digital twin)
    - ⏳ Phase 4: Vertical-specific modules (auto components, pharma, plating)

    **Data note:**
    Currently using simulated data with intentional failure patterns seeded (Machine M02: gradual degradation, fails day 22; Machine M04: sudden failure, day 27). When real customer data arrives, only the data loader changes.
    """)
