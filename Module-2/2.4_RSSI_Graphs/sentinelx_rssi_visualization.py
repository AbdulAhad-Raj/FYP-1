
import pandas as pd
import matplotlib.pyplot as plt
import os

# -----------------------------------------
# SENTINEL-X MODULE 2.3
# RSSI SIGNAL VISUALIZATION
# -----------------------------------------

INPUT_FILE = "sentinel_x_cleaned.csv"

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        "Cleaned CSV file not found. Run preprocessing first."
    )

data = pd.read_csv(INPUT_FILE)

data["Timestamp"] = pd.to_datetime(data["Timestamp"])

tags = ["TAG-01", "TAG-02", "TAG-03", "TAG-04"]

for tag in tags:

    tag_data = data[data["Tag_ID"] == tag].copy()

    if tag_data.empty:
        print(f"No measurements available for {tag}")
        continue

    tag_data = tag_data.sort_values("Timestamp")

    plt.figure(figsize=(12, 5))

    plt.plot(
        tag_data["Timestamp"],
        tag_data["RSSI_dBm"],
        label="Raw RSSI",
        alpha=0.6
    )

    plt.plot(
        tag_data["Timestamp"],
        tag_data["RSSI_Filtered"],
        label="Filtered RSSI (Moving Average)",
        linewidth=2
    )

    plt.title(f"Sentinel-X RSSI Analysis - {tag}")
    plt.xlabel("Time")
    plt.ylabel("RSSI (dBm)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=30)
    plt.tight_layout()

    output_file = f"{tag}_rssi_comparison.png"

    plt.savefig(output_file, dpi=300)
    plt.show()

    print(f"Graph saved: {output_file}")

print("\nRSSI visualization completed.")
