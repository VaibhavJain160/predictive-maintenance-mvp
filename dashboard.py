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
from io import BytesIO

# -- Config --
st.set_page_config(
    page_title="Predictive Maintenance MVP",
    page_icon="⚙️",
    layout="wide",
)

DATA_FILE = "data/analysis_results.csv"
WHY_THIS_MATTERS = "Sustained abnormal behavior increases the risk of unplanned downtime, so early inspection is recommended."
REQUIRED_COLUMNS = [
    "timestamp",
    "machine_id",
    "voltage",
    "vibration",
    "pressure",
    "rotation",
    "health_score",
    "status",
]
NUMERIC_COLUMNS = ["voltage", "vibration", "pressure", "rotation", "health_score"]

# -- Helpers --
@st.cache_data
def load_demo_data():
    df = pd.read_csv(DATA_FILE)
    return prepare_data(df)

@st.cache_data
def load_uploaded_data(file_bytes):
    df = pd.read_csv(BytesIO(file_bytes))
    return prepare_data(df)

def prepare_data(df):
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required column(s): {', '.join(missing_columns)}")

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if df["timestamp"].isna().any():
        raise ValueError("The timestamp column contains values that could not be parsed.")

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        if df[column].isna().any():
            raise ValueError(f"The {column} column contains non-numeric values.")

    return df

def build_fleet_summary(df):
    summary = df.groupby("machine_id").agg(
        avg_health=("health_score", "mean"),
        critical_count=("status", lambda x: (x == "CRITICAL").sum()),
        warning_count=("status", lambda x: (x == "WARNING").sum()),
        total_readings=("status", "count"),
    ).reset_index()

    summary["overall_status"] = summary["critical_count"].apply(
        lambda x: "CRITICAL" if x > 40 else ("WARNING" if x > 15 else "HEALTHY")
    )
    return summary

def first_warning_sign(df, machine_id):
    machine_df = df[df["machine_id"] == machine_id].sort_values("timestamp")
    warning_rows = machine_df[machine_df["status"].isin(["WARNING", "CRITICAL"])]
    if warning_rows.empty:
        return "No warning signs detected."
    first_warning = warning_rows.iloc[0]
    return (
        f"{first_warning['timestamp'].strftime('%Y-%m-%d %H:%M')} "
        f"({first_warning['status']}, health score {first_warning['health_score']:.1f}/100)"
    )

def recommendation_for(status):
    if status == "CRITICAL":
        return "Inspect this machine immediately and plan maintenance before the next production window."
    if status == "WARNING":
        return "Schedule an inspection and monitor the next readings closely."
    return "Continue routine monitoring."

def status_color(status):
    return {
        "HEALTHY": "🟢",
        "WARNING": "🟡",
        "CRITICAL": "🔴",
    }.get(status, "⚪")

# -- Data source --
if "upload_widget_key" not in st.session_state:
    st.session_state.upload_widget_key = 0

st.sidebar.header("Data Source")
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV",
    type=["csv"],
    key=f"csv_upload_{st.session_state.upload_widget_key}",
)
if st.sidebar.button("Reset to Demo CSV"):
    st.session_state.upload_widget_key += 1
    st.rerun()

# -- Load data --
try:
    if uploaded_file is not None:
        df = load_uploaded_data(uploaded_file.getvalue())
        data_source = "Uploaded CSV"
    else:
        df = load_demo_data()
        data_source = "Demo CSV"
except FileNotFoundError:
    st.error("❌ Data file not found. Run `python generate_data.py` then `python analyze.py` first.")
    st.stop()
except (ValueError, pd.errors.EmptyDataError) as exc:
    st.error(f"❌ CSV could not be loaded. {exc}")
    st.stop()

st.sidebar.caption(f"Data source: {data_source}")
summary = build_fleet_summary(df)

st.markdown(
    """
    <style>
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] label p,
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] div {
        color: var(--text-color) !important;
        opacity: 1 !important;
    }

    div[data-testid="stMetric"] label p,
    div[data-testid="stMetric"] label,
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricValue"] {
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -- Header --
st.title("⚙️ Predictive Maintenance Dashboard")
st.markdown("**SEP Project — AI analytics layer for factory SCADA data**")
st.caption(f"Showing {len(df):,} readings across {df['machine_id'].nunique()} machines | Period: {df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}")

# -- Overview tab + per-machine tab --
tab_overview, tab_priorities, tab_machine, tab_alerts, tab_about = st.tabs(["📊 Overview", "Maintenance Priorities", "🔧 Per Machine", "🚨 Alerts", "ℹ️ About"])

# ============================================================
# TAB 1: OVERVIEW
# ============================================================
with tab_overview:
    st.subheader("Fleet Health at a Glance")

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
# TAB 2: MAINTENANCE PRIORITIES
# ============================================================
with tab_priorities:
    st.subheader("Fleet Risk Ranking")

    ranking = summary.sort_values(
        ["critical_count", "avg_health", "warning_count"],
        ascending=[False, True, False],
    ).reset_index(drop=True)
    ranking_display = pd.DataFrame({
        "Rank": range(1, len(ranking) + 1),
        "Machine": ranking["machine_id"],
        "Critical anomalies": ranking["critical_count"].astype(int),
        "Average health score": ranking["avg_health"].map(lambda value: f"{value:.1f}/100"),
        "Status": ranking["overall_status"].map(lambda value: f"{status_color(value)} {value}"),
    })

    st.dataframe(
        ranking_display,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.subheader("Detailed Alerts")

    risky_machines = ranking[ranking["overall_status"].isin(["WARNING", "CRITICAL"])]
    if risky_machines.empty:
        st.success("No machines need immediate attention.")
    else:
        for _, row in risky_machines.iterrows():
            with st.container(border=True):
                st.markdown(f"### {status_color(row['overall_status'])} {row['machine_id']}")
                st.markdown(
                    f"**What I'm seeing:** {int(row['critical_count'])} critical anomalies "
                    f"and {int(row['warning_count'])} warnings, with an average health score "
                    f"of {row['avg_health']:.1f}/100."
                )
                st.markdown(f"**First warning sign:** {first_warning_sign(df, row['machine_id'])}")
                st.markdown(f"**My recommendation:** {recommendation_for(row['overall_status'])}")
                st.markdown(f"**Why this matters:** {WHY_THIS_MATTERS}")

# ============================================================
# TAB 3: PER-MACHINE DEEP DIVE
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
        st.write(f"**Pattern:** {WHY_THIS_MATTERS}")
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
# TAB 4: ALERTS LOG
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
# TAB 5: ABOUT
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
