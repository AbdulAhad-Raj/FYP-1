
import pandas as pd
import matplotlib.pyplot as plt
import os

# -----------------------------------------
# SENTINEL-X MODULE 2.3
# KALMAN FILTER IMPLEMENTATION
# -----------------------------------------

INPUT_FILE = "sentinel_x_cleaned.csv"
OUTPUT_FILE = "sentinel_x_kalman_filtered.csv"

# Initial Kalman Filter parameters
PROCESS_NOISE = 0.1
MEASUREMENT_NOISE = 4.0
INITIAL_UNCERTAINTY = 1.0

print("=" * 50)
print("       SENTINEL-X KALMAN FILTER")
print("=" * 50)

# 1. Check input file
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        "Cleaned RSSI CSV file not found."
    )

# 2. Load cleaned data
data = pd.read_csv(INPUT_FILE)

required_columns = ["Tag_ID", "Timestamp", "RSSI_dBm"]

for column in required_columns:
    if column not in data.columns:
        raise ValueError(
            f"Required column missing: {column}"
        )

# 3. Convert and validate data
data["RSSI_dBm"] = pd.to_numeric(
    data["RSSI_dBm"], errors="coerce"
)

data["Timestamp"] = pd.to_datetime(
    data["Timestamp"], errors="coerce"
)

data = data.dropna(
    subset=["Tag_ID", "Timestamp", "RSSI_dBm"]
)

data = data.sort_values(
    by=["Tag_ID", "Timestamp"]
).copy()

# 4. Define the one-dimensional Kalman Filter
def kalman_filter(
    measurements,
    process_noise=PROCESS_NOISE,
    measurement_noise=MEASUREMENT_NOISE,
    initial_uncertainty=INITIAL_UNCERTAINTY
):
    estimates = []

    # Initialize using the first measurement
    estimate = float(measurements.iloc[0])
    uncertainty = initial_uncertainty

    for measurement in measurements:

        measurement = float(measurement)

        # Prediction step
        predicted_estimate = estimate
        predicted_uncertainty = uncertainty + process_noise

        # Kalman Gain
        kalman_gain = (
            predicted_uncertainty /
            (predicted_uncertainty + measurement_noise)
        )

        # Update estimate
        estimate = (
            predicted_estimate +
            kalman_gain * (measurement - predicted_estimate)
        )

        # Update uncertainty
        uncertainty = (
            (1 - kalman_gain) * predicted_uncertainty
        )

        estimates.append(estimate)

    return estimates

# 5. Apply filter separately to each tag
data["RSSI_Kalman"] = (
    data.groupby("Tag_ID")["RSSI_dBm"]
    .transform(
        lambda readings: kalman_filter(readings)
    )
)

# 6. Save the filtered dataset
data.to_csv(OUTPUT_FILE, index=False)

print("\nKalman filtering completed successfully!")
print("Total processed records:", len(data))
print("Output file:", OUTPUT_FILE)

print("\nRecords processed per tag:")
print(data["Tag_ID"].value_counts().sort_index())

print("\nSample comparison:")
print(
    data[
        ["Tag_ID", "RSSI_dBm", "RSSI_Filtered", "RSSI_Kalman"]
    ].head(10).to_string(index=False)
)

# 7. Generate comparison graphs
for tag in ["TAG-01", "TAG-02", "TAG-03", "TAG-04"]:

    tag_data = data[data["Tag_ID"] == tag].copy()

    if tag_data.empty:
        print(f"No measurements found for {tag}")
        continue

    plt.figure(figsize=(12, 5))

    plt.plot(
        tag_data["Timestamp"],
        tag_data["RSSI_dBm"],
        label="Raw RSSI",
        alpha=0.4
    )

    plt.plot(
        tag_data["Timestamp"],
        tag_data["RSSI_Filtered"],
        label="Moving Average",
        linewidth=2
    )

    plt.plot(
        tag_data["Timestamp"],
        tag_data["RSSI_Kalman"],
        label="Kalman Filter",
        linewidth=2
    )

    plt.title(f"Sentinel-X RSSI Filtering - {tag}")
    plt.xlabel("Time")
    plt.ylabel("RSSI (dBm)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=30)
    plt.tight_layout()

    graph_file = f"{tag}_kalman_comparison.png"
    plt.savefig(graph_file, dpi=300)
    plt.show()

    print("Graph saved:", graph_file)

print("\nAll Kalman Filter operations completed.")
