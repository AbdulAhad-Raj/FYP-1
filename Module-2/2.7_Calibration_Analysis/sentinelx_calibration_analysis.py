
import pandas as pd
import matplotlib.pyplot as plt
import os

# -----------------------------------------
# SENTINEL-X MODULE 2.3
# RSSI CALIBRATION ANALYSIS
# -----------------------------------------

INPUT_FILE = "sentinel_x_calibration.csv"

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        "Calibration dataset not found."
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
]

if data.empty:
    raise ValueError(
        "No valid calibration measurements found."
    )

# Calculate statistics at each distance
summary = (
    data.groupby(["Tag_ID", "Distance_m"])
    ["RSSI_dBm"]
    .agg(
        Reading_Count="count",
        Mean_RSSI="mean",
        Median_RSSI="median",
        Standard_Deviation="std",
        Minimum_RSSI="min",
        Maximum_RSSI="max"
    )
    .reset_index()
)

summary["Standard_Deviation"] = (
    summary["Standard_Deviation"].fillna(0)
)

print("\nSENTINEL-X CALIBRATION RESULTS")
print("=" * 55)

print(summary.to_string(index=False))

# Save the statistics
summary.to_csv(
    "sentinel_x_calibration_summary.csv",
    index=False
)

# Generate a graph for each tag
for tag in summary["Tag_ID"].unique():

    tag_data = summary[
        summary["Tag_ID"] == tag
    ].sort_values("Distance_m")

    plt.figure(figsize=(10, 5))

    plt.errorbar(
        tag_data["Distance_m"],
        tag_data["Mean_RSSI"],
        yerr=tag_data["Standard_Deviation"],
        marker="o",
        capsize=5,
        label="Mean RSSI ± Standard Deviation"
    )

    plt.title(
        f"Sentinel-X RSSI Calibration - {tag}"
    )

    plt.xlabel("Distance (metres)")
    plt.ylabel("RSSI (dBm)")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    filename = f"{tag}_calibration_graph.png"

    plt.savefig(filename, dpi=300)
    plt.show()

    print("Graph saved:", filename)

print("\nCalibration analysis completed.")
