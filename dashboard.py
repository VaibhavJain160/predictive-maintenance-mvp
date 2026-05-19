"""
dashboard.py
-------------
Live-feel predictive maintenance dashboard.
Talks to the user in plain English. Auto-refreshes. Looks like a real ops tool.

Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import random

# -- Page config --
st.set_page_config(
    page_title="Factory Pulse | Predictive Maintenance",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "data/analysis_results.csv"

# -- Custom CSS for a more polished look --
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f3a5f;
    }
    .greeting-card {
        background: linear-gradient(135deg, #1f3a5f 0%, #2c5282 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .alert-card {
        background-color: #fff5f5;
        border-left: 5px solid #e53e3e;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .success-card {
        background-color: #f0fff4;
        border-left: 5px solid #38a169;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .insight-box {
        background-color: #f4f1ea;
        border-left: 4px solid #c9a961;
        padding: 12px 18px;
        border-radius: 6px;
        margin: 8px 0;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# -- Load data --
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ Data not found. Run `python3 generate_data.py` then `python3 analyze.py` first.")
    st.stop()

# -- Sidebar: user identity + controls --
with st.sidebar:
    st.markdown("### 👷 Operator Console")
    user_name = st.text_input("Your name", value="Site Engineer")
    st.markdown("---")
    st.markdown("### ⚙️ Controls")
    auto_refresh = st.toggle("Live mode (auto-refresh)", value=False, help="Refreshes every 5 seconds to simulate live data feed")
    show_technical = st.toggle("Show technical details", value=True)
    st.markdown("---")
    st.markdown("### 📊 Data Range")
    st.caption(f"**Period:** {df['timestamp'].min().strftime('%b %d')} → {df['timestamp'].max().strftime('%b %d, %Y')}")
    st.caption(f"**Total readings:** {len(df):,}")
    st.caption(f"**Machines:** {df['machine_id'].nunique()}")
    st.markdown("---")
    st.caption("🔌 Connected to: SCADA Export v1.0")
    st.caption("🛡️ Powered by SwayamVaha Tech")

# -- Header greeting --
current_hour = datetime.now().hour
if current_hour < 12:
    greeting = "Good morning"
elif current_hour < 17:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

# Compute fleet summary
summary = df.groupby("machine_id").agg(
    avg_health=("health_score", "mean"),
    critical_count=("status", lambda x: (x == "CRITICAL").sum()),
).reset_index()
summary["overall_status"] = summary["critical_count"].apply(
    lambda x: "CRITICAL" if x > 40 else ("WARNING" if x > 15 else "HEALTHY")
)

n_critical = (summary["overall_status"] == "CRITICAL").sum()
n_healthy = (summary["overall_status"] == "HEALTHY").sum()
total = len(summary)

# Personalized greeting card
if n_critical > 0:
    headline = f"⚠️ {n_critical} machine{'s' if n_critical > 1 else ''} need{'s' if n_critical == 1 else ''} your attention today."
    subtext = f"The rest of your fleet ({n_healthy} machine{'s' if n_healthy != 1 else ''}) is running smoothly."
else:
    headline = "✅ All machines healthy today."
    subtext = "Your fleet is running smoothly. No urgent action needed."

st.markdown(f"""
<div class="greeting-card">
    <h2 style="margin:0; color:white;">{greeting}, {user_name} 👋</h2>
    <p style="font-size: 18px; margin: 10px 0 5px 0; color: white;">{headline}</p>
    <p style="font-size: 14px; opacity: 0.85; margin: 0; color: white;">{subtext}</p>
</div>
""", unsafe_allow_html=True)

# -- Top-level KPIs --
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🏭 Machines monitored", total)
with col2:
    st.metric("✅ Healthy", n_healthy, delta=f"{n_healthy/total*100:.0f}% of fleet")
with col3:
    st.metric("⚠️ Need attention", n_critical, delta=f"{n_critical} critical" if n_critical > 0 else "none", delta_color="inverse")
with col4:
    avg_fleet_health = summary["avg_health"].mean()
    st.metric("💚 Avg fleet health", f"{avg_fleet_health:.0f}/100")

st.markdown("---")

# -- Tabs --
tab1, tab2, tab3, tab4 = st.tabs(["🎯 What needs my attention?", "🔧 Machine deep-dive", "📜 Activity log", "💡 About this tool"])

# ============================================================
# TAB 1: WHAT NEEDS ATTENTION
# ============================================================
with tab1:
    st.subheader(f"Priority actions for you, {user_name}")

    critical_machines = summary[summary["overall_status"] == "CRITICAL"].sort_values("critical_count", ascending=False)
    warning_machines = summary[summary["overall_status"] == "WARNING"]
    healthy_machines = summary[summary["overall_status"] == "HEALTHY"]

    if len(critical_machines) == 0:
        st.markdown("""
        <div class="success-card">
            <h4 style="margin:0;">🎉 Nothing urgent today!</h4>
            <p style="margin: 5px 0 0 0;">Your entire fleet is operating within normal parameters. Great job keeping things running smoothly.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"I've flagged **{len(critical_machines)} machine(s)** that show patterns I haven't seen during their normal operation. Here's what I think you should do:")

        for idx, row in critical_machines.iterrows():
            machine_id = row["machine_id"]
            n_anomalies = int(row["critical_count"])
            avg_health = row["avg_health"]

            # Find when the anomalies started
            machine_df = df[df["machine_id"] == machine_id].sort_values("timestamp")
            anomalies = machine_df[machine_df["status"] == "CRITICAL"]
            if len(anomalies) > 0:
                first_anomaly = anomalies["timestamp"].min()
                last_anomaly = anomalies["timestamp"].max()
                days_active = (last_anomaly - first_anomaly).days

                # Identify which sensor is most abnormal
                normal_df = machine_df[machine_df["status"] == "HEALTHY"]
                sensor_deviations = {}
                for sensor in ["voltage", "vibration", "pressure", "rotation"]:
                    if len(normal_df) > 0:
                        normal_mean = normal_df[sensor].mean()
                        anomaly_mean = anomalies[sensor].mean()
                        deviation = abs(anomaly_mean - normal_mean) / (normal_mean + 0.001) * 100
                        sensor_deviations[sensor] = deviation

                top_sensor = max(sensor_deviations, key=sensor_deviations.get) if sensor_deviations else "vibration"

                st.markdown(f"""
                <div class="alert-card">
                    <h4 style="margin:0; color: #c53030;">🔴 Machine {machine_id} — Requires inspection</h4>
                    <p style="margin: 8px 0;"><b>What I'm seeing:</b> {n_anomalies} abnormal readings over the last {days_active} days. The <b>{top_sensor}</b> is showing the most unusual pattern compared to its normal range.</p>
                    <p style="margin: 8px 0;"><b>First warning sign:</b> {first_anomaly.strftime('%B %d at %H:%M')}</p>
                    <p style="margin: 8px 0;"><b>My recommendation:</b> Schedule a maintenance check within the next 48 hours. Inspect the {top_sensor} sensor and the related mechanical components.</p>
                    <p style="margin: 8px 0;"><b>Why this matters:</b> Machines showing this pattern typically experience a hard failure within 5-10 days if left unaddressed. Acting now likely saves you days of unplanned downtime.</p>
                </div>
                """, unsafe_allow_html=True)

    # Show healthy machines briefly
    if len(healthy_machines) > 0:
        with st.expander(f"✅ {len(healthy_machines)} healthy machine(s) — running normally"):
            for _, row in healthy_machines.iterrows():
                st.markdown(f"**{row['machine_id']}** — health score {row['avg_health']:.0f}/100. No issues detected.")

# ============================================================
# TAB 2: MACHINE DEEP-DIVE
# ============================================================
with tab2:
    selected = st.selectbox("Pick a machine to investigate", sorted(df["machine_id"].unique()))
    machine_df = df[df["machine_id"] == selected].sort_values("timestamp")

    # Status interpretation
    n_crit = (machine_df["status"] == "CRITICAL").sum()
    avg_health = machine_df["health_score"].mean()

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if n_crit > 40:
            st.markdown(f"""
            <div class="alert-card">
                <h3 style="margin:0;">🔴 {selected} — Action required</h3>
                <p style="margin: 8px 0 0 0;">This machine is showing concerning patterns. I'd recommend inspection within 48 hours.</p>
            </div>
            """, unsafe_allow_html=True)
        elif n_crit > 15:
            st.markdown(f"""
            <div style="background-color: #fffaf0; border-left: 5px solid #d69e2e; padding: 15px; border-radius: 8px;">
                <h3 style="margin:0;">🟡 {selected} — Keep an eye on this</h3>
                <p style="margin: 8px 0 0 0;">Some minor anomalies. Worth a routine check during your next maintenance window.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="success-card">
                <h3 style="margin:0;">🟢 {selected} — Running smoothly</h3>
                <p style="margin: 8px 0 0 0;">This machine is operating well within normal parameters.</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.metric("Health score", f"{avg_health:.0f}/100")
    with col3:
        st.metric("Anomalies", n_crit)

    st.markdown("### 📈 What the sensors are telling me")

    # Sensor stories
    sensor_info = {
        "voltage": ("⚡ Voltage", "Motor electrical supply — spikes can mean electrical faults", "V"),
        "vibration": ("📳 Vibration", "Mechanical health — rising vibration often means bearings or alignment issues", "mm/s"),
        "pressure": ("🔵 Pressure", "Process pressure — drops can mean leaks, spikes mean blockages", "bar"),
        "rotation": ("🔄 Rotation", "RPM — drops indicate load issues or motor wear", "RPM"),
    }

    for sensor, (title, story, unit) in sensor_info.items():
        with st.container(border=True):
            st.markdown(f"#### {title}  *<small style='color:#6b7280;'>{story}</small>*", unsafe_allow_html=True)

            # Compute trend insight
            recent = machine_df.tail(72)  # last 3 days of hourly readings
            earlier = machine_df.head(72)  # first 3 days
            recent_avg = recent[sensor].mean()
            earlier_avg = earlier[sensor].mean()
            change_pct = ((recent_avg - earlier_avg) / earlier_avg) * 100 if earlier_avg != 0 else 0

            col_a, col_b = st.columns([3, 1])
            with col_a:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=machine_df["timestamp"], y=machine_df[sensor],
                    mode="lines", name=sensor,
                    line=dict(color="#1f3a5f", width=1.5),
                ))
                # Highlight anomalies
                anomalies = machine_df[machine_df["status"] == "CRITICAL"]
                if len(anomalies) > 0:
                    fig.add_trace(go.Scatter(
                        x=anomalies["timestamp"], y=anomalies[sensor],
                        mode="markers", name="Anomaly",
                        marker=dict(color="#e53e3e", size=7, symbol="x", line=dict(width=1)),
                    ))
                fig.update_layout(
                    height=220, margin=dict(l=20, r=20, t=10, b=20),
                    yaxis_title=unit, xaxis_title="",
                    showlegend=False, plot_bgcolor="white",
                )
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                st.metric(f"Current avg", f"{recent_avg:.1f} {unit}", delta=f"{change_pct:+.1f}% vs start")
                if abs(change_pct) > 10:
                    st.caption(f"⚠️ Notable change")
                else:
                    st.caption("✓ Stable")

            # Plain English insight
            if abs(change_pct) > 10:
                direction = "increased" if change_pct > 0 else "decreased"
                st.markdown(f"""
                <div class="insight-box">
                💡 The {sensor} has {direction} by {abs(change_pct):.1f}% compared to the start of the period.
                This kind of drift is worth investigating — it can indicate gradual wear or process changes.
                </div>
                """, unsafe_allow_html=True)

    if show_technical:
        st.markdown("### 🔬 Technical details")
        st.dataframe(
            machine_df.tail(20)[["timestamp", "voltage", "vibration", "pressure", "rotation", "health_score", "status"]],
            use_container_width=True, hide_index=True,
        )

# ============================================================
# TAB 3: ACTIVITY LOG
# ============================================================
with tab3:
    st.subheader("Recent activity across all machines")

    all_alerts = df[df["status"] == "CRITICAL"].sort_values("timestamp", ascending=False)

    if len(all_alerts) == 0:
        st.success("No alerts in the period. Quiet shift! ☕")
    else:
        st.markdown(f"Showing **{len(all_alerts)} alerts** from the last 30 days, newest first.")

        # Show as a conversational feed
        for _, row in all_alerts.head(20).iterrows():
            time_ago = (df["timestamp"].max() - row["timestamp"])
            days_ago = time_ago.days
            hours_ago = int(time_ago.total_seconds() / 3600)

            if days_ago > 0:
                when = f"{days_ago} day{'s' if days_ago > 1 else ''} ago"
            else:
                when = f"{hours_ago} hour{'s' if hours_ago != 1 else ''} ago"

            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**🔴 Anomaly detected on {row['machine_id']}**")
                    st.caption(f"📅 {row['timestamp'].strftime('%B %d at %H:%M')} ({when})")
                    st.caption(f"Readings: V={row['voltage']:.1f}, Vib={row['vibration']:.1f}, P={row['pressure']:.1f}, RPM={row['rotation']:.0f}")
                with col2:
                    st.metric("Health", f"{row['health_score']:.0f}/100")

        if len(all_alerts) > 20:
            st.info(f"Showing 20 most recent. {len(all_alerts) - 20} earlier alerts not shown.")

# ============================================================
# TAB 4: ABOUT
# ============================================================
with tab4:
    st.subheader("What is this tool?")
    st.markdown("""
    This is a **predictive maintenance dashboard** that watches your factory's sensor data and tells you,
    in plain English, which machines need attention and why.

    **How it works:**
    1. Your SCADA system already collects voltage, vibration, pressure, and rotation data on every machine
    2. This tool reads that data and uses AI (Isolation Forest) to learn what "normal" looks like for your fleet
    3. When a machine deviates from normal, you get a clear alert with a recommended action

    **What makes this different:**
    - **No new hardware needed** — uses your existing SCADA exports
    - **Talks to you like a colleague**, not a software manual
    - **Tells you what to do**, not just what's broken
    - **Built for your fleet** — learns YOUR machines' normal patterns

    **Built by:** SEP Project, in collaboration with **SwayamVaha Technologies Pvt. Ltd.** — 30+ years in industrial automation.
    """)

    st.markdown("### 🛣️ Roadmap")
    st.markdown("""
    - ✅ **Phase 1 (current):** Historical CSV analysis + dashboard
    - ⏳ **Phase 2:** Live data ingestion (MQTT / OPC UA)
    - ⏳ **Phase 3:** "What-if" simulation — try changes virtually before doing them on the line
    - ⏳ **Phase 4:** Industry-specific modules (auto components, pharma, plating)
    """)

# -- Live mode refresh --
if auto_refresh:
    time.sleep(5)
    st.rerun()

# -- Footer --
st.markdown("---")
st.caption(f"🛡️ Factory Pulse v1.0  •  Last refreshed: {datetime.now().strftime('%H:%M:%S')}  •  Demo data — replace with real SCADA exports")