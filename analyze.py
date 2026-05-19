"""
analyze.py
-----------
Runs anomaly detection on factory sensor data.

Uses Isolation Forest — an unsupervised ML algorithm that:
- Doesn't need labeled failure data (which most factories don't have)
- Identifies data points that are "different" from the norm
- Works well on multi-sensor data
- Is fast and simple

Output:
- data/analysis_results.csv — original data + anomaly score + health score

How to adapt for real customer data:
- Replace load_data() to read the customer's actual CSV.
- Map their columns to the expected schema (timestamp, machine_id, voltage,
  vibration, pressure, rotation) — or update FEATURES list below.
- Everything else stays the same.
"""

import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

INPUT_FILE = "data/simulated_factory_data.csv"
OUTPUT_FILE = "data/analysis_results.csv"

# Sensor columns to analyze
FEATURES = ["voltage", "vibration", "pressure", "rotation"]

# Isolation Forest parameters
# contamination = expected % of anomalies (5% is a reasonable default for industrial data)
CONTAMINATION = 0.05


def load_data(path):
    """Load and prepare data."""
    df = pd.read_csv(path, parse_dates=["timestamp"])
    print(f"✓ Loaded {len(df):,} rows from {path}")
    return df


def detect_anomalies(df):
    """
    Run Isolation Forest on the entire fleet using a GLOBAL model.

    Why global model:
    - We learn what "normal" looks like across the whole fleet.
    - Machines that genuinely deviate from fleet-wide normal stand out.
    - Healthy machines will have ~0 critical anomalies; failing machines will spike.

    This is the right approach when machines are similar (same type/role).
    For mixed fleets, you'd train one model per machine TYPE, not per machine.
    """
    df = df.copy().reset_index(drop=True)

    # Scale features (Isolation Forest works better on scaled data)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[FEATURES])

    # Train Isolation Forest on the whole fleet
    # contamination=0.05 means "expect ~5% of all readings to be anomalies"
    # The model will assign these to the genuinely abnormal points
    model = IsolationForest(
        contamination=CONTAMINATION,
        random_state=42,
        n_estimators=100,
    )
    model.fit(X_scaled)

    # Predictions
    df["anomaly_label"] = model.predict(X_scaled)         # -1 = anomaly, 1 = normal
    df["anomaly_score"] = model.decision_function(X_scaled)  # higher = more normal

    # Convert to a health score (0-100) — higher is healthier
    # Use the GLOBAL range so scores are comparable across machines
    min_score, max_score = df["anomaly_score"].min(), df["anomaly_score"].max()
    if max_score != min_score:
        df["health_score"] = (
            (df["anomaly_score"] - min_score) / (max_score - min_score) * 100
        ).round(1)
    else:
        df["health_score"] = 100.0

    # Categorize
    def categorize(row):
        if row["anomaly_label"] == -1:
            return "CRITICAL"
        elif row["health_score"] < 50:
            return "WARNING"
        else:
            return "HEALTHY"

    df["status"] = df.apply(categorize, axis=1)

    # Print per-machine summary
    for machine_id, machine_df in df.groupby("machine_id"):
        n_anomalies = (machine_df["status"] == "CRITICAL").sum()
        n_warnings = (machine_df["status"] == "WARNING").sum()
        print(f"  {machine_id}: {n_anomalies} critical anomalies, {n_warnings} warnings")

    return df


def summarize_findings(df):
    """Print a human-readable summary."""
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)

    for machine_id, machine_df in df.groupby("machine_id"):
        n_total = len(machine_df)
        n_critical = (machine_df["status"] == "CRITICAL").sum()
        n_warning = (machine_df["status"] == "WARNING").sum()

        # When did anomalies start appearing?
        anomalies = machine_df[machine_df["status"] == "CRITICAL"]
        first_anomaly = anomalies["timestamp"].min() if len(anomalies) > 0 else None

        verdict = "✓ HEALTHY"
        if n_critical > 40:
            verdict = "⚠ HIGH RISK — investigate immediately"
        elif n_critical > 15:
            verdict = "⚠ MODERATE RISK — schedule inspection"

        print(f"\n{machine_id}: {verdict}")
        print(f"  Total readings: {n_total}")
        print(f"  Critical anomalies: {n_critical} ({n_critical/n_total*100:.1f}%)")
        print(f"  Warnings: {n_warning} ({n_warning/n_total*100:.1f}%)")
        if first_anomaly is not None:
            print(f"  First anomaly detected: {first_anomaly}")


def main():
    df = load_data(INPUT_FILE)

    print(f"\nRunning anomaly detection (Isolation Forest, contamination={CONTAMINATION})...")
    results = detect_anomalies(df)

    os.makedirs("data", exist_ok=True)
    results.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✓ Saved analysis to {OUTPUT_FILE}")

    summarize_findings(results)

    print("\n" + "="*60)
    print("NEXT STEP: Run the dashboard")
    print("="*60)
    print("Command: streamlit run dashboard.py")


if __name__ == "__main__":
    main()
