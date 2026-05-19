"""
generate_data.py
-----------------
Generates 30 days of simulated factory sensor data for 5 machines.

Why simulated:
- Real customer data (Umasons) is being arranged.
- This data mimics the structure of the Microsoft Azure Predictive Maintenance
  public dataset, which is the industry standard for this use case.
- When real CSV arrives, this file is replaced with a real-data loader.

Output: data/simulated_factory_data.csv

Schema (matches typical SCADA exports):
- timestamp: datetime, every hour for 30 days
- machine_id: 5 machines (M01-M05)
- voltage: motor voltage (V) — normal range 150-200
- vibration: vibration (mm/s) — normal range 30-50
- pressure: pressure (bar) — normal range 90-110
- rotation: RPM — normal range 400-500

Intentional failures seeded:
- Machine M02 fails on day 22 (gradual degradation visible from day 18)
- Machine M04 fails on day 27 (sudden spike on day 26)
- Other machines run healthy throughout
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Reproducibility — same data every run
np.random.seed(42)

# Config
NUM_MACHINES = 5
NUM_DAYS = 30
READINGS_PER_DAY = 24  # hourly readings
START_DATE = datetime(2026, 4, 1, 0, 0, 0)
OUTPUT_FILE = "data/simulated_factory_data.csv"

# Normal operating ranges (mean, std) for each sensor
NORMAL_RANGES = {
    "voltage":   (170.0, 5.0),
    "vibration": (40.0, 3.0),
    "pressure":  (100.0, 2.0),
    "rotation":  (450.0, 8.0),
}


def generate_machine_data(machine_id, failure_day=None, failure_type="gradual"):
    """
    Generate 30 days of hourly sensor data for one machine.

    failure_day: int or None — day on which the machine fails (1-30)
    failure_type: 'gradual' or 'sudden'
        - gradual: degradation starts 4 days before failure
        - sudden: spike 1 day before failure
    """
    rows = []
    total_readings = NUM_DAYS * READINGS_PER_DAY

    for hour_idx in range(total_readings):
        ts = START_DATE + timedelta(hours=hour_idx)
        current_day = (ts - START_DATE).days + 1  # 1-30

        # Baseline normal readings
        v = np.random.normal(*NORMAL_RANGES["voltage"])
        vib = np.random.normal(*NORMAL_RANGES["vibration"])
        p = np.random.normal(*NORMAL_RANGES["pressure"])
        r = np.random.normal(*NORMAL_RANGES["rotation"])

        # Inject failure pattern if applicable
        if failure_day is not None:
            days_to_failure = failure_day - current_day

            if failure_type == "gradual" and 0 <= days_to_failure <= 4:
                # Gradual degradation: vibration rises, rotation drops, voltage fluctuates
                severity = (5 - days_to_failure) / 5.0  # 0.0 -> 1.0
                vib += severity * 25  # vibration creeps up
                r -= severity * 60    # rotation drops
                v += np.random.normal(0, severity * 15)  # voltage gets jittery

            elif failure_type == "sudden" and days_to_failure <= 1:
                # Sudden spike just before failure
                if days_to_failure == 1:
                    vib += np.random.uniform(20, 40)
                    p += np.random.uniform(10, 20)
                elif days_to_failure == 0:
                    # Hard failure event
                    vib += np.random.uniform(40, 60)
                    p -= np.random.uniform(15, 25)
                    r -= np.random.uniform(100, 200)

        rows.append({
            "timestamp": ts,
            "machine_id": machine_id,
            "voltage": round(v, 2),
            "vibration": round(vib, 2),
            "pressure": round(p, 2),
            "rotation": round(r, 2),
        })

    return rows


def main():
    print(f"Generating {NUM_DAYS} days of hourly data for {NUM_MACHINES} machines...")

    all_rows = []

    # Machine config — which machines fail, when, and how
    machine_config = {
        "M01": {"failure_day": None, "failure_type": None},        # healthy
        "M02": {"failure_day": 22,  "failure_type": "gradual"},    # gradual degradation
        "M03": {"failure_day": None, "failure_type": None},        # healthy
        "M04": {"failure_day": 27,  "failure_type": "sudden"},     # sudden failure
        "M05": {"failure_day": None, "failure_type": None},        # healthy
    }

    for machine_id, cfg in machine_config.items():
        all_rows.extend(
            generate_machine_data(
                machine_id,
                failure_day=cfg["failure_day"],
                failure_type=cfg["failure_type"],
            )
        )

    df = pd.DataFrame(all_rows)
    df = df.sort_values(["timestamp", "machine_id"]).reset_index(drop=True)

    # Save
    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    # Print summary
    print(f"\n✓ Saved {len(df):,} rows to {OUTPUT_FILE}")
    print(f"\nMachine summary:")
    for mid, cfg in machine_config.items():
        status = "HEALTHY" if cfg["failure_day"] is None else f"FAILS day {cfg['failure_day']} ({cfg['failure_type']})"
        print(f"  {mid}: {status}")
    print(f"\nDate range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nSample rows:")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()
