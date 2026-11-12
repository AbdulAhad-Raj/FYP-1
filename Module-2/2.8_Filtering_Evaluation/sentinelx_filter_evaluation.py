
import pandas as pd
import numpy as np
import os

# -----------------------------------------
# SENTINEL-X MODULE 2.3
# FILTER PERFORMANCE EVALUATION
# -----------------------------------------

INPUT_FILE = "sentinel_x_calibration.csv"

PROCESS_NOISE = 0.1
MEASUREMENT_NOISE = 4.0
INITIAL_UNCERTAINTY = 1.0

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        "Calibration CSV file not found."
    )

data = pd.read_csv(INPUT_FILE)

required_columns = [
    "Distance_m",
    "Tag_ID",
    "RSSI_dBm"
]

for column in required_columns:
    if column not in data.columns:
        raise ValueError(
            f"Missing column: {column}"
        )

data["Distance_m"] = pd.to_numeric(
    data["Distance_m"], errors="coerce"
)

data["RSSI_dBm"] = pd.to_numeric(
    data["RSSI_dBm"], errors="coerce"
)

data = data.dropna(
    subset=required_columns
)

data = data[
    (data["Distance_m"] > 0) &
    (data["RSSI_dBm"] >= -100) &
    (data["RSSI_dBm"] <= 0)
].copy()

if data.empty:
    raise ValueError("No valid calibration readings.")

# Keep measurement order within each distance.
# This assumes rows were recorded in collection order.

def kalman_filter(values):
    measurements = values.tolist()

    estimate = float(measurements[0])
    uncertainty = INITIAL_UNCERTAINTY

    estimates = []

    for measurement in measurements:

        predicted_estimate = estimate

        predicted_uncertainty = (
            uncertainty + PROCESS_NOISE
        )

        gain = (
            predicted_uncertainty /
            (predicted_uncertainty + MEASUREMENT_NOISE)
        )

        estimate = (
            predicted_estimate +
            gain * (measurement - predicted_estimate)
        )

        uncertainty = (
            (1 - gain) * predicted_uncertainty
        )

        estimates.append(estimate)

    return estimates


# Evaluate each tag at each distance independently.
results = []

group_columns = ["Tag_ID", "Distance_m"]

for (tag, distance), group in data.groupby(
    group_columns, sort=True
):

    group = group.copy()

    raw = group["RSSI_dBm"]

    # Five-reading moving average
    moving_average = raw.rolling(
        window=5,
        min_periods=1
    ).mean()

    # Kalman Filter
    kalman = pd.Series(
        kalman_filter(raw),
        index=group.index
    )

    # Calculate standard deviation
    raw_std = raw.std()
    ma_std = moving_average.std()
    kalman_std = kalman.std()

    # Standard deviation is undefined for one reading.
    # Record zero only as a placeholder in that case.
    raw_std = 0 if pd.isna(raw_std) else raw_std
    ma_std = 0 if pd.isna(ma_std) else ma_std
    kalman_std = 0 if pd.isna(kalman_std) else kalman_std

    results.append({
        "Tag_ID": tag,
        "Distance_m": distance,
        "Reading_Count": len(group),
        "Raw_Mean": raw.mean(),
        "Raw_Std": raw_std,
        "Moving_Average_Std": ma_std,
        "Kalman_Std": kalman_std
    })


summary = pd.DataFrame(results)

# Calculate percentage reduction in standard deviation.
summary["MA_Std_Reduction_Percent"] = np.where(
    summary["Raw_Std"] > 0,
    (
        (summary["Raw_Std"] - summary["Moving_Average_Std"])
        / summary["Raw_Std"]
    ) * 100,
    0
)

summary["Kalman_Std_Reduction_Percent"] = np.where(
    summary["Raw_Std"] > 0,
    (
        (summary["Raw_Std"] - summary["Kalman_Std"])
        / summary["Raw_Std"]
    ) * 100,
    0
)

OUTPUT_FILE = "sentinel_x_filter_evaluation.csv"

summary.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSENTINEL-X FILTER EVALUATION")
print("=" * 65)

print(summary.round(2).to_string(index=False))

print("\nResults saved to:", OUTPUT_FILE)

print("\nEvaluation completed successfully.")
