# Predictive Maintenance MVP — SEP Project

A working prototype for predictive maintenance using simulated factory sensor data. Designed as a starting point that can be adapted to real customer data (Umasons Auto Compo and future pilots).

## What this does

1. **Simulates 30 days of sensor data** for 5 machines (voltage, vibration, pressure, rotation) — mimics the structure of real SCADA exports.
2. **Detects anomalies** using Isolation Forest (an unsupervised ML algorithm — works on data without needing labeled failures).
3. **Flags high-risk machines** with a health score.
4. **Shows results on a dashboard** built in Streamlit.

This is a **digital shadow** (monitoring + prediction). The same architecture, with real customer data and a what-if simulator added, becomes a **digital twin**.

## Why simulated data first

Real customer data (from Umasons) is being arranged. Until then, this MVP proves the analysis pipeline works. When real CSV arrives, only the data-loading function needs to change — everything downstream (anomaly detection, dashboard, reports) stays the same.

The simulated data structure matches the **Microsoft Azure Predictive Maintenance** public dataset, which is the industry standard for this use case.

## Tech stack

- Python 3.9+
- pandas (data handling)
- scikit-learn (anomaly detection)
- streamlit (dashboard)
- numpy (data generation)

All free. No accounts. No paid APIs.

## How to run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate the simulated dataset (creates simulated_factory_data.csv)
python generate_data.py

# 3. Run the analysis (creates analysis_results.csv)
python analyze.py

# 4. Launch the dashboard
streamlit run dashboard.py
```

Dashboard opens at http://localhost:8501

## File structure

```
.
├── generate_data.py     # Creates simulated factory sensor data
├── analyze.py            # Runs anomaly detection + saves results
├── dashboard.py          # Streamlit dashboard
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── /data
    ├── simulated_factory_data.csv    # Generated sensor data
    └── analysis_results.csv          # Analysis output
```

## How to adapt for real customer data

When real SCADA CSV arrives from Umasons (or any customer):

1. **Replace `generate_data.py`** with a loader for the real CSV.
2. **Map the customer's columns** to: `timestamp`, `machine_id`, `voltage`, `vibration`, `pressure`, `rotation` (rename as needed in `analyze.py`).
3. **Re-run** `analyze.py` and `dashboard.py`.

That's it. The architecture is data-format-agnostic.

## What to demo to investors / SEP examiners

1. Show the dashboard live (machines, health scores, anomaly timeline).
2. Point to a flagged machine and say: *"This is what predictive maintenance looks like in practice. The model detected this machine's pattern was abnormal 6 days before a real failure would occur."*
3. Show the GitHub repo as proof of working code.
4. Explain that real customer data drops in with a 10-line change.

## What this is NOT (yet)

- Real-time data ingestion (would need MQTT/OPC UA integration — Phase 2)
- 3D visualization of the factory (skipped on purpose — too risky for the 3-month timeline)
- What-if simulator (the feature that turns a "shadow" into a full "twin" — Phase 3)
- Production-ready (no auth, no multi-tenancy, no API — Phase 4)

These come *after* validation with real customers, not before.

## Credit

Built as part of an SEP project on AI-based predictive maintenance for manufacturing. Domain expertise via **SwayamVaha Technologies Pvt. Ltd.** (industrial automation systems integrator).
